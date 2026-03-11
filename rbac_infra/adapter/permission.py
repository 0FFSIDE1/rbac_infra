from __future__ import annotations

from typing import Iterable
from rest_framework.permissions import BasePermission
from django.core.exceptions import PermissionDenied
from .models import UserRole
from django.core.cache import cache

class RBACPermission(BasePermission):
    """Tenant-aware, fail-closed permission checker with Redis-cached permissions."""

    action: str | None = None
    resource: str | None = None
    fallback_actions: Iterable[str] = ()

    def _resolve_user_role(self, user):
        return UserRole.objects.select_related("tenant", "role").filter(user=user).first()

    def _permission_cache_key(self, user_id: int, tenant_id: int) -> str:
        return f"perm:user:{user_id}:tenant:{tenant_id}"

    def _load_permissions(self, user_role):
        cache_key = self._permission_cache_key(user_role.user_id, user_role.tenant_id)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        perms = {
            f"{user_role.tenant.name}:{perm.action}:{perm.resource}"
            for perm in user_role.role.permissions.filter(tenant=user_role.tenant).only("action", "resource")
        }
        cache.set(cache_key, perms, timeout=300)
        return perms

    def _matches(self, permission_set: set[str], tenant_name: str, action: str, resource: str) -> bool:
        return (
            f"{tenant_name}:{action}:{resource}" in permission_set
            or f"{tenant_name}:*:*" in permission_set
            or f"{tenant_name}:*:{resource}" in permission_set
            or f"{tenant_name}:{action}:*" in permission_set
        )

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not self.action or not self.resource:
            return False

        user_role = self._resolve_user_role(user)
        if not user_role:
            return False

        request.tenant = user_role.tenant
        request.user_role = user_role

        permission_set = self._load_permissions(user_role)
        actions = [self.action, *list(self.fallback_actions)]
        return any(self._matches(permission_set, user_role.tenant.name, action, self.resource) for action in actions)
