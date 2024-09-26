"""
ASGI config for smartsilid_server project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import pythoncom
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsilid_server.settings')
pythoncom.CoInitialize()
application = get_asgi_application()
