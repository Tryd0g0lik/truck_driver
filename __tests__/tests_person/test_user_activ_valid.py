"""
__tests__/tests_person/test_user_activ_valid.py
"""

import json

import pytest
import logging

from blib2to3.pgen2.token import AWAIT

from __tests__.__fixtures__.fix import fix_clear_db, fix_get_user_of_db
from logs import configure_logging
from rest_framework.test import APIRequestFactory

from django.contrib.auth.models import AnonymousUser

from project.service import sync_for_async
from project.views import CSRFTokenView

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.mark.parametrize(
    "username, email, password, category, expected",
    [
        ("Serge", "serge@his.com", "123456789", "BASE", True),
        (" Serge_01 ", "serge@his.com", "123456%789", "BASE", True),
        (" Serge_03 ", "serge@his.com", "1234567dsq89", "BASE", True),
        ("Serge_02", "serge@his.com", "123456789", "BASE", True),
    ],
)
@pytest.mark.persone_active_valid
@pytest.mark.django_db
async def test_persone_active_valid(
    fix_clear_db, fix_get_user_of_db, username, email, password, category, expected
):
    from person.views_api.users_views import UserViews
    from django.contrib.sessions.middleware import SessionMiddleware

    log.info(
        "%s: START TEST WHERE 'username': %s & 'email': %s & 'password': %s & 'category': %s & 'expecteD': %s"
        % (
            test_persone_active_valid.__name__,
            username,
            email,
            password,
            category,
            expected,
        )
    )
    factory = APIRequestFactory()
    log.info("%s: BEGINNING a REGISTRATION" % test_persone_active_valid.__name__)
    request = factory.post("/person/", content_type="application/json")
    request.__setattr__("user", AnonymousUser())
    request.__setattr__(
        "data",
        {
            "username": username,
            "email": email,
            "password": password,
            "category": category,
        },
    )
    email = request.data.__getitem__("email")
    log.info(
        "%s:REGISTRATE - GET REQUEST.data['email'] %s"
        % (test_persone_active_valid.__name__, email)
    )
    # csrf = await CSRFTokenView().get(request)
    # request.headers.__setattr__("Set-Cookie", csrf)
    log.info(
        "%s: REGISTRATE - GET REQUEST" % test_persone_active_valid.__name__,
    )

    await UserViews().create(request)
    log.info(
        "%s: REGISTRATE - COMPLETED a REGISTRATION" % test_persone_active_valid.__name__
    )
    await fix_get_user_of_db()
    log.info(
        "%s: ACTIVE - GET FACTORY" % test_persone_active_valid.__name__,
    )

    # get the csrf-token
    request = factory.get("auth/csrftoken/")
    csrf_response = await CSRFTokenView().get(request)
    log.info(
        "%s: ACTIVE - 'csrf_response': %s"
        % (test_persone_active_valid.__name__, str(csrf_response.__dict__))
    )
    log.info(
        "%s: AFTER, GET CSRF: %s "
        % (
            test_persone_active_valid.__name__,
            json.loads(csrf_response.content.decode()).__getitem__("csrfToken"),
        )
    )

    request = factory.post("/person/0/active/", content_type="application/json")
    request.__setattr__("user", AnonymousUser())
    request.headers.__setattr__(
        "Set-Cookie",
        json.loads(csrf_response.content.decode()).__getitem__("csrfToken"),
    )
    # request.user.__setattr__("is_active", True)
    request.__setattr__(
        "data",
        {
            "username": username,
            "password": password,
        },
    )
    # ADDING a SESSION
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(request)
    request_is_saving = request.session.save
    await sync_for_async(request_is_saving)

    response = await UserViews().active(request, kwargs=request.body)
    log.info(
        "%s: RECEIVED THE RESPONSE: %s"
        % (test_persone_active_valid.__name__, str(response.__dict__))
    )
    log.info(
        "%s: ACTIVE - GET 'user_factory'" % test_persone_active_valid.__name__,
    )
    log.info(
        "%s: ACTIVE - GET 'status_code': %s"
        % (test_persone_active_valid.__name__, response.status_code)
    )
    res_bool = True if response.status_code < 400 else False
    log.info(
        "%s: ACTIVE - GET 'res_bool': %s"
        % (test_persone_active_valid.__name__, res_bool)
    )
    # await clear_db() if res_bool == expected else None
    assert res_bool == expected
    log.info(
        "%s: ACTIVE - RESPONSE 'res_bool': %s"
        % (test_persone_active_valid.__name__, res_bool)
    )
    # await clear_db() if response.data["data"].lower() == "Ok".lower() else None
    result_bool = (
        (True if "user" in response.data["data"][0].keys() else False)
        if type(response.data["data"]) == list and len(response.data["data"]) > 0
        else False
    )
    assert result_bool == expected
