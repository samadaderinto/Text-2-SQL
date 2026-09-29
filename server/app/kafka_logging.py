import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from functools import lru_cache


EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
SECRET_PATTERN = re.compile(
    r"(?i)\b(password|token|authorization|secret)\b\s*[:=]\s*\S+"
)


def redact_log_text(value):
    value = EMAIL_PATTERN.sub("[redacted-email]", value)
    return SECRET_PATTERN.sub(r"\1=[redacted]", value)


@lru_cache(maxsize=1)
def get_kafka_producer():
    from kafka import KafkaProducer

    brokers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092").split(",")
    return KafkaProducer(
        bootstrap_servers=[broker.strip() for broker in brokers if broker.strip()],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks=1,
        retries=3,
        max_block_ms=1000,
        request_timeout_ms=3000,
        linger_ms=25,
    )


class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        event = {
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "level": record.levelname.lower(),
            "service": "backend",
            "environment": os.getenv("DEPLOY_ENV", "local"),
            "logger": record.name,
            "message": redact_log_text(record.getMessage()),
        }
        if record.exc_info:
            event["exception"] = redact_log_text(
                self.formatException(record.exc_info)
            )
        return json.dumps(event, ensure_ascii=True)


class KafkaLogHandler(logging.Handler):
    def emit(self, record):
        try:
            event = json.loads(self.format(record))
            get_kafka_producer().send(
                os.getenv("KAFKA_LOG_TOPIC", "audql.logs"), event
            ).add_errback(self._report_delivery_error)
        except Exception:
            self.handleError(record)

    @staticmethod
    def _report_delivery_error(error):
        sys.stderr.write(f"Kafka log delivery failed: {error}\n")
        sys.stderr.flush()


def publish_log_event(event):
    return get_kafka_producer().send(
        os.getenv("KAFKA_LOG_TOPIC", "audql.logs"), event
    )
