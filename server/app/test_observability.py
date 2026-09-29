import json
import logging
from unittest.mock import patch

from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from .kafka_logging import JsonLogFormatter, KafkaLogHandler

@override_settings(REST_FRAMEWORK={"DEFAULT_THROTTLE_RATES": {"client_logs": "100/min"}})
class ClientLogApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    @patch("app.observability.publish_log_event")
    def test_client_error_is_sanitized_and_published_without_authentication(
        self, publish
    ):
        response = self.client.post(
            "/logs/client/",
            {
                "level": "error",
                "event_type": "api_error",
                "message": "Failure for user@example.com with password=hunter2",
                "route": "/orders/?access_token=private",
                "method": "post",
                "status_code": 500,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 202)
        event = publish.call_args.args[0]
        self.assertEqual(event["service"], "frontend")
        self.assertEqual(event["route"], "/orders/")
        self.assertNotIn("user@example.com", event["message"])
        self.assertNotIn("hunter2", event["message"])

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

    def test_invalid_frontend_events_are_rejected(self):
        response = self.client.post(
            "/logs/client/",
            {"level": "debug", "event_type": "api_error", "message": "Oops"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    @patch(
        "app.observability.publish_log_event",
        side_effect=RuntimeError("broker unavailable"),
    )
    def test_kafka_failure_is_reported_to_the_frontend(self, _publish):
        response = self.client.post(
            "/logs/client/",
            {
                "level": "error",
                "event_type": "api_error",
                "message": "Request failed",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.data["detail"], "Logging service is temporarily unavailable."
        )
