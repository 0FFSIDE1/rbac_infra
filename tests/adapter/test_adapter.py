import pytest
from rbac_infra.caching.memory_cache import RedisCache


def test_redis_set_get(monkeypatch):

    store = {}

    class FakeRedis:
        def get(self, key):
            return store.get(key)

        def setex(self, key, ttl, value):
            store[key] = value

    monkeypatch.setattr(
        "rbac_infra.caching.memory_cache.redis.Redis.from_url",
        lambda url: FakeRedis()
    )

    cache = RedisCache()

    cache.set("key", True, 60)
    assert cache.get("key") is True


@pytest.mark.django_db
def test_django_role_repository():
    from django.contrib.auth.models import User
    from rbac_infra.adapter.models import Tenant, Role, UserRole
    from rbac_infra.adapter.repository import DjangoRoleRepository

    user = User.objects.create(username="u")
    tenant = Tenant.objects.create(name="t")
    role = Role.objects.create(name="admin", tenant=tenant)

    UserRole.objects.create(user=user, role=role)

    repo = DjangoRoleRepository()

    roles = repo.get_user_roles(user.id, tenant.name)

    assert "admin" in roles