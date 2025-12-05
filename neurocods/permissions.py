# myapp/permissions.py
from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """
    Custom permission to only allow superusers to access certain views.
    """

    def has_permission(self, request, _):
        return request.user.is_authenticated and request.user.is_superuser
