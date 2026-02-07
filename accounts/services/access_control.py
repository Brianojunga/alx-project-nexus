from ..models import Membership
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied, ValidationError

def make_agent(user, pk, user_role):
    admin_membership = get_object_or_404(
        Membership,
        user = user,
        role = user_role
    )

    member_to_update = get_object_or_404(
        Membership,
        user__id = pk
    )

    if member_to_update.user == user:
        raise ValidationError("Cannot modify your own role.")
    if member_to_update.role == "vendor_agent":
        raise ValidationError("User already has this role.")
    
    if admin_membership.role != "platform_admin": 
        if not admin_membership.vendor:
            raise ValidationError("Admin user must be associated with a vendor.")

        if member_to_update.vendor and member_to_update.vendor != admin_membership.vendor:
            raise PermissionDenied(
                "Cannot modify members from a different vendor organization."
            )
        
        member_to_update.role = "vendor_agent"
        member_to_update.vendor = admin_membership.vendor
        member_to_update.save()
        return member_to_update

    if member_to_update.role == "vendor_admin":
        raise ValidationError("Cannot modify role vendor admin")
    
    member_to_update.role = "platform_agent"
    member_to_update.vendor = None
    member_to_update.save()
    return member_to_update



def remove_agent(user, pk, user_role):
    admin_membership = get_object_or_404(
        Membership,
        user = user,
        role = user_role
    )

    member_to_update = get_object_or_404(
        Membership,
        user__id = pk
    )

    if member_to_update.user == user:
        raise ValidationError("Cannot modify your own role.")
    if member_to_update.role != "vendor_agent" and member_to_update.role != "platform_agent":
        raise ValidationError("User is not an agent.")
    
    if admin_membership.role != "platform_admin": 
        if not admin_membership.vendor:
            raise ValidationError("Admin user must be associated with a vendor.")

        if member_to_update.vendor and member_to_update.vendor != admin_membership.vendor:
            raise PermissionDenied(
                "Cannot modify members from a different vendor organization."
            )
        
        member_to_update.role = "user"
        member_to_update.vendor = None
        member_to_update.save()
        return member_to_update

    member_to_update.role = "user"
    member_to_update.vendor = None
    member_to_update.save()
    return member_to_update



 
    


