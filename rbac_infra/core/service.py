"""
Core RBAC service implementation.
This module contains the main RBACService class which implements the core logic for checking permissions based on user roles and policies.
The service uses repositories to fetch roles and permissions, and supports caching for improved performance. It also includes a safe wildcard matching mechanism for permissions.
"""
from typing import Set, List, Optional
from .interfaces import RoleRepository, PermissionRepository
from .exceptions import AccessDenied
from rbac_infra.caching.interfaces import CacheBackend
from rbac_infra.caching.memory_cache import RedisCache

class RBACService:

    def __init__(
        self,
        role_repo,
        permission_repo,
        policies: Optional[List] = None,
        cache: Optional[CacheBackend] = None,
    ):
        if role_repo is None:
            raise ValueError("role_repo must be provided")

        if permission_repo is None:
            raise ValueError("permission_repo must be provided")

        self.role_repo = role_repo
        self.permission_repo = permission_repo
        self.policies = policies or []
        self.cache = cache

    def _match(self, requested: str, stored: str) -> bool:
        """
        Safe wildcard matching.
        Format: tenant:action:resource
        Supports '*' for action or resource only.
        Tenant must match exactly.
        """
        try:
            r_tenant, r_action, r_resource = requested.split(":")
            s_tenant, s_action, s_resource = stored.split(":")
        except ValueError:
            return False

        # Strict tenant isolation
        if r_tenant != s_tenant:
            return False

        action_match = (s_action == "*" or s_action == r_action)
        resource_match = (s_resource == "*" or s_resource == r_resource)

        return action_match and resource_match

    def check(self, user_id, tenant_id, action, resource, context=None):
        """
        Check if user has permission to perform action on resource within tenant.
        Context is passed to policies for additional checks.
        """

        context = context or {}

        permission_key = f"{tenant_id}:{action}:{resource}"
        cache_key = f"rbac:{permission_key}:{user_id}"

        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                if not cached:
                    raise AccessDenied("Access denied")
                return True

        roles = self.role_repo.get_user_roles(user_id, tenant_id)

        allowed = False

        for role in roles:
            perms = self.permission_repo.get_role_permissions(
                role, tenant_id
            )
            for perm in perms:
                if self._match(permission_key, perm.key()):
                    allowed = True
                    break
            if allowed:
                break

        # policy fallback
        if not allowed:
            for policy in self.policies:
                if policy.evaluate(user_id, action, resource, context):
                    allowed = True
                    break

        if self.cache:
            self.cache.set(cache_key, allowed, ttl=60)

        if not allowed:
            raise AccessDenied("Access denied")

        return True