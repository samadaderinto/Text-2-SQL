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
