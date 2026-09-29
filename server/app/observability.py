import logging
import re
from datetime import datetime, timezone

from django.conf import settings
from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .kafka_logging import publish_log_event


logger = logging.getLogger(__name__)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
SECRET_PATTERN = re.compile(
    r"(?i)\b(password|token|authorization|secret)\b\s*[:=]\s*\S+"
)


def redact_sensitive_text(value):
    value = EMAIL_PATTERN.sub("[redacted-email]", value)
    return SECRET_PATTERN.sub(r"\1=[redacted]", value)


class ClientLogThrottle(AnonRateThrottle):
    scope = "client_logs"


class ClientLogSerializer(serializers.Serializer):
    level = serializers.ChoiceField(choices=("error", "warning"))
    event_type = serializers.ChoiceField(
        choices=("window_error", "unhandled_rejection", "api_error")
    )
    message = serializers.CharField(max_length=1000, trim_whitespace=True)
    stack = serializers.CharField(max_length=4000, required=False, allow_blank=True)
    route = serializers.CharField(max_length=300, required=False, allow_blank=True)
    method = serializers.CharField(max_length=10, required=False, allow_blank=True)
    status_code = serializers.IntegerField(
        required=False, min_value=100, max_value=599
    )
    timestamp = serializers.DateTimeField(required=False)

    def validate_route(self, value):
        return value.split("?", 1)[0].split("#", 1)[0]


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([ClientLogThrottle])
def client_log(request):
    serializer = ClientLogSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    timestamp = data.get("timestamp", datetime.now(timezone.utc))
    event = {
        "timestamp": timestamp.astimezone(timezone.utc).isoformat(),
        "level": data["level"],
        "service": "frontend",
        "environment": settings.DEPLOY_ENV,
        "event_type": data["event_type"],
        "message": redact_sensitive_text(data["message"]),
        "route": data.get("route", ""),
    }
    if data.get("stack"):
        event["stack"] = redact_sensitive_text(data["stack"])
    if data.get("method"):
        event["method"] = data["method"].upper()
    if data.get("status_code"):
        event["status_code"] = data["status_code"]

    try:
        publish_log_event(event)
    except Exception:
        logger.exception("Could not publish frontend error event to Kafka")
        return Response(
            {"detail": "Logging service is temporarily unavailable."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response(status=status.HTTP_202_ACCEPTED)
