"""
This module defines the Django models for the RBAC infrastructure. It includes models for tenants, roles, permissions, and the relationships between them. The models are designed to support multi-tenancy and to allow for efficient querying of user roles and permissions within a specific tenant context.
"""
from django.db import models

class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    


class Role(models.Model):
    name = models.CharField(max_length=100)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["id", "tenant"],
                name="unique_role_tenant_pair"
            ),
            models.UniqueConstraint(
                fields=["name", "tenant"],
                name="unique_role_name_per_tenant"
            ),
        ]
    
    def __str__(self):
        return f"{self.name}:{self.tenant}"
    

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

    def __str__(self):
        return f"{self.role}:{self.action}:{self.resource}:{self.tenant}"
    

class UserRole(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE, db_index=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, db_index=True)


    def clean(self):
        if self.role.tenant_id != self.tenant_id:
            raise ValidationError("Role tenant must match UserRole tenant")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "tenant"],
                name="unique_user_role_per_tenant"
            ),
            models.UniqueConstraint(
                fields=["role", "tenant"],
                name="role_must_match_tenant"
            ),
        ]

    def __str__(self):
        return f"{self.user}:{self.role}"
    