from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):

    def has_permission(self, request, view):
        print(f'{view=}')
        return request.user.is_superuser or request.user.role == 'admin'

