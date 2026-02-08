from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, include
from .views import MyTokenObtainPairView
from .views import RegisterViewSet, VendorViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r"register", RegisterViewSet, basename="register")
router.register(r"vendors", VendorViewSet, basename="vendors")




urlpatterns = [
    path("token/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("", include(router.urls))
]
