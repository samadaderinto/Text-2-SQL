import logging
from uuid import uuid4

from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.http import JsonResponse
from django.views.decorators.http import require_GET


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


@require_GET
def liveness_check(request):
    return JsonResponse({"status": "ok"})


@require_GET
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
