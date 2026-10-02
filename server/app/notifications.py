import json
import logging
import os

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification, NotificationDevice, User


logger = logging.getLogger(__name__)
FCM_SCOPE = "https://www.googleapis.com/auth/firebase.messaging"
SUPPORTED_NOTIFICATION_CHANNELS = {"email", "push"}


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
    if not tokens:
        return {"sent": 0}

    if not getattr(settings, "FCM_ENABLED", False):
        raise RuntimeError("FCM is disabled but active notification devices exist.")

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


def _notification_channels(channels):
    selected_channels = ("email", "push") if channels is None else tuple(channels)
    unsupported_channels = set(selected_channels) - SUPPORTED_NOTIFICATION_CHANNELS
    if unsupported_channels:
        raise ValueError(
            f"Unsupported notification channels: {', '.join(sorted(unsupported_channels))}"
        )
    return selected_channels


def send_user_notification(*, user_id, subject, body, data=None, channels=None):
    user = User.objects.get(pk=user_id)
    preferences = Notification.objects.filter(user=user).first()
    selected_channels = _notification_channels(channels)

    result = {}
    if "email" in selected_channels:
        if preferences is not None and not preferences.email_notification:
            result["email"] = {"sent": 0, "skipped": "user_preference"}
        else:
            result["email"] = send_email_notification(
                subject=subject,
                body=body,
                recipients=[user.email],
            )

    if "push" in selected_channels:
        if preferences is not None and not preferences.push_notification:
            result["push"] = {"sent": 0, "skipped": "user_preference"}
        else:
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

    if result.get("push", {}).get("sent"):
        logger.info("Push notification sent for user %s", user_id)
    if result.get("email", {}).get("sent"):
        logger.info("Email notification sent for user %s", user_id)
    return result


def enqueue_user_notification(*, user_id, subject, body, data=None, channels=None):
    from .job_queue import enqueue_job
    from .models import QueueJob

    selected_channels = _notification_channels(channels)

    user = User.objects.get(pk=user_id)
    return enqueue_job(
        QueueJob.Kind.NOTIFICATION_SEND,
        {
            "user_id": user.pk,
            "subject": subject,
            "body": body,
            "data": data or {},
            "channels": list(selected_channels),
        },
        user=user,
    )
