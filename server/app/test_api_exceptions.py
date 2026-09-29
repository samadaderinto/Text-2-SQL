from unittest.mock import Mock

from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from .api_exceptions import api_exception_handler


class ApiExceptionHandlerTests(SimpleTestCase):
    def setUp(self):
        self.request = APIRequestFactory().get("/api/example/")
        self.context = {"request": self.request}

    def test_preserves_framework_validation_errors(self):
        response = api_exception_handler(
            ValidationError({"email": ["Enter a valid email address."]}),
            self.context,
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data,
            {"email": ["Enter a valid email address."]},
        )

    def test_hides_unhandled_exception_details_from_clients(self):
        error = RuntimeError("database password must not be exposed")
        with self.assertLogs("app.api_exceptions", level="ERROR"):
            response = api_exception_handler(error, self.context)

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.data,
            {"detail": "An unexpected error occurred. Please try again later."},
        )
        self.assertNotIn("database password", str(response.data))
