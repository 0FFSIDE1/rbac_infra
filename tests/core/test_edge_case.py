import pytest
from rbac_infra.core.exceptions import AccessDenied
from rbac_infra.core.service import RBACService
from tests.utils.fakes import FakeRoleRepo, FakePermissionRepo

def test_no_roles():
    service = RBACService(
        FakeRoleRepo({}),
        FakePermissionRepo({}),
    )

    
    with pytest.raises(AccessDenied):
        service.check("u", "t", "a", "r")


def test_empty_permissions():
    role_map = {("u", "t"): ["admin"]}
    perm_map = {("admin", "t"): []}

    service = RBACService(
        FakeRoleRepo(role_map),
        FakePermissionRepo(perm_map),
    )

    with pytest.raises(AccessDenied):
        service.check("u", "t", "read", "invoice")
