from rbac_infra.core.interfaces import Policy
from rbac_infra.core.service import RBACService
import pytest
from rbac_infra.core.exceptions import AccessDenied
from tests.utils.fakes import FakeRoleRepo, FakePermissionRepo

class OwnerPolicy(Policy):
    def evaluate(self, user_id, action, resource, context):
        return context.get("owner_id") == user_id


def test_owner_policy_allows():
    service = RBACService(
        FakeRoleRepo({}),
        FakePermissionRepo({}),
        policies=[OwnerPolicy()]
    )

    assert service.check(
        "user1",
        "tenant1",
        "update",
        "invoice",
        context={"owner_id": "user1"}
    )


def test_owner_policy_denies():
    service = RBACService(
        FakeRoleRepo({}),
        FakePermissionRepo({}),
        policies=[OwnerPolicy()]
    )

    

    with pytest.raises(AccessDenied):
        service.check(
            "user1",
            "tenant1",
            "update",
            "invoice",
            context={"owner_id": "user2"}
        )