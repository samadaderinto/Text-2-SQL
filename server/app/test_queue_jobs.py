from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from .job_queue import MAX_JOB_ATTEMPTS, process_job
from .models import QueueJob, User


class QueueJobApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="queue-owner@example.com", password="ValidPass1!"
        )
        self.other_user = User.objects.create_user(
            email="queue-other@example.com", password="ValidPass1!"
        )

    def test_job_status_is_private_to_owner(self):
        job = QueueJob.objects.create(
            user=self.user,
            kind=QueueJob.Kind.QUERY_GENERATE,
            status=QueueJob.Status.SUCCEEDED,
            result={"results": []},
        )
        self.client.force_authenticate(user=self.other_user)

        response = self.client.get(f"/jobs/{job.pk}/")

        self.assertEqual(response.status_code, 404)

    def test_job_status_returns_result_after_completion(self):
        job = QueueJob.objects.create(
            user=self.user,
            kind=QueueJob.Kind.QUERY_GENERATE,
            status=QueueJob.Status.SUCCEEDED,
            result={"results": []},
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/jobs/{job.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], QueueJob.Status.SUCCEEDED)
        self.assertEqual(response.data["result"], {"results": []})

    def test_job_download_rejects_non_export_job(self):
        job = QueueJob.objects.create(
            user=self.user,
            kind=QueueJob.Kind.QUERY_GENERATE,
            status=QueueJob.Status.SUCCEEDED,
            result={"content": "not an export"},
        )
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/jobs/{job.pk}/download/")

        self.assertEqual(response.status_code, 409)


class QueueJobProcessingTests(TestCase):
    def test_successful_job_persists_result(self):
        user = User.objects.create_user(
            email="query-owner@example.com", password="ValidPass1!"
        )
        job = QueueJob.objects.create(
            user=user,
            kind=QueueJob.Kind.QUERY_GENERATE,
            payload={"user_id": user.pk, "prompt": "list products"},
        )
        result = {"status": "success", "results": []}
        with patch(
            "app.job_queue.SearchService.generate_query_response",
            return_value=result,
        ):
            processed = process_job(job.pk)

        self.assertEqual(processed.status, QueueJob.Status.SUCCEEDED)
        self.assertEqual(processed.result, result)
        self.assertEqual(processed.attempts, 1)

    def test_failed_job_is_retried_then_marked_failed(self):
        user = User.objects.create_user(
            email="retry-owner@example.com", password="ValidPass1!"
        )
        job = QueueJob.objects.create(
            user=user,
            kind=QueueJob.Kind.QUERY_GENERATE,
            payload={"user_id": user.pk, "prompt": "list products"},
        )

        with patch(
            "app.job_queue.SearchService.generate_query_response",
            side_effect=RuntimeError("temporary failure"),
        ):
            for attempt in range(MAX_JOB_ATTEMPTS):
                job.available_at = timezone.now() - timedelta(seconds=1)
                job.save(update_fields=["available_at"])
                job = process_job(job.pk)
                expected_status = (
                    QueueJob.Status.FAILED
                    if attempt == MAX_JOB_ATTEMPTS - 1
                    else QueueJob.Status.QUEUED
                )
                self.assertEqual(job.status, expected_status)

        self.assertEqual(job.attempts, MAX_JOB_ATTEMPTS)
        self.assertEqual(job.error, "The background task failed. Please try again.")

    def test_notification_send_job_delivers_via_fcm_and_email(self):
        from app.models import Notification, NotificationDevice
        from app.notifications import enqueue_user_notification

        user = User.objects.create_user(
            email="notif-user@example.com", password="ValidPass1!"
        )
        Notification.objects.create(
            user=user,
            email_notification=True,
            push_notification=True,
        )
        NotificationDevice.objects.create(
            user=user,
            token="fcm-device-token-123",
            platform="web",
            is_active=True,
        )

        job = enqueue_user_notification(
            user_id=user.pk,
            subject="Order Shipped",
            body="Your order #1001 has shipped!",
            channels=["email", "push"],
            data={"order_id": "1001"},
        )
        self.assertEqual(job.kind, QueueJob.Kind.NOTIFICATION_SEND)
        self.assertEqual(job.status, QueueJob.Status.QUEUED)

        with patch("app.notifications.send_mail", return_value=1) as mock_mail, patch(
            "app.notifications.send_fcm_notification",
            return_value={"sent": 1, "disabled_tokens": 0},
        ) as mock_fcm:
            processed = process_job(job.pk)

        self.assertEqual(processed.status, QueueJob.Status.SUCCEEDED)
        self.assertEqual(processed.result["email"], {"sent": 1})
        self.assertEqual(processed.result["push"], {"sent": 1, "disabled_tokens": 0})
        mock_mail.assert_called_once()
        mock_fcm.assert_called_once_with(
            tokens=["fcm-device-token-123"],
            title="Order Shipped",
            body="Your order #1001 has shipped!",
            data={"order_id": "1001"},
        )

