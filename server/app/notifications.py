import json
import logging
import os

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification, NotificationDevice, User


logger = logging.getLogger(__name__)
FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"


def send_email_notification(*, subject, body, recipients):
    if not recipients:
        return {"sent": 0}
    sent = send_mail(
        subject,
        body,
        settings.DEFAULT_FROM_EMAIL,
        recipients,
        fail_silently=False,
    )
    return {"sent": sent}


def _load_fcm_credentials():
    from google.oauth2 import service_account

    service_account_json = os.getenv("FCM_SERVICE_ACCOUNT_JSON", "").strip()
    service_account_file = os.getenv("FCM_SERVICE_ACCOUNT_FILE", "").strip()

    if service_account_json:
        info = json.loads(service_account_json)
        return service_account.Credentials.from_service_account_info(
            info, scopes=[FCM_SCOPE]
        )
    if service_account_file:
        return service_account.Credentials.from_service_account_file(
            service_account_file, scopes=[FCM_SCOPE]
        )
    return None


def send_fcm_notification(*, tokens, title, body, data=None):
    if not getattr(settings, "FCM_ENABLED", False):
        return {"sent": 0, "skipped": "fcm_disabled"}

    if not tokens:
        return {"sent": 0}

    from google.auth.transport.requests import AuthorizedSession

    project_id = getattr(settings, "FCM_PROJECT_ID", "")
    credentials = _load_fcm_credentials()
    if not project_id or credentials is None:
        raise RuntimeError("FCM is enabled but FCM_PROJECT_ID or credentials are missing.")

    session = AuthorizedSession(credentials)
    url = f"https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
    sent = 0
    failed_tokens = []

    for token in tokens:
        message = {
            "message": {
                "token": token,
                "notification": {"title": title, "body": body},
                "data": {key: str(value) for key, value in (data or {}).items()},
            }
        }
        response = session.post(url, json=message, timeout=10)
        if response.status_code == 404:
            failed_tokens.append(token)
            continue
        response.raise_for_status()
        sent += 1

    if failed_tokens:
        NotificationDevice.objects.filter(token__in=failed_tokens).update(is_active=False)

    return {"sent": sent, "disabled_tokens": len(failed_tokens)}


def send_user_notification(*, user_id, subject, body, channels=None, data=None):
    user = User.objects.get(pk=user_id)
    preferences = Notification.objects.filter(user=user).first()
    channels = set(channels or ["email", "push"])
    result = {"email": None, "push": None}

    if "email" in channels and (
        preferences is None or preferences.email_notification
    ):
        result["email"] = send_email_notification(
            subject=subject,
            body=body,
            recipients=[user.email],
        )

    if "push" in channels and (
        preferences is None or preferences.push_notification
    ):
        tokens = list(
            NotificationDevice.objects.filter(user=user, is_active=True).values_list(
                "token", flat=True
            )
        )
        result["push"] = send_fcm_notification(
            tokens=tokens,
            title=subject,
            body=body,
            data=data,
        )

    logger.info("Notification sent for user %s through %s", user_id, sorted(channels))
    return result


def enqueue_user_notification(*, user_id, subject, body, channels=None, data=None):
    from .job_queue import enqueue_job
    from .models import QueueJob

    user = User.objects.get(pk=user_id)
    return enqueue_job(
        QueueJob.Kind.NOTIFICATION_SEND,
        {
            "user_id": user.pk,
            "subject": subject,
            "body": body,
            "channels": list(channels) if channels else ["email", "push"],
            "data": data or {},
        },
        user=user,
    )

