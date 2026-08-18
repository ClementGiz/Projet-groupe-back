from rest_framework.permissions import BasePermission
from .models import User

class IsAdminUserRole(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )

class IsFormateurRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.Role.FORMATEUR or request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )

class IsRefAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.role == User.Role.REF or request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )