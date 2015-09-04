"""
WSGI config for pawseyportal project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

from django.core.handlers.wsgi import WSGIHandler
import os
import django

webapp_root = os.path.dirname(os.path.abspath(__file__))

class WSGIEnvironment(WSGIHandler):

    def __call__(self, environ, start_response):

        os.environ['SCRIPT_NAME'] = environ['SCRIPT_NAME']
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawseyportal.settings")
        os.environ['HTTPS'] = "on"
        django.setup()
        return super(WSGIEnvironment, self).__call__(environ, start_response)

application = WSGIEnvironment()
