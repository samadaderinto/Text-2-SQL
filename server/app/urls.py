from rest_framework import routers
from .views import  QueryViewSet, AuthViewSet, ProductViewSet, CustomerViewSet, OrderViewSet, SettingsViewSet


router = routers.DefaultRouter()

router.register(r"auth", AuthViewSet, basename="auth")
router.register(r"query", QueryViewSet, basename="query")
router.register(r"customers", CustomerViewSet, basename="customers")
router.register(r"product", ProductViewSet, basename="products")
router.register(r"orders", OrderViewSet, basename="orders")
router.register(r"settings", SettingsViewSet, basename="settings")


urlpatterns = router.urls