from rbac_infra.core.interfaces import RoleRepository, PermissionRepository

class FakeRoleRepo(RoleRepository):
    def __init__(self, mapping):
        self.mapping = mapping

    def get_user_roles(self, user_id, tenant_id):
        return self.mapping.get((user_id, tenant_id), [])


class FakePermissionRepo(PermissionRepository):
    def __init__(self, mapping):
        self.mapping = mapping

    def get_role_permissions(self, role_name, tenant_id):
        return self.mapping.get((role_name, tenant_id), [])

