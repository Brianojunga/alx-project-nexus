from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser, Membership, Vendor

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add extra claims if needed
        token["email"] = user.email
        return token

    def validate(self, attrs):
        # Override to allow login with email instead of username
        credentials = {
            "email": attrs.get("email"),
            "password": attrs.get("password")
        }
        user = CustomUser.objects.filter(email=credentials["email"]).first()
        if user is None or not user.check_password(credentials["password"]):
            raise serializers.ValidationError("Invalid credentials")
        data = super().validate({"username": user.email, "password": credentials["password"]})
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    vendor_role = serializers.SerializerMethodField()


    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "password", "vendor_role"]

    def get_vendor_role(self, obj):
        memberships  = Membership.objects.filter(user=obj)
        role_vendor = []
        for i, membership in enumerate(memberships):
            role_vendor.append({
                "company": i+1,
                "company_name": membership.vendor.company_name if membership.vendor else None,
                "role": membership.role
            })
        return role_vendor
    
    def validate(self, data):
        email = data.get("email", None)
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User with this email exists")
        
class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ["user", "vendor", "role"]
        read_only_fields = ["user"]

     
class VendorSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True, source='membership_set')
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = ["company_name", "address", "phone_number", "email", "slug", "approved", "is_active", "memberships", "owner"]
        read_only_fields = ["slug", "approved", "is_active"]

    def get_owner(self, obj):
        membership = Membership.objects.filter(vendor=obj, role="vendor_admin").first()
        if membership:
            return MembershipSerializer(membership).data
        return None

    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Phone number must contain digits only.")