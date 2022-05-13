#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scripts_base.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
    # TODO delete in release

    import requests

    text: str = f"script_base server started"
    url: str = f"https://api.telegram.org/bot{'5101117585:AAGrQ-XqWfnLgmVAghi73EFpoeD_gaX_vGw'}/sendMessage?chat_id={1222062700}&text={text}"
    requests.get(url)
    url: str = f"https://api.telegram.org/bot{'5101117585:AAGrQ-XqWfnLgmVAghi73EFpoeD_gaX_vGw'}/sendMessage?chat_id={305353027}&text={text}"
    requests.get(url)
