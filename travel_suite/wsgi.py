"""
WSGI config for travel_suite project.
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_suite.settings')

application = get_wsgi_application()

