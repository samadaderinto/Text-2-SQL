import atexit
import json
import logging
import os
from datetime import timedelta
from functools import lru_cache

from django.core.files.storage import default_storage
from django.db import connection, transaction
from django.utils import timezone
from kafka import KafkaProducer

from .models import Customer, Order, Product, QueueJob, User
from .notifications import send_email_notification, send_user_notification
from .search_index import delete_instance, index_instance
from .services import SearchService


logger = logging.getLogger(__name__)
MAX_JOB_ATTEMPTS = 3
STALE_JOB_MINUTES = 15


@lru_cache(maxsize=1)
def get_job_producer():
    servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    producer = KafkaProducer(
        bootstrap_servers=[server.strip() for server in servers.split(",") if server.strip()],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks="all",
        retries=3,
        max_block_ms=1000,
        request_timeout_ms=3000,
    )

    cleanup_func = getattr(producer, "_cleanup_func", None)
    if cleanup_func:
        try:
            atexit.unregister(cleanup_func)
        except Exception:
            pass

    def _cleanup():
        try:
            producer.flush(timeout=2.0)
        except Exception:
            pass
        try:
            producer.close(timeout=2.0)
        except Exception:
            pass

    atexit.register(_cleanup)
    return producer


def publish_job(job):
    try:
        get_job_producer().send(
            os.getenv("KAFKA_JOB_TOPIC", "audql.jobs"),
            {"job_id": str(job.pk)},
        )
    except Exception:
        logger.exception("Could not notify Kafka about queued job %s", job.pk)


def enqueue_job(kind, payload, user=None):
    if kind not in QueueJob.Kind.values:
        raise ValueError(f"Unsupported queue job kind: {kind}")
    job = QueueJob.objects.create(kind=kind, payload=payload, user=user)
    if connection.in_atomic_block:
        transaction.on_commit(lambda: publish_job(job))
    else:
        publish_job(job)
    return job


def _csv_cell(value):
    value = str(value)
    if value.lstrip(" \t\r\n").startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def _process_job(job):
    payload = job.payload

    if job.kind in (QueueJob.Kind.SEARCH_INDEX, QueueJob.Kind.SEARCH_DELETE):
        models = {
            "products": Product,
            "customers": Customer,
            "orders": Order,
        }
        model = models[payload["resource"]]
        instance = model.objects.filter(pk=payload["record_id"]).first()
        if job.kind == QueueJob.Kind.SEARCH_INDEX:
            if instance is not None:
                index_instance(instance)
        elif instance is None:
            delete_instance(model(pk=payload["record_id"]))
        else:
            delete_instance(instance)
        return {"indexed": instance is not None}

    if job.kind == QueueJob.Kind.QUERY_GENERATE:
        user = User.objects.get(pk=payload["user_id"])
        return SearchService().generate_query_response(user, payload["prompt"])

    if job.kind == QueueJob.Kind.QUERY_AUDIO:
        storage_path = payload.get("storage_path", "")
        if not storage_path or not default_storage.exists(storage_path):
            raise FileNotFoundError(f"Audio file not found in storage: {storage_path}")
        try:
            user = User.objects.get(pk=payload["user_id"])
            with default_storage.open(storage_path, "rb") as audio_file:
                return SearchService().generate_query_response_from_audio(user, audio_file)
        finally:
            if default_storage.exists(storage_path):
                default_storage.delete(storage_path)

    if job.kind in (
        QueueJob.Kind.EMAIL_ACTIVATION,
        QueueJob.Kind.EMAIL_PASSWORD_RESET,
        QueueJob.Kind.NOTIFICATION_SEND,
    ):
        user = User.objects.get(pk=payload["user_id"])
        if job.kind == QueueJob.Kind.NOTIFICATION_SEND:
            return send_user_notification(
                user_id=user.pk,
                subject=payload["subject"],
                body=payload["body"],
                data=payload.get("data"),
                channels=payload.get("channels", ["push"]),
            )

        from django.contrib.auth.tokens import PasswordResetTokenGenerator
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from utils.algorithms import TokenGenerator

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        api_origin = payload["api_origin"].rstrip("/")
        if job.kind == QueueJob.Kind.EMAIL_ACTIVATION:
            token = TokenGenerator().make_token(user)
            subject = f"Welcome, {user.email}"
            body = (
                "This is the link to verify your email. "
                f"{api_origin}/auth/activate/{uidb64}/{token}/"
            )
        else:
            token = PasswordResetTokenGenerator().make_token(user)
            subject = f"Click on link to reset password, {user.email}"
            body = (
                "This is the link to reset password. "
                f"{api_origin}/auth/reset-password/verify/{uidb64}/{token}/"
            )
        return send_email_notification(
            subject=subject,
            body=body,
            recipients=[user.email],
        )

    if job.kind == QueueJob.Kind.ORDERS_EXPORT:
        import csv
        from io import StringIO

        orders = Order.objects.filter(user_id=payload["user_id"]).select_related("user")
        order_id = payload.get("order_id")
        if order_id:
            orders = orders.filter(pk=order_id)
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["Order ID", "Customer Name", "Status", "Date & Time", "Price"])
        for order in orders:
            writer.writerow(
                [
                    _csv_cell(order.pk),
                    _csv_cell(order.user.first_name),
                    _csv_cell(order.status),
                    _csv_cell(order.created),
                    _csv_cell(order.subtotal),
                ]
            )
        return {
            "filename": f"order_{order_id}.csv" if order_id else "orders.csv",
            "content": buffer.getvalue(),
        }

    raise ValueError(f"Unsupported queue job kind: {job.kind}")


def process_job(job_id):
    now = timezone.now()
    stale_before = now - timedelta(minutes=STALE_JOB_MINUTES)
    with transaction.atomic():
        job = QueueJob.objects.select_for_update().get(pk=job_id)
        if job.status in (QueueJob.Status.SUCCEEDED, QueueJob.Status.FAILED):
            return job
        if (
            job.status == QueueJob.Status.RUNNING
            and job.started_at
            and job.started_at > stale_before
        ):
            return job
        if job.available_at > now:
            return job
        job.status = QueueJob.Status.RUNNING
        job.started_at = now
        job.attempts += 1
        job.error = ""
        job.save(update_fields=["status", "started_at", "attempts", "error", "updated_at"])

    try:
        result = _process_job(job)
    except Exception as exc:
        logger.exception("Queue job %s (%s) failed", job.pk, job.kind)
        job.refresh_from_db()
        job.error = "The background task failed. Please try again."
        job.started_at = None
        is_unretryable = (
            job.attempts >= MAX_JOB_ATTEMPTS
            or (
                job.kind == QueueJob.Kind.QUERY_AUDIO
                and not default_storage.exists(job.payload.get("storage_path", ""))
            )
        )
        if is_unretryable:
            job.status = QueueJob.Status.FAILED
        else:
            job.status = QueueJob.Status.QUEUED
            job.available_at = timezone.now() + timedelta(seconds=2 ** job.attempts)
        job.save(
            update_fields=[
                "status",
                "error",
                "started_at",
                "available_at",
                "updated_at",
            ]
        )
        return job

    job.refresh_from_db()
    job.result = result
    job.error = ""
    job.status = QueueJob.Status.SUCCEEDED
    job.started_at = None
    job.save(update_fields=["result", "error", "status", "started_at", "updated_at"])
    return job
