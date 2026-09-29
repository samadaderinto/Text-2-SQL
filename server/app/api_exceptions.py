import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        if response.status_code >= 500:
            request = context.get("request")
            logger.error(
                "API request failed with status %s: %s %s",
                response.status_code,
                getattr(request, "method", "unknown"),
                getattr(request, "path", "unknown"),
                exc_info=(type(exc), exc, exc.__traceback__),
            )
        return response

    request = context.get("request")
    logger.error(
        "Unhandled API exception for %s %s",
        getattr(request, "method", "unknown"),
        getattr(request, "path", "unknown"),
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return Response(
        {"detail": "An unexpected error occurred. Please try again later."},
        status=500,
    )
