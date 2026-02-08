from rest_framework import serializers
from .models import Payment, VendorSubAccount

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = fields

class VendorSubAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorSubAccount
        fields = ["id", "vendor", "subaccount_code", "percentage_charge", "created_at",]
        read_only_fields = fields