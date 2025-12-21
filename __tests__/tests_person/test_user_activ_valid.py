"""
__tests__/tests_person/test_user_activ_valid.py
"""

import asyncio
import json
import logging

import pytest
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from rest_framework.test import APIRequestFactory

from __tests__.__fixtures__.fix import (
    fix_del_user_of_db,
    fix_get_session,
    fix_get_user_of_db,
)
from logs import configure_logging
from person.views_api.redis_person import RedisOfPerson
from project.views import CSRFTokenView

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


# Note: Email is the field not necessarily
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
@pytest.mark.persone_active_valid
@pytest.mark.django_db
async def test_persone_active_valid(
    fix_get_user_of_db,
    fix_del_user_of_db,
    fix_get_session,
    username,
    email,
    password,
    category,
    expected,
):
    from person.views_api.users_views import UserViews

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
            "username": username.strip(),
            "email": email.strip(),
            "password": password.strip(),
            "category": category.strip(),
        },
    )
    await UserViews().create(request)
    log.info(
        "%s: REGISTRATE - COMPLETED a REGISTRATION" % test_persone_active_valid.__name__
    )
    # CHECK THE QUANTITY OF LINES (see to the log file)
    await fix_get_user_of_db()

    # get the csrf-token
    request = factory.get("auth/csrftoken/")
    csrf_response = await CSRFTokenView().get(request)
    log.info(
        "%s: ACTIVE - 'csrf_response': %s & type of csrf_response: %s"
        % (
            test_persone_active_valid.__name__,
            str(csrf_response.__dict__),
            type(csrf_response),
        )
    )
    # assert isinstance(csrf_response, JsonResponse)
    # assert csrf_response.status_code == 200
    # assert isinstance(csrf_response.data, str)
    # assert len(csrf_response.data) > 5

    # CREATING THE REQUEST FOR USER's ACTIVATION
    request = factory.post("/person/0/active/", content_type="application/json")
    request.__setattr__("user", AnonymousUser())
    request.headers.__setattr__(
        "Set-Cookie",
        json.loads(csrf_response.content.decode()).__getitem__("csrfToken"),
    )
    request.__setattr__(
        "data",
        {
            "username": username,
            "password": password,
        },
    )
    # CREATE AND ADDING a SESSION FOR USER's ACTIVATION
    request = await fix_get_session(request)
    # THIS REQUEST TO THE SERVER for getting the activation's tokens and the data properties of user
    response = await UserViews().active(request, kwargs=request.body)
    log.info(
        "%s: RECEIVED THE RESPONSE: %s"
        % (test_persone_active_valid.__name__, str(response.__dict__))
    )

    # CHECK THA STATUS CODE
    res_bool = True if response.status_code < 400 else False
    log.info(
        "%s: ACTIVE - GET 'res_bool': %s"
        % (test_persone_active_valid.__name__, res_bool)
    )

    assert res_bool == expected
    log.info(
        "%s: ACTIVE - RESPONSE 'res_bool': %s"
        % (test_persone_active_valid.__name__, res_bool)
    )
    # CHECK = WHAT CONTAINING IN RESPONSE
    data_of_response = json.loads(response.content.decode()).__getitem__("data")
    result_bool = (
        (True if "user" in data_of_response[0].keys() else False)
        if type(data_of_response) == list and len(data_of_response) > 0
        else False
    )
    assert result_bool == expected

    async def clean_redis():
        client = RedisOfPerson(db=1)
        for i in range(0, 10):
            await client.delete(f"user:{i}:person")

    task_clean_redis_1 = asyncio.create_task(clean_redis())
    task_clean_relation_db = asyncio.create_task(fix_del_user_of_db())

    # CLEANING IN DB
    await asyncio.gather(task_clean_redis_1, task_clean_relation_db)
