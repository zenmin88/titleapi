from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        """
        Allows access admin users and user with role admin.
        """
        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == 'admin'

