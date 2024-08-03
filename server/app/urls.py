from rest_framework import routers
from .views import  QueryViewSet, AuthViewSet


router = routers.DefaultRouter()

router.register(r"", AuthViewSet, basename="auth")
router.register(r"", QueryViewSet, basename="query")

urlpatterns = router.urls