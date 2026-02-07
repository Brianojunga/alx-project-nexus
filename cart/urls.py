from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CartViewSet, CartItemViewSet

router = DefaultRouter()
router.register(r'vendors/(?P<vendor_slug>[-\w]+)/carts', CartViewSet, basename='vendor-carts')
router.register(r'vendors/(?P<vendor_slug>[-\w]+)/cartitems', CartItemViewSet, basename='vendor-cartitems')

urlpatterns =[
    path("", include(router.urls))
]