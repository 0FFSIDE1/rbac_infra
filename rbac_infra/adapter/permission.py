from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from .models import UserRole, Tenant


class RBACPermission(BasePermission):

    action = None
    resource = None

    def resolve_tenant(self, user):
        try:
            return Tenant.objects.get(name=user.username)
        except Tenant.DoesNotExist:
            user_role = (
                UserRole.objects
                .filter(user=user)
                .select_related("role__tenant")
                .first()
            )

            if user_role:
                return user_role.role.tenant

        raise PermissionDenied("User has no tenant assigned")

    def has_permission(self, request, view):

        if not request.user or not request.user.is_authenticated:
            return False

        tenant = self.resolve_tenant(request.user)

        request.tenant = tenant

        perm_string = f"{tenant.name}:{self.action}:{self.resource}"

        # CRITICAL: return explicit boolean
        return bool(request.user.has_perm(perm_string))