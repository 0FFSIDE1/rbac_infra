import pytest
from rbac_infra.core.service import RBACService
from rbac_infra.core.entities import Permission
from .utils.fakes import FakeRoleRepo, FakePermissionRepo


@pytest.fixture
def basic_setup():
    role_map = {
        ("user1", "tenant1"): ["admin"],
    }

    perm_map = {
        ("admin", "tenant1"): [
            Permission(action="read", resource="invoice", tenant_id="tenant1")
        ]
    }

    service = RBACService(
        FakeRoleRepo(role_map),
        FakePermissionRepo(perm_map),
    )

    return service