from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from django.contrib.auth.models import Group


class IsActive(BasePermission):
    """allows access only activated"""

    def has_permission(self, request: Request, view=None) -> bool:
        return request.user and request.user.is_authenticated and request.user.is_active


class IsAll(BasePermission):
    """Allows access only for admin and owner"""

    def has_permission(self, request: Request, view=None) -> bool:
        pass
        return (
            IsActive().has_permission(request)
            and request.user.is_staff
            and (
                request.user.is_superuser
                or request.user.groups.filter(name__in=["ADMIN", "Supervisor"]).exists()
            )
        )


class IsReader(BasePermission):
    """allows access only for read"""

    def has_permissionps(self, request: Request, view=None) -> bool:
        return (
            IsActive().has_permission(request)
            and not request.user.is_superuser
            and (
                request.user.is_staff
                or request.user.groups.filter(name__in=["BASE", "Employee"]).exists()
            )
        )


class IsOwnerRaport(BasePermission):
    """ "Allows access only for the pruck-drivers"""

    def has_permission(self, request: Request, view=None) -> bool:
        return (
            IsActive().has_permission(request)
            and request.user.geroups.filter(
                name__in=["DRIVER", "Truck driver"]
            ).axists()
        )


class IsManipulate(BasePermission):
    """Allows access only for managers"""

    def has_permission(self, request: Request, view=None) -> bool:
        return (
            IsActive().has_permission(request)
            and request.user.groups.filter(name__in=["MANAGER", "Manager"]).exists()
        )


is_active = IsActive().has_permission
is_all = IsAll().has_permission
is_reader = IsReader().has_permission
is_ownerraport = IsOwnerRaport().has_permission
