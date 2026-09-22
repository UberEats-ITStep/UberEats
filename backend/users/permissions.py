from rest_framework.permissions import SAFE_METHODS, BasePermission
 
ADMIN_ROLES = frozenset({"ADMIN"})
 
 
def is_admin(user) -> bool:
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if not getattr(user, "is_active", False):
        return False
    if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
        return True
    role = getattr(user, "role", None)
    return isinstance(role, str) and role.strip().upper() in ADMIN_ROLES
 
 
class IsAdmin(BasePermission):
    """Administrators only, for every HTTP method."""
 
    message = "You do not have permission to perform this action."
 
    def has_permission(self, request, view):
        return is_admin(request.user)
 
 
class IsAdminOrReadOnly(BasePermission):
    """
    Public read, admin-only write. Use for the public catalog
    (categories, cuisines, menu items).
 
    Anonymous write attempts get 401, non-admin users get 403.
    """
 
    message = "Only administrators can modify catalog data."
 
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return is_admin(request.user)
 
 
class IsAdminOrAuthenticatedReadOnly(BasePermission):
    """
    Authenticated users may read (the view's queryset must still scope rows to
    the owner); only administrators may write.
    """
 
    message = "Only admins can update order status."
 
    def has_permission(self, request, view):
        user = request.user
        if not (user and user.is_authenticated):
            return False
        if request.method in SAFE_METHODS:
            return True
        return is_admin(user)
 