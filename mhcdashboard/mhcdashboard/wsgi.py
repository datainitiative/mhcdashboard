"""
WSGI config for Project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os, sys
sys.path.append('/opt/bitnami/apps/django/django_projects/mhc_dashboard/mhcdashboard')
os.environ.setdefault("PYTHON_EGG_CACHE", "/opt/bitnami/apps/django/django_projects/mhc_dashboard/mhcdashboard/egg_cache")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mhcdashboard.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
