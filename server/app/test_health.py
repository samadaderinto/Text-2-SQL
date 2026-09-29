from unittest.mock import patch

from django.test import TestCase, override_settings


class HealthCheckTests(TestCase):
    def test_liveness_check_does_not_depend_on_services(self):
        with patch("app.health._check_database", side_effect=RuntimeError):
            response = self.client.get("/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    @override_settings(ELASTICSEARCH_ENABLED=False)
    def test_readiness_check_reports_database_and_cache(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "checks": {
                    "database": {"status": "ok"},
                    "cache": {"status": "ok"},
                },
            },
        )

    @override_settings(ELASTICSEARCH_ENABLED=False)
    @patch("app.health._check_database", side_effect=RuntimeError("private detail"))
    def test_readiness_check_returns_unavailable_without_leaking_errors(
        self, _database_check
    ):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["checks"]["database"], {"status": "error"})
        self.assertNotIn("private detail", response.content.decode())

    @override_settings(ELASTICSEARCH_ENABLED=True)
    @patch("app.health._check_elasticsearch")
    def test_readiness_checks_elasticsearch_when_enabled(self, elasticsearch_check):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["checks"]["elasticsearch"], {"status": "ok"})
        elasticsearch_check.assert_called_once_with()
