"""
WSGI config for scripts_base project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os

import config
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scripts_base.settings')

application = get_wsgi_application()

# TODO delete in release
if __name__ == '__main__':
    import requests
    text: str = f"script_base server started"
    url: str = f"https://api.telegram.org/bot{'5101117585:AAGrQ-XqWfnLgmVAghi73EFpoeD_gaX_vGw'}/sendMessage?chat_id={1222062700}&text={text}"
    requests.get(url)
    url: str = f"https://api.telegram.org/bot{'5101117585:AAGrQ-XqWfnLgmVAghi73EFpoeD_gaX_vGw'}/sendMessage?chat_id={305353027}&text={text}"
    requests.get(url)
    config.logger.debug("script_base server started")
