import logging
import re

logger = logging.getLogger(__name__)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
SECRET_PATTERN = re.compile(
    r"(?i)\b(password|token|authorization|secret)\b\s*[:=]\s*\S+"
)


def redact_sensitive_text(value):
    value = EMAIL_PATTERN.sub("[redacted-email]", value)
    return SECRET_PATTERN.sub(r"\1=[redacted]", value)
