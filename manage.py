#!/usr/bin/env python3.6
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    project_folder = os.path.expanduser('~/mysite')  # adjust as appropriate
    load_dotenv(os.path.join(project_folder, '.env'))
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
