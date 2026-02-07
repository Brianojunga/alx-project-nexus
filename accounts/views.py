from rest_framework.response import Response
from .serializers import RegisterSerializer, VendorSerializer
from rest_framework import viewsets, status
from .models import CustomUser, Membership, Vendor
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from accounts.services.access_control import make_agent, remove_agent
from .permissions import IsPlatformAdmin, IsVendorAdmin
from django.core.cache import cache

# Create your views here.
class RegisterViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Skip database queries during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return CustomUser.objects.none()
            
        user = self.request.user 
        if not user.is_authenticated:
            return CustomUser.objects.none()
            
        membership = Membership.objects.filter(user=user).first()
        if membership and membership.role in ["platform_admin", "platform_agent"]:
            return CustomUser.objects.all()

        if membership and membership.role in ["vendor_admin", "vendor_agent"]:
            vendor_memberships = Membership.objects.filter(vendor=membership.vendor, role__in="user")
            user_ids = vendor_memberships.values_list("user__id", flat=True)
            return CustomUser.objects.filter(id__in=user_ids)
        
        return CustomUser.objects.none()
    
    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated, IsPlatformAdmin])
    def make_platform_agent(self, request, pk=None):
        user = self.request.user
        updated_membership = make_agent(user, pk, "platform_admin")
        return Response(
            {"detail": f"User {updated_membership.user.email} promoted to platform agent."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated, IsVendorAdmin])
    def make_vendor_agent(self, request, pk=None):
        user = self.request.user
        updated_membership = make_agent(user, pk, "vendor_admin")
        return Response(
            {"detail": f"User {updated_membership.user.email} promoted to {updated_membership.vendor.company_name} agent."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated, IsPlatformAdmin])
    def remove_platform_agent(self, request, pk=None):
        user = self.request.user
        updated_membership = remove_agent(user, pk, "platform_admin")
        return Response(
            {"detail": f"User {updated_membership.user.email} removed from platform agent."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated, IsVendorAdmin])
    def remove_vendor_agent(self, request, pk=None):
        user = self.request.user
        membership =Membership.objects.filter(user=user).first()
        updated_membership = remove_agent(user, pk, "vendor_admin")
        return Response(
            {"detail": f"User {updated_membership.user.email} removed from {membership.vendor.company_name} agent."},
            status=status.HTTP_200_OK
        )
    
class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        # Skip database queries during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Vendor.objects.none()
            
        user = self.request.user
        if not user.is_authenticated:
            return Vendor.objects.none()
        
        membership = Membership.objects.filter(user=user).first()
        if user.is_admin or (membership and membership.role in ["platform_admin", "platform_agent"]):
            return Vendor.objects.all()
        if membership and membership.role == "vendor_admin":
            return Vendor.objects.filter(id=membership.vendor.id)
        return Vendor.objects.none()
    
    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated, IsPlatformAdmin])
    def approve_vendor(self, request, pk=None):
        vendor = self.get_object()
        vendor.approved = True
        vendor.save()
        return Response(
            {"detail": f"Vendor {vendor.company_name} approved."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PATCH"], permission_classes=[IsAuthenticated, IsPlatformAdmin])
    def reject_vendor(self, request, pk=None):
        vendor = self.get_object()
        vendor.approved = False
        vendor.save()
        return Response(
            {"detail": f"Vendor {vendor.company_name} rejected."},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["PATCH", "GET"], permission_classes=[IsAuthenticated, IsPlatformAdmin])
    def get_approved_vendors(self, request):
   
        
        cache_key = 'vendors_approved'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached, status=status.HTTP_200_OK)

        approved_vendors = Vendor.objects.filter(approved=True)
        serializer = self.get_serializer(approved_vendors, many=True)
        cache.set(cache_key, serializer.data, 60 * 15)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=["PATCH", "GET"], permission_classes=[IsAuthenticated, IsPlatformAdmin])
    def get_pending_vendors(self, request):
        
        cache_key = 'vendors_pending'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached, status=status.HTTP_200_OK)

        pending_vendors = Vendor.objects.filter(approved=False)
        serializer = self.get_serializer(pending_vendors, many=True)
        cache.set(cache_key, serializer.data, 60 * 15)
        return Response(serializer.data, status=status.HTTP_200_OK)

