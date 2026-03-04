from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "test-secret-key")
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "rbac_infra.adapter.apps.RBACAdapterConfig",
]

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

MIDDLEWARE = []


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

USE_TZ = True

