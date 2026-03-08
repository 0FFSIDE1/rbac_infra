from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from .models import UserRole, Tenant


class RBACPermission(BasePermission):
    """
    Base RBAC permission class.
    Resolves tenant for owner or staff user.
    """

    action = None
    resource = None

    def resolve_tenant(self, user):
        """
        Resolve tenant for the authenticated user.

        Owner:
            username == tenant.name

        Staff:
            resolved via UserRole
        """

        # Owner case
        try:
            return Tenant.objects.get(name=user.username)
        except Tenant.DoesNotExist:
            pass

        # Staff case
        user_role = (
            UserRole.objects
            .select_related("tenant")
            .filter(user=user)
            .first()
        )

        if not user_role:
            raise PermissionDenied("User does not belong to any tenant")

        return user_role.tenant

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        tenant = self.resolve_tenant(request.user)

        # Attach tenant to request for views to reuse
        request.tenant = tenant

        perm_string = f"{tenant.name}:{self.action}:{self.resource}"

        return request.user.has_perm(perm_string)