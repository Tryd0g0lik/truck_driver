import logging
import subprocess

from django.core.management.base import BaseCommand, CommandError

from logs import configure_logging

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            subprocess.run(
                ["daphne", "-b", "0.0.0.0", "-p", "8000", "project.asgi:application"],
                check=True,
            )
        except Exception as error:
            log.error(f"SERVER: {error.args[0]}")
