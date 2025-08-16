import os

from django.shortcuts import render
from django.http import HttpResponse
from project.settings import BASE_DIR


def main_views(request: type(HttpResponse)) -> type(render):
    """
    Here is opening the main page of service.
    :param request:
    :return:
    """
    files = []
    # GET JS FILES FOR LOGIN AND REGISTER PAGES
    # if "login" in request.path.lower() or "register" in request.path.lower():
    files = os.listdir(f"{BASE_DIR}/collectstatic/scripts")
    files = ["scripts/" + file for file in files]
    return render(request, "layout/index.html", {"js_files": files})
