from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access admin users and user with role admin.
    """
    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False
        return request.user.is_superuser or request.user.role == 'admin'


class IsModeratorRole(BasePermission):
    """
    Allows access users with role='moderator'.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == 'moderator'


class IsAdminOrModeratorOrAuthor(BasePermission):
    """
    Permission on object level.Allows access
    admin, moderator and author of object.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser or request.user.role == 'admin':
            return True
        if request.user.role == 'moderator':
            return True
        return obj.author == request.user
