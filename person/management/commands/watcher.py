"""
person/management/commands/watcher.py
"""

import logging
import os
import subprocess
import sys

from django.core.management.base import BaseCommand
from watchfiles import watch, BaseFilter

from project.settings import BASE_DIR


class Command(BaseCommand, BaseFilter):
    def handle(self, *args, **options):
        self.ignore_dirs = (
            "nginx",
            "media",
            "img",
            ".github",
            "__tests__",
            "bundles",
            "__pycache__",
            "collectstatic",
            "static",
            "project",
        )
        logging.info(BASE_DIR)

        for changes in watch("person"):
            port = 8000
            if self.server_stop(port) and changes:
                self.stdout.write(
                    self.style.SUCCESS(f"Остановлен сервер на порту {port}")
                )

                python_executable = sys.executable
                manage_py_path = os.path.join(BASE_DIR, "manage.py")

                cmd = f'"{python_executable}" "{manage_py_path}" server  0.0.0.0:8000'
                subprocess.Popen(
                    cmd, shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE
                )

            else:
                self.stdout.write(
                    self.style.WARNING(f"Сервер на порту {port} не найден")
                )
            print(f"{BASE_DIR}\\manage.py")

            # os.execvp(f"{BASE_DIR}\\server.sh", args=["python", f"{BASE_DIR}\\manage.py", "server"])

    def server_stop(self, port):
        result = subprocess.run(
            ["netstat", "-ano", "|", "findstr", f":{port}"],
            shell=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if "LISTENING" in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(["taskkill", "/PID", pid, "/F"])
            return True
        else:
            return False
