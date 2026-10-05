import logging
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import OpenApiResponse, extend_schema


logger = logging.getLogger(__name__)


def _check_database():
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT 1")


def _check_cache():
    key = f"audql:health:{uuid4().hex}"
    value = uuid4().hex
    try:
        cache.set(key, value, timeout=5)
        if cache.get(key) != value:
            raise RuntimeError("Cache read/write check failed.")
    finally:
        cache.delete(key)


def _check_elasticsearch():
    from .search_index import get_elasticsearch_client

    if not get_elasticsearch_client().ping():
        raise RuntimeError("Elasticsearch did not respond to ping.")


def _run_check(name, check):
    try:
        check()
    except Exception:
        logger.exception("Readiness check failed: %s", name)
        return {"status": "error"}
    return {"status": "ok"}


@extend_schema(
    summary="Application liveness probe",
    description=(
        "Kubernetes/container liveness probe. Immediately returns HTTP 200 with `status: ok` if the web process is running. "
        "Does not inspect external dependencies. "
        "Compare with `/health/` (readiness probe), which actively verifies database, cache, and Elasticsearch connectivity."
    ),
    responses={
        200: OpenApiResponse(description="Application web server process is responsive"),
    },
    tags=["Observability"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def liveness_check(request):
    return JsonResponse({"status": "ok"})


@extend_schema(
    summary="System readiness health check",
    description=(
        "Comprehensive infrastructure readiness check verifying connectivity to the database, Redis cache, "
        "and Elasticsearch cluster (when enabled). "
        "Returns HTTP 200 when all core systems are operational, or HTTP 503 Service Unavailable if any component fails. "
        "Compare with `/health/live/`, which only tests application process liveness without evaluating dependencies."
    ),
    responses={
        200: OpenApiResponse(description="All downstream services (database, cache, elasticsearch) are healthy"),
        503: OpenApiResponse(description="One or more critical service dependencies failed health checks"),
    },
    tags=["Observability"],
)
@api_view(["GET"])
@permission_classes([AllowAny])
def readiness_check(request):
    check_functions = {
        "database": _check_database,
        "cache": _check_cache,
    }
    if settings.ELASTICSEARCH_ENABLED:
        check_functions["elasticsearch"] = _check_elasticsearch

    checks = {
        name: _run_check(name, check)
        for name, check in check_functions.items()
    }
    healthy = all(result["status"] == "ok" for result in checks.values())
    return JsonResponse(
        {"status": "ok" if healthy else "error", "checks": checks},
        status=200 if healthy else 503,
    )
