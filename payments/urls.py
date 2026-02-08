from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, Verify
from django.urls import path

router = DefaultRouter()

urlpatterns = [
    path('payments/<str:vendor_slug>/<int:order_id>/', PaymentViewSet.as_view({'post': 'create'}), name='create-payment'),
    path('payments/verify/<str:reference>/', Verify.as_view(), name='verify-payment'),
] + router.urls
