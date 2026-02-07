from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from accounts.models import Membership, Vendor
from .utilis import get_session_key
from services.caching import caching

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Cart.objects.none()

        request = self.request
        user = request.user
        vendor_slug = self.kwargs.get("vendor_slug")

        # Admin / vendor roles
        if user.is_authenticated:
            membership = Membership.objects.filter(
                user=user,
                vendor__slug=vendor_slug,
            ).first()

            if user.is_staff or (
                membership and membership.role in [
                    "platform_admin",
                    "vendor_admin",
                    "platform_agent",
                    "vendor_agent",
                ]
            ):
                return Cart.objects.filter(vendor__slug=vendor_slug)

            return Cart.objects.filter(
                user=user,
                vendor__slug=vendor_slug,                   
                is_active=True
            )

        # Guest user
        session_key = get_session_key(request)
        return Cart.objects.filter(
            session_key=session_key,
            vendor__slug=vendor_slug,
            is_active=True
        )

    def list(self, request, *args, **kwargs):
        # cache cart listings per vendor for admin roles
        return caching(self, request, "cart", *args, **kwargs)

    def perform_create(self, serializer):
        request = self.request
        user = request.user
        vendor_slug = self.kwargs.get("vendor_slug")

        vendor = get_object_or_404(Vendor, slug=vendor_slug)

        if user.is_authenticated:
            serializer.save(
                user=user,
                vendor=vendor
            )
        else:
            session_key = get_session_key(request)
            serializer.save(
                session_key=session_key,
                vendor=vendor
            )


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return CartItem.objects.none()

        request = self.request
        user = request.user
        vendor_slug = self.kwargs.get("vendor_slug")

        if user.is_authenticated:
            return CartItem.objects.filter(
                cart__user=user,
                product__vendor__slug=vendor_slug
            ).select_related(
                "product",
                "cart",
                "product__vendor"
            )

        # guest user
        session_key = get_session_key(request)

        return CartItem.objects.filter(
            cart__session_key=session_key,
            product__vendor__slug=vendor_slug
        ).select_related(
            "product",
            "cart",
            "product__vendor"
        )
    
    def perfom_create(self, serializer):
        request = self.request
        user = request.user
        vendor_slug = self.kwargs.get("vendor_slug")

        vendor = get_object_or_404(
            Vendor,
            slug=vendor_slug
        )

        if user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(
                user=user,
                vendor=vendor,
                is_active=True
            )
        else:
            session_key = get_session_key(request)
            cart, _ = Cart.objects.get_or_create(
                session_key=session_key,
                vendor=vendor,
                is_active=True
            )

        product = serializer.validate_data["product"]

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults ={
                "quantity" : serializer.validated_data.get("quantity", 1)
            }
        )

        if not created:
            item.quantity += serializer.validated_data.get("quantity", 1)
            item.save()

        serializer.instance = item