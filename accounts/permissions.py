from rest_framework.permissions import BasePermission
from .models import User


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.role == User.Role.ADMIN or request.user.is_superuser)
        )


class IsStaffRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.role in [User.Role.STAFF, User.Role.ADMIN]
                or request.user.is_superuser
            )
        )


class IsCustomerRole(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.CUSTOMER
        )