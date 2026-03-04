import pytest
from rbac_infra.core.exceptions import AccessDenied
from rbac_infra.core.entities import Permission
from rbac_infra.core.service import RBACService
from tests.utils.fakes import FakeRoleRepo, FakePermissionRepo

def test_user_has_permission(basic_setup):
    assert basic_setup.check(
        user_id="user1",
        tenant_id="tenant1",
        action="read",
        resource="invoice"
    )

def test_user_without_permission_denied(basic_setup):
    with pytest.raises(AccessDenied):
        basic_setup.check(
            user_id="user1",
            tenant_id="tenant1",
            action="delete",
            resource="invoice"
        )

def test_cross_tenant_denied():

    role_map = {
        ("user1", "tenant1"): ["admin"],
    }

    perm_map = {
        ("admin", "tenant1"): [
            Permission("read", "invoice", "tenant1")
        ]
    }

    service = RBACService(
        role_repo=FakeRoleRepo(role_map),
        permission_repo=FakePermissionRepo(perm_map),
    )

    with pytest.raises(AccessDenied):
        service.check(
            user_id="user1",
            tenant_id="tenant2",
            action="read",
            resource="invoice"
        )

def test_action_wildcard():

    role_map = {
        ("user1", "tenant1"): ["admin"],
    }

    perm_map = {
        ("admin", "tenant1"): [
            Permission("*", "invoice", "tenant1")
        ]
    }

    service = RBACService(
        FakeRoleRepo(role_map),
        FakePermissionRepo(perm_map),
    )

    assert service.check(
        "user1", "tenant1", "delete", "invoice"
    )


def test_resource_wildcard():
    role_map = {
        ("user1", "tenant1"): ["admin"],
    }

    perm_map = {
        ("admin", "tenant1"): [
            Permission("read", "*", "tenant1")
        ]
    }

    service = RBACService(
        FakeRoleRepo(role_map),
        FakePermissionRepo(perm_map),
    )

    assert service.check(
        "user1", "tenant1", "read", "invoice"
    )