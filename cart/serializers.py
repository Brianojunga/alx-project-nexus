from rest_framework import serializers
from .models import Cart, CartItem
from accounts.serializers import VendorSerializer, RegisterSerializer
from django.contrib.auth import get_user_model
from products.serializers import ProductSerializer

user = get_user_model()

class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user", "session_key", "is_active", "vendor", "items", "total", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "session_key", "is_active", "vendor", "created_at", "updated_at"]

    def get_items(self, obj):
        items = CartItem.objects.filter(cart=obj)
        return CartItemSerializer(items, many=True).data


class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    price_total = serializers.SerializerMethodField()
    product = ProductSerializer()

    class Meta:
        model = CartItem
        fields = ["id", "cart", "product", "quantity", "price_total", "created_at", "updated_at"]
        read_only_fields = ["id", "cart", "product", "created_at", "updated_at"]

    def get_price_total(self, obj):
        return obj.total
        


