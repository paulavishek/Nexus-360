"""
ASGI config for project_chatbot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_chatbot.settings')

# Import Django ASGI application early to ensure setup
from django.core.asgi import get_asgi_application

# Initialize Django ASGI application early to populate AppRegistry before importing other code
django_asgi_app = get_asgi_application()

# Now import the rest (this ensures Django is set up before importing consumers)
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chatbot.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chatbot.routing.websocket_urlpatterns
        )
    ),
})
