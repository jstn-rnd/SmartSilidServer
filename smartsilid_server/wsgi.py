"""
WSGI config for smartsilid_server project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import os
import pythoncom
from django.core.wsgi import get_wsgi_application
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsilid_server.settings')
pythoncom.CoInitialize()

application = get_wsgi_application()
