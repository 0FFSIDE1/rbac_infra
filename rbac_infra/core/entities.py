"""
Core entities for RBAC system.
Defines the main data structures used in the RBAC system, such as Role and Permission.
These are simple data classes that represent the core concepts of roles and permissions.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Role:
    name: str

@dataclass(frozen=True)
class Permission:
    action: str
    resource: str
    tenant_id: str

    def key(self) -> str:
        return f"{self.tenant_id}:{self.action}:{self.resource}"