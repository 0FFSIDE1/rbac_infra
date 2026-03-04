"""
Core interfaces for RBAC system.
Defines the abstract base classes for repositories and services used in the RBAC system.
These interfaces allow for decoupling the core logic from specific implementations, such as Django ORM or in-memory caching.
"""
from abc import ABC, abstractmethod
from typing import List, Dict
from .entities import Permission

class RoleRepository(ABC):

    @abstractmethod
    def get_user_roles(self, user_id: str, tenant_id: str) -> List[str]:
        pass


class PermissionRepository(ABC):

    @abstractmethod
    def get_role_permissions(self, role_name: str, tenant_id: str) -> List[Permission]:
        pass


class Policy(ABC):

    @abstractmethod
    def evaluate(
        self,
        user_id: str,
        action: str,
        resource: str,
        context: Dict
    ) -> bool:
        pass