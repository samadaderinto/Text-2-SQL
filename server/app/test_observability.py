import json
import logging
from unittest.mock import patch

from django.test import TestCase

from .kafka_logging import JsonLogFormatter, KafkaLogHandler


class BackendLoggingTests(TestCase):
    def test_backend_json_logs_are_structured_and_redacted(self):
        record = logging.LogRecord(
            "app.views",
            logging.ERROR,
            __file__,
            1,
            "Failed for user@example.com with password=hunter2",
            (),
            None,
        )

        event = json.loads(JsonLogFormatter().format(record))

        self.assertEqual(event["service"], "backend")
        self.assertEqual(event["level"], "error")
        self.assertNotIn("user@example.com", event["message"])
        self.assertNotIn("hunter2", event["message"])

    @patch("app.kafka_logging.get_kafka_producer")
    def test_backend_log_handler_publishes_structured_events(self, get_producer):
        handler = KafkaLogHandler()
        handler.setFormatter(JsonLogFormatter())
        record = logging.LogRecord(
            "app.views",
            logging.WARNING,
            __file__,
            1,
            "Slow API request",
            (),
            None,
        )

        handler.emit(record)

        event = get_producer.return_value.send.call_args.args[1]
        self.assertEqual(
            get_producer.return_value.send.call_args.args[0], "audql.logs"
        )
        self.assertEqual(event["message"], "Slow API request")
        get_producer.return_value.send.return_value.add_errback.assert_called_once()
