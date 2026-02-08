from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, CheckoutViewSet

router = DefaultRouter()
router.register( r"vendors/(?P<vendor_slug>[^/.]+)/orders", OrderViewSet, basename="vendor-orders" )
router.register( r"vendors/(?P<vendor_slug>[^/.]+)/checkout", CheckoutViewSet, basename="checkout" )

urlpatterns = router.urls