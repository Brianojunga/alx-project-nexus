from rest_framework.permissions import BasePermission
from accounts.services.has_role import has_role
    
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