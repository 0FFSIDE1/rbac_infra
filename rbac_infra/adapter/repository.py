"""
Django adapter for RBAC Infra.
Provides Django ORM-based implementations of the RoleRepository and PermissionRepository interfaces, allowing the core RBAC logic to interact with Django models for roles and permissions.
This module also includes the RBACBackend class which integrates the core RBACService with the Django-based repositories and caching layer.
"""
from rbac_infra.core.interfaces import RoleRepository, PermissionRepository
from rbac_infra.core.entities import Permission as CorePermission
from .models import UserRole, RolePermission, Role, Permission


class DjangoRoleRepository(RoleRepository):
    """
    Fetches role names for a user within a specific tenant.
    """

    def get_user_roles(self, user_id, tenant_id):
        return list(
            Role.objects.filter(
                userrole__user_id=user_id,
                tenant__name=tenant_id,
            ).values_list("name", flat=True)
        )


class DjangoPermissionRepository(PermissionRepository):
    """
    Fetches permissions for a role within a specific tenant.
    """

    def get_role_permissions(self, role_name, tenant_id):
        qs = Permission.objects.filter(
            role__name=role_name,
            tenant__name=tenant_id,
        )

        return [
            CorePermission(
                action=p.action,
                resource=p.resource,
                tenant_id=p.tenant.name,
            )
            for p in qs
        ]