import json
import logging
import os
import time
import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import DatabaseError, close_old_connections
from django.db.models import Q
from django.utils import timezone
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.job_queue import process_job
from app.models import QueueJob


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process background jobs using Kafka notifications and the database outbox."

    def handle(self, *args, **options):
        topic = os.getenv("KAFKA_JOB_TOPIC", "audql.jobs")
        group_id = os.getenv("KAFKA_JOB_GROUP_ID", "audql-workers")
        bootstrap_servers = [
            server.strip()
            for server in os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092").split(",")
            if server.strip()
        ]
        consumer = None
        next_connection_attempt = 0.0

        self.stdout.write(f"Queue worker started; Kafka topic: {topic}")
        try:
            while True:
                close_old_connections()
                if consumer is None and time.monotonic() >= next_connection_attempt:
                    try:
                        consumer = KafkaConsumer(
                            topic,
                            bootstrap_servers=bootstrap_servers,
                            group_id=group_id,
                            enable_auto_commit=True,
                            auto_offset_reset="latest",
                            request_timeout_ms=3000,
                            api_version_auto_timeout_ms=3000,
                        )
                    except KafkaError:
                        logger.exception("Could not connect queue worker to Kafka")
                        next_connection_attempt = time.monotonic() + 5

                if consumer is not None:
                    try:
                        messages = consumer.poll(timeout_ms=250, max_records=25)
                        for records in messages.values():
                            for message in records:
                                self._process_message(message.value)
                    except KafkaError:
                        logger.exception("Kafka queue polling failed")
                        consumer.close()
                        consumer = None
                        next_connection_attempt = time.monotonic() + 5

                try:
                    queued_jobs = list(
                        QueueJob.objects.filter(
                            Q(status=QueueJob.Status.QUEUED)
                            | Q(
                                status=QueueJob.Status.RUNNING,
                                started_at__lte=timezone.now() - timedelta(minutes=15),
                            ),
                            available_at__lte=timezone.now(),
                        )
                        .order_by("created_at")
                        .values_list("pk", flat=True)[:25]
                    )
                    for job_id in queued_jobs:
                        process_job(job_id)
                except DatabaseError:
                    logger.exception("Queue worker could not scan pending jobs")
                    time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write("Queue worker stopped.")
        finally:
            if consumer is not None:
                consumer.close()

    @staticmethod
    def _process_message(value):
        try:
            payload = json.loads(value.decode("utf-8"))
            job_id = uuid.UUID(payload["job_id"])
        except (AttributeError, KeyError, TypeError, UnicodeDecodeError, ValueError):
            logger.error("Received malformed Kafka queue message")
            return
        try:
            process_job(job_id)
        except QueueJob.DoesNotExist:
            logger.warning("Kafka message references missing queue job %s", job_id)
