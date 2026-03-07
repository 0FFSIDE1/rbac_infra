import pytest
from django.contrib.auth.models import User
# from django.test import override_settings

from rbac_infra.adapter.backend import RBACBackend
from rbac_infra.adapter.models import Tenant, Role, Permission, UserRole
from rbac_infra.caching.memory_cache import RedisCache


@pytest.mark.django_db
def test_backend_grants_permission():
    user = User.objects.create(username="john")
    tenant = Tenant.objects.create(name="tenant1")

    role = Role.objects.create(name="admin", tenant=tenant)
    Permission.objects.create(
        role=role,
        action="read",
        resource="invoice",
        tenant=tenant,
    )
    UserRole.objects.create(user=user, role=role)

    backend = RBACBackend()

    assert backend.has_perm(
        user,
        "tenant1:read:invoice"
    )


@pytest.mark.django_db
def test_backend_denies_permission():
    user = User.objects.create(username="john")
    tenant = Tenant.objects.create(name="tenant1")

    role = Role.objects.create(name="viewer", tenant=tenant)
    Permission.objects.create(
        role=role,
        action="read",
        resource="invoice",
        tenant=tenant,
    )
    UserRole.objects.create(user=user, role=role)

    backend = RBACBackend()

    assert not backend.has_perm(
        user,
        "tenant1:delete:invoice"
    )


@pytest.mark.django_db
def test_backend_cross_tenant_denied():
    user = User.objects.create(username="john")
    tenant1 = Tenant.objects.create(name="tenant1")
    tenant2 = Tenant.objects.create(name="tenant2")

    role = Role.objects.create(name="admin", tenant=tenant1)
    Permission.objects.create(
        role=role,
        action="read",
        resource="invoice",
        tenant=tenant1,
    )
    UserRole.objects.create(user=user, role=role)

    backend = RBACBackend()

    assert not backend.has_perm(
        user,
        "tenant2:read:invoice"
    )


@pytest.mark.django_db
def test_backend_invalid_permission_string():
    user = User.objects.create(username="john")

    backend = RBACBackend()

    # malformed string
    assert not backend.has_perm(user, "invalid-format")


@pytest.mark.django_db
def test_backend_uses_redis_cache(monkeypatch):
    user = User.objects.create(username="john")
    tenant = Tenant.objects.create(name="tenant1")

    role = Role.objects.create(name="admin", tenant=tenant)
    Permission.objects.create(
        role=role,
        action="read",
        resource="invoice",
        tenant=tenant,
    )
    UserRole.objects.create(user=user, role=role)

    cache = RedisCache()
    backend = RBACBackend()
    backend.service.cache = cache  # inject test cache

    # First call — should compute and cache
    assert backend.has_perm(user, "tenant1:read:invoice")

    cache_key = f"rbac:tenant1:read:invoice:{user.id}"
    assert cache.get(cache_key) is True

    # Now delete permission from DB
    Permission.objects.all().delete()

    # Second call — should still return True from cache
    assert backend.has_perm(user, "tenant1:read:invoice")


@pytest.mark.django_db
def test_wildcard_grants_permission():
    user = User.objects.create(username="john")
    tenant = Tenant.objects.create(name="tenant1")

    role = Role.objects.create(name="admin", tenant=tenant)
    Permission.objects.create(
        role=role,
        action="*",
        resource="*",
        tenant=tenant,
    )
    UserRole.objects.create(user=user, role=role)

    backend = RBACBackend()

    assert backend.has_perm(
        user,
        "tenant1:invite:user"
    )