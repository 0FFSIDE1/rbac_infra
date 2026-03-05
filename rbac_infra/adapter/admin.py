from django.contrib import admin
from rbac_infra.adapter.models import Tenant, Role, Permission, UserRole
# Register your models here.

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Columns in the list view
    search_fields = ('name',)  # Searchable fields

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'action', 'resource', 'tenant')  # Columns in the list view
    search_fields = ('role__name', 'action', 'resource')  # Searchable fields


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'tenant')  # Columns in the list view
    search_fields = ('name',)  # Searchable fields

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Columns in the list view
    search_fields = ('user__username', 'role__name')  # Searchable fields