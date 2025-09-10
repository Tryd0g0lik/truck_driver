"""
person/management/commands/server.py
"""

import logging
import subprocess


from django.core.management.base import BaseCommand
from logs import configure_logging
from project import settings

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class Command(BaseCommand):

    def handle(self, *args, **options):

        try:
            subprocess.run(
                [
                    "daphne",
                    "-b",
                    settings.ALLOWED_HOSTS[0],
                    "-p",
                    "8000",
                    "project.asgi:application",
                ],
            )
        except Exception as error:
            log.error(f"SERVER: {error.args[0]}")
