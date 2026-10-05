"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularRedocView,
    SpectacularSwaggerView,
    SpectacularAPIView,
)
from app.health import liveness_check, readiness_check
from app.metrics import metrics
from app.views import QueueJobDownloadView, QueueJobStatusView


urlpatterns = [
    path("health/", readiness_check, name="health"),
    path("health/live/", liveness_check, name="health-live"),
    path("metrics/", metrics, name="metrics"),
    path("jobs/<uuid:job_id>/", QueueJobStatusView.as_view(), name="queue-job-status"),
    path(
        "jobs/<uuid:job_id>/download/",
        QueueJobDownloadView.as_view(),
        name="queue-job-download",
    ),
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
    path("docs/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path("docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
if settings.DEBUG:
    urlpatterns += [
        *static(settings.STATIC_URL, document_root=settings.STATIC_ROOT),
        *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
    ]
