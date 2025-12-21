"""
__tests__/tests_person/test_user_inactive_valid.py
"""

import asyncio
import logging

import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from __tests__.__fixtures__.fix import (
    fix_del_user_of_db,
    fix_get_session,
    fix_get_user_of_db,
    fix_user_registration,
)
from logs import configure_logging
from person.models import Users
from person.views_api.redis_person import RedisOfPerson
from project.views import CSRFTokenView

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.mark.parametrize(
    "username, email, password, category, expected",
    [
        ("Serge", "serge@his.com", "123456789", "BASE", True),
        (" Serge_01 ", "serge@his.com", "123456%789", "BASE", True),
        (" Serge_03 ", "serge@his.com", "1234567dsq89", "BASE", True),
        (" Serge_04", "", "1234567dsq89", "BASE", True),
        ("Serge_02", "serge@his.com", "123456789", "BASE", True),
    ],
)
@pytest.mark.persone_inactive_valid
@pytest.mark.django_db
async def test_persone_inactive_valid(
    fix_get_user_of_db,
    fix_del_user_of_db,
    fix_get_session,
    fix_user_registration,
    username,
    email,
    password,
    category,
    expected,
):
    # from django.contrib.auth.forms import UserCreationForm
    from django import forms

    from person.views_api.users_views import UserViews

    log.info("====== BEFORE registration of user ======")
    factory = APIRequestFactory()
    await fix_user_registration(
        fix_get_session, factory, username, email, password, category, expected
    )
    # if not result:
    #     log.error("%s : %s & 'result' is: %s", (test_persone_inactive_valid.__name__, "ERROR => 'result' is invalid!", str(result)) )
    #     assert isinstance(result,  WSGIRequest)

    log.info("====== BEFORE csrf_response ======")
    request = factory.get("auth/csrftoken/")
    csrf_response = await CSRFTokenView().get(request)
    log.info("====== BEFORE decode the b-data to the 'utf-8' from JsonResponse======")
    csrf = b"".join(csrf_response._container).decode("utf-8")
    log.info("csrf_response: %s", (str(csrf_response.__dict__)))
    assert isinstance(csrf_response, JsonResponse)
    assert csrf_response.status_code == 200
    log.info("====== BEFORE a user login ======")
    request_login = factory.post(
        "/api/auth/person/0/active/", content_type="application/json"
    )
    log.info(request_login.__dict__.__str__())

    request_login.__setattr__("user", AnonymousUser())
    log.info(
        "'user' (%s) was added to the: %s"
        % (
            AnonymousUser(),
            request_login,
        )
    )
    log.info(" ====== BEFORE i will create FORM data  ====== ")

    class UserForm(forms.Form):
        username = forms.CharField()
        password = forms.CharField(widget=forms.PasswordInput())

    # form_data = UserCreationForm({"username": username, "password": password})
    form_data = UserForm({"username": username, "password": password})
    if form_data.is_valid():
        request_login.__setattr__("data", form_data.cleaned_data)
    log.info(" ===== GET FORM DATA IS: '%s' " % str(form_data.__dict__.__str__()))

    log.info(" ===== FORM DATA WAS ADDED To the request")
    response_login = await UserViews().active(request_login)
    assert isinstance(response_login, Response)
    assert response_login.status_code == 200
    assert len(csrf) > 5
    log.info(
        "%s: ACTIVE - 'csrf_response': %s"
        % (test_persone_inactive_valid.__name__, str(csrf_response.__dict__))
    )
    log.info("====== BEFORE include email: %s & username: %s ======", (email, username))
    response_id_list = await asyncio.to_thread(
        lambda: list(Users.objects.filter(email=email, username=username))
    )
    log.info(
        "====== BEFORE include len(response_id_list) %s ======",
        (len(response_id_list),),
    )
    assert len(response_id_list) > 0
    response_id = response_id_list[0]
    log.info("====== BEFORE include response_id %s ======", (str(response_id),))
    assert isinstance(response_id, int)
    log.info("====== BEFORE include factory.patch ======")
    request_include = factory.patch(f"/api/auth/person/{str(response_id)}/inactive")
    request_include.headers["X-CSRFToken"] = csrf
    response_inactive = await UserViews().inactive(request_include)

    assert isinstance(response_inactive, Response)
    assert response_inactive.status_code == 200
