from rest_framework.permissions import BasePermission
from accounts.models import Membership
from rest_framework.permissions import SAFE_METHODS

class IsPlatformAdmin(BasePermission):
    #Permission class to check if user is a platform admin or Django superuser.
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        # Check if user has platform_admin role
        return Membership.objects.filter(
            user=request.user,
            role="platform_admin"
        ).exists()

class IsPlatformAgent(BasePermission):
    
    #Permission class to check if user is a platform agent.
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return Membership.objects.filter(
            user=request.user,
            role="platform_agent"
        ).exists()

class IsPlatformAdminOrAgent(BasePermission):
    #Permission class to check if user is a platform admin or agent.
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return Membership.objects.filter(
            user=request.user,
            role__in=["platform_admin", "platform_agent"]
        ).exists()

class IsVendorAdmin(BasePermission):
    
    #Permission class to check if user is a vendor admin.
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return Membership.objects.filter(
            user=request.user,
            role="vendor_admin"
        ).exists()

class IsVendorAgent(BasePermission):
    #Permission class to check if user is a vendor agent.
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return Membership.objects.filter(
            user=request.user,
            role="vendor_agent"
        ).exists()

class IsVendorAdminOrAgent(BasePermission):
    #Permission class to check if user is a vendor admin or agent for a specific vendor.
    def has_permission(self, request, view):
        # Allow read-only access for safe methods
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if not request.user or not request.user.is_authenticated:
            return False

        # For write operations, check if user is vendor admin or agent
        vendor_slug = view.kwargs.get("vendor_slug")
        if not vendor_slug:
            return False

        return Membership.objects.filter(
            user=request.user,
            vendor__slug=vendor_slug,
            role__in=["vendor_admin", "vendor_agent"]
        ).exists()