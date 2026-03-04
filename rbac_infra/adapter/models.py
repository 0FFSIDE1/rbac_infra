"""
This module defines the Django models for the RBAC infrastructure. It includes models for tenants, roles, permissions, and the relationships between them. The models are designed to support multi-tenancy and to allow for efficient querying of user roles and permissions within a specific tenant context.
"""
from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Role(models.Model):
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "tenant")

class Permission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    action = models.CharField(max_length=100)
    resource = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="permissions")

    class Meta:
        unique_together = (
            "role",
            "action",
            "resource",
            "tenant",
        )

    def key(self):
        return f"{self.tenant.name}:{self.action}:{self.resource}"

class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

class UserRole(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)