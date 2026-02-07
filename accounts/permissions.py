from rest_framework.permissions import BasePermission
from accounts.services.has_role import has_role
from accounts.models import Membership
from rest_framework.permissions import SAFE_METHODS
    
class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return has_role(request, user, "platform_admin")
    
class IsVendorAdmin(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return has_role(request, user, "vendor_admin")


class IsPlatformAgent(BasePermission):
    def has_permission(self, request, view):
        pass

class IsVendorAgent(BasePermission):
    def has_permission(self, request, view):
        pass


class IsVendorAdminOrAgent(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        return Membership.objects.filter(
            user=request.user,
            vendor__slug=view.kwargs["vendor_slug"],
            role__in=["vendor_admin", "vendor_agent"]
        ).exists()