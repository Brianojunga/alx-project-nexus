# orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "price",
            "quantity",
            "total",
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "vendor",
            "status",
            "subtotal",
            "tax",
            "total",
            "items",
            "created_at",
        ]
        read_only_fields = fields
