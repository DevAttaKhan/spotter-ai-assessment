import os

from django.core.exceptions import ImproperlyConfigured
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

_debug = os.environ.get("DJANGO_DEBUG", "true").lower() == "true"
_secret = os.environ.get("DJANGO_SECRET_KEY", "")
if not _debug and _secret in ("", "dev-only-change-me"):
    raise ImproperlyConfigured("Set DJANGO_SECRET_KEY before running with DJANGO_DEBUG=false.")
