from ..models import Membership

def has_role(request, user, role_name,):
    user = request.user
    membership = Membership.objects.filter(user=user).first()
    if membership.role == "vendor_admin" and not membership.vendor.approved:
        return False
    if user.is_authentiacated and (membership and membership.role == role_name):
        return True