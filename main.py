import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrms.settings')

from django.core.asgi import get_asgi_application

app = get_asgi_application()
