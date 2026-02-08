from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import CustomUser, Membership, Vendor
from django.contrib.auth import authenticate

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username field and add email field
        self.fields[self.username_field] = serializers.EmailField()
        self.fields['password'] = serializers.CharField(write_only=True)
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError(
                {"non_field_errors": ["Email and password are required"]},
                code='authorization'
            )

        # Manually authenticate with email since CustomUser uses email as USERNAME_FIELD
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials"]},
                code='authorization'
            )
        
        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError(
                {"non_field_errors": ["Invalid credentials"]},
                code='authorization'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": ["User account is disabled"]},
                code='authorization'
            )

        # Generate tokens
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
        return data

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    vendor_role = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ["id", "email", "first_name", "last_name", "password", "vendor_role"]
        read_only_fields = ["id", "vendor_role"]

    def get_vendor_role(self, obj):
        memberships = Membership.objects.filter(user=obj)
        role_vendor = []
        for i, membership in enumerate(memberships):
            role_vendor.append({
                "company": i+1,
                "company_name": membership.vendor.company_name if membership.vendor else None,
                "role": membership.role
            })
        return role_vendor if role_vendor else None
    
    def validate(self, data):
        email = data.get("email", None)
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "User with this email already exists"})
        return data
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        email = validated_data.pop('email')
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )
        return user
        
class MembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    
    class Meta:
        model = Membership
        fields = ["id", "user", "user_email", "user_first_name", "user_last_name", "vendor", "role"]
        read_only_fields = ["user"]

     
class VendorSerializer(serializers.ModelSerializer):
    memberships = MembershipSerializer(many=True, read_only=True, source='membership_set')
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = ["id", "company_name", "address", "phone_number", "email", "slug", "approved", "is_active", "memberships", "owner"]
        read_only_fields = ["slug", "approved", "is_active", "owner"]

    def get_owner(self, obj):
        membership = Membership.objects.filter(vendor=obj, role="vendor_admin").first()
        if membership:
            return {
                "id": membership.user.id,
                "email": membership.user.email,
                "first_name": membership.user.first_name,
                "last_name": membership.user.last_name,
                "role": membership.role
            }
        return None

    def validate(self, data):
        phone_number = data.get('phone_number')
        slug = data.get('slug')
        if slug and Vendor.objects.filter(slug=slug).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise serializers.ValidationError("Vendor with this slug already exists.")
        if phone_number:
            if phone_number.startswith("+"):
                phone_number = phone_number[1:]
                data['phone_number'] = phone_number

            if not phone_number.isdigit():
                raise serializers.ValidationError(
                    "Invalid phone number format."
                )
        return data
