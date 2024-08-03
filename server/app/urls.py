from rest_framework import routers
from .views import  QueryViewSet, AuthViewSet, ProductViewSet, CustomerViewSet, OrderViewSet, SettingsViewSet


router = routers.DefaultRouter()

router.register(r"", AuthViewSet, basename="auth")
router.register(r"", QueryViewSet, basename="query")
router.register(r"", CustomerViewSet, basename="customers")
router.register(r"", ProductViewSet, basename="products")
router.register(r"", OrderViewSet, basename="orders")
router.register(r"", SettingsViewSet, basename="orders")


urlpatterns = router.urls