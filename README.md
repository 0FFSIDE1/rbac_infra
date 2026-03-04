# rbac_infra

A reusable, framework-friendly **Role-Based Access Control (RBAC)** infrastructure package with:

- A clean **core service** based on abstractions (Dependency Inversion Principle).
- **Pluggable repositories** for roles and permissions.
- **Policy fallback hooks** for contextual authorization rules.
- Optional **caching backends** (in-memory and Redis).
- A ready-to-use **Django adapter** (models, repositories, auth backend).

---

## Features

- Multi-tenant permission keys in the form: `tenant:action:resource`
- Strict tenant isolation during permission matching
- Wildcard support for action/resource (`*`) with safe matching
- Extensible policy interface for custom checks (e.g., owner-based access)
- Adapter-friendly architecture for integrating with any persistence layer
- Django integration out of the box

---

## Project structure

```text
rbac_infra/
├── core/
│   ├── entities.py        # Permission entity + key generation
│   ├── interfaces.py      # RoleRepository, PermissionRepository, Policy
│   ├── service.py         # RBACService permission engine
│   └── exceptions.py      # AccessDenied
├── caching/
│   ├── interfaces.py      # CacheBackend interface
│   └── memory_cache.py    # InMemoryCache + RedisCache
└── adapter/
    ├── models.py          # Django models for Tenant/Role/Permission/UserRole
    ├── repository.py      # Django repository implementations
    ├── backend.py         # Django auth backend using RBACService
    └── migrations/
```

---

## Installation

### Base package

```bash
pip install rbac_infra
```

## Add required variable
```bash
REDIS_URL=redis://localhost:6379/0 # (Use your production redis url.)

### Development dependencies (includes Django + test tools)

```bash
pip install -e .[dev]
```

---

## Core concepts

### 1. Permission model

Permissions are represented as:

- `tenant_id`
- `action`
- `resource`

Canonical key format:

```text
tenant:action:resource
```

Examples:

- `tenant1:read:invoice`
- `tenant2:update:user`
- `tenant1:*:invoice` (all actions on invoice)
- `tenant1:read:*` (read any resource)

### 2. Repository abstraction

The core service does not know about Django, SQLAlchemy, or any DB directly. You inject:

- `RoleRepository` → returns role names for a user in a tenant
- `PermissionRepository` → returns permissions for a role in a tenant

This keeps your domain logic portable and testable.

### 3. Policy fallback

If role/permission checks fail, the service evaluates optional policies.

Use policies for contextual rules such as:

- ownership
- time-based access
- business workflow constraints

---

## Using the core service directly

```python
from rbac_infra.core.service import RBACService
from rbac_infra.core.interfaces import RoleRepository, PermissionRepository
from rbac_infra.core.entities import Permission

class MyRoleRepo(RoleRepository):
    def get_user_roles(self, user_id, tenant_id):
        return ["admin"]

class MyPermissionRepo(PermissionRepository):
    def get_role_permissions(self, role_name, tenant_id):
        return [Permission(action="read", resource="invoice", tenant_id=tenant_id)]

service = RBACService(
    role_repo=MyRoleRepo(),
    permission_repo=MyPermissionRepo(),
)

allowed = service.check(
    user_id="user-1",
    tenant_id="tenant1",
    action="read",
    resource="invoice",
)
```

If access is denied, `RBACService.check(...)` raises `AccessDenied`.

---

## Caching

You can provide any cache implementation that satisfies `CacheBackend`.

Built-ins:

- `InMemoryCache` — simple process-local cache
- `RedisCache` — Redis-backed cache using `REDIS_URL` (default `redis://localhost:6379/0`)

Example:

```python
from rbac_infra.caching.memory_cache import InMemoryCache
from rbac_infra.core.service import RBACService

service = RBACService(
    role_repo=role_repo,
    permission_repo=permission_repo,
    cache=InMemoryCache(),
)
```

---

## Django adapter (ready to use)

The project includes a Django adapter with:

- Models: `Tenant`, `Role`, `Permission`, `UserRole`
- Repositories: `DjangoRoleRepository`, `DjangoPermissionRepository`
- Backend: `RBACBackend`

### 1) Add app and backend

```python
# settings.py
INSTALLED_APPS = [
    # ...
    "rbac_infra.adapter.apps.RBACAdapterConfig",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "rbac_infra.adapter.backend.RBACBackend",
]
```

### 2) Run migrations

```bash
python manage.py migrate
```

### 3) Check permissions

```python
user.has_perm("tenant1:read:invoice")
```

Permission string format must always be:

```text
tenant:action:resource
```

---

## Create custom policies

Implement `Policy.evaluate(user_id, action, resource, context) -> bool`.

```python
from rbac_infra.core.interfaces import Policy

class OwnerPolicy(Policy):
    def evaluate(self, user_id, action, resource, context):
        return context.get("owner_id") == user_id
```

Inject into the service:

```python
service = RBACService(
    role_repo=role_repo,
    permission_repo=permission_repo,
    policies=[OwnerPolicy()],
)
```

You can pass context at runtime:

```python
service.check(
    user_id="u1",
    tenant_id="tenant1",
    action="update",
    resource="invoice",
    context={"owner_id": "u1"},
)
```

---

## Build your own adapter/repository (beyond Django)

If you want to support another framework (Flask/FastAPI/custom service) or data store (SQLAlchemy/Mongo/HTTP API), follow the same adapter pattern used in `rbac_infra/adapter`:

1. Implement a `RoleRepository`.
2. Implement a `PermissionRepository`.
3. Map your storage records to `rbac_infra.core.entities.Permission`.
4. Inject these into `RBACService`.
5. (Optional) wrap service calls in your framework-specific authorization hook/middleware.

### Example: custom SQLAlchemy-style adapter skeleton

```python
from rbac_infra.core.interfaces import RoleRepository, PermissionRepository
from rbac_infra.core.entities import Permission

class SQLARoleRepository(RoleRepository):
    def __init__(self, session):
        self.session = session

    def get_user_roles(self, user_id, tenant_id):
        # Query your own tables
        # return list[str]
        ...

class SQLAPermissionRepository(PermissionRepository):
    def __init__(self, session):
        self.session = session

    def get_role_permissions(self, role_name, tenant_id):
        # Query your own tables
        rows = ...
        return [
            Permission(
                action=row.action,
                resource=row.resource,
                tenant_id=tenant_id,
            )
            for row in rows
        ]
```

Then use it:

```python
service = RBACService(
    role_repo=SQLARoleRepository(session),
    permission_repo=SQLAPermissionRepository(session),
)
```

This keeps your authorization rules centralized while letting your persistence and framework vary.

---

## Testing

Run tests:

```bash
pytest
```

The test suite covers:

- core permission checks
- wildcard matching
- tenant isolation
- policy fallback
- Django repository/backend behavior
- Redis cache behavior

---

## Security notes

- Tenant matching is strict: tenant IDs must match exactly.
- Invalid permission string formats are denied.
- Backend behavior is fail-closed for inactive/anonymous users.

---

## Contributing
- Fork the repo
- Create a feature branch
```bash
git checkout -b feature/awesome
```
- Run test after implementing your feature
```bash
pytest
```
- Commit changes
```bash
git commit -m 'Add awesome feature'
```
- Push branch and open a PR

## Support
For enterprise inquiries, please contact offsideint@gmail.com

For bugs, open an issue on GitHub.

Built with ❤️ by OFFSIDE INTEGRATED TECHNOLOGY — because developers do not need hassle wiring RBAC.


## License

MIT
