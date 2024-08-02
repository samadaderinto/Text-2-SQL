from rest_framework import routers
from .views import AppViewSet


router = routers.DefaultRouter()

router.register(r"", AppViewSet, basename="")

urlpatterns = router.urls