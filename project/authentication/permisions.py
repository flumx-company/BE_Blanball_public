from rest_framework import permissions
from rest_framework.request import Request


class IsNotAuthenticated(permissions.BasePermission):
    """allows access only to admin users"""

    def has_permission(self, request: Request, view) -> bool:
        if request.user.id is None:
            return True
