import time

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from django.http import HttpResponse


HTTP_REQUESTS = Counter(
    "audql_http_requests_total",
    "HTTP requests handled by the Django application.",
    ("method", "route", "status"),
)
HTTP_LATENCY = Histogram(
    "audql_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ("method", "route"),
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)
HTTP_ERRORS = Counter(
    "audql_http_errors_total",
    "HTTP 4xx and 5xx responses.",
    ("method", "route", "status_class"),
)


def _route(request):
    match = getattr(request, "resolver_match", None)
    return getattr(match, "route", None) or request.path.split("?", 1)[0]


class MetricsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        started = time.perf_counter()
        response = self.get_response(request)
        route = _route(request)
        method = request.method
        status = str(response.status_code)
        HTTP_REQUESTS.labels(method, route, status).inc()
        HTTP_LATENCY.labels(method, route).observe(time.perf_counter() - started)
        if response.status_code >= 400:
            HTTP_ERRORS.labels(method, route, f"{response.status_code // 100}xx").inc()
        return response


def metrics(request):
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)
