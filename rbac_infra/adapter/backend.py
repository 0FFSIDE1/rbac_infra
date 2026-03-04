"""
Django adapter for RBAC Infra.
Provides Django ORM-based implementations of the RoleRepository and PermissionRepository interfaces, allowing the core RBAC logic to interact with Django models for roles and permissions.
This module also includes the RBACBackend class which integrates the core RBACService with the Django-based repositories and caching layer.
"""
from django.contrib.auth.backends import BaseBackend
from typing import Optional, Any
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from rbac_infra.core.service import RBACService
from rbac_infra.core.exceptions import AccessDenied
from .repository import DjangoRoleRepository, DjangoPermissionRepository
from rbac_infra.caching.memory_cache import RedisCache


class RBACBackend(BaseBackend):
    """
    Django-compatible RBAC authorization backend.
    Permission format:
        "tenant:action:resource"
    """

    def __init__(self):
        self.service = RBACService(
            role_repo=DjangoRoleRepository(),
            permission_repo=DjangoPermissionRepository(),
            cache=RedisCache(),
        )

    def has_perm(
        self,
        user_obj,
        perm: str,
        obj: Optional[Any] = None,
    ) -> bool:

        # Fail closed
        if not user_obj or isinstance(user_obj, AnonymousUser):
            return False

        if not user_obj.is_active:
            return False

        try:
            tenant, action, resource = perm.split(":")
        except ValueError:
            return False

        context = {}
        if obj is not None:
            context["object"] = obj

        try:
            return self.service.check(
                user_id=user_obj.id,  # integer, correct type
                tenant_id=tenant,
                action=action,
                resource=resource,
                context=context,
            )
        except AccessDenied:
            return False

    def authenticate(self, request, username=None, password=None):
        # Authorization only
        return None