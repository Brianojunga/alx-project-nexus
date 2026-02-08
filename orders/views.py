from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer
from services.caching import caching
from accounts.models import Membership
from cart.utilis import get_session_key
from cart.models import Cart
from .services import create_order_from_cart
from rest_framework.response import Response


# Create your views here.
class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    serilaizer_class = OrderSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Order.objects.none()
        
        request = self.request
        user = request.user
        vendor_slug = self.kwargs.get("vendor_slug")

        if user.is_authenticated:
            membership = Membership.objects.filter(
                user=user,
                vendor__slug = vendor_slug,
                role__in =[
                    "platform_admin",
                    "vendor_admin",
                    "platform_agent",
                    "vendor_agent",
                ],
            ).exists()
            if user.is_staff or membership:
                return Order.objects.filter(vendor__slug=vendor_slug)
            return Order.objects.filter(
                user=user,
                vendor__slug=vendor_slug
            )
        session_key = get_session_key(request)
        return Order.objects.filter(
            session_key=session_key,
            vendor__slug=vendor_slug
        )
    
    def list(self, request, *args, **kwargs):
        return caching(self, request, "order", *args, **kwargs)
    
class CheckoutViewSet(viewsets.viewset):

    def create(self, request, vendor_slug=None):
        user = request.user
        session_key = get_session_key(request)

        cart = get_object_or_404(
            Cart,
            vendor__slug = vendor_slug,
            is_active=True,
            user=user if user.is_authenticated else None,
            session_key=session_key if not user.is_authenticated else None
        )

        order = create_order_from_cart(cart)

        return Response(
            {"order_id" : order.id},
            status=status.HTTP_201_CREATED
        )