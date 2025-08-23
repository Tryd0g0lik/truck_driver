from rest_framework.permissions import BasePermission
from django.contrib.auth.models import Group


class IsAll(BasePermission):
    """Allows access only to owners"""

    def has_permission(self, request, views=None):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and (
                request.user.is_staff
                or request.user.is_superuser
                or request.user.groups.filter(name__in=["ADMIN", "Supervisor"]).exists()
            )
        )


class IsReader(BasePermission):
    """Allows access only to reade"""

    def has_permission(self, request, view=None):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and not request.user.is_superuser
            and (
                request.user.is_staff
                or request.user.groups.filter(name__in=["BASE", "Employee"]).exists()
            )
        )


class IsOwnerRapport(BasePermission):
    """Allows access only for the truck driver"""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and (
                request.user.is_staff
                or request.user.groups.filter(
                    name__in=["DRIVER", "Truck driver"]
                ).exists()
            )
        )


class IsManipulate(BasePermission):
    """Allows access only for the managers"""

    def has_permission(self, request, view=None):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and request.user.groups.filter(name__in=["MANAGER", "Manager"]).exists()
        )
