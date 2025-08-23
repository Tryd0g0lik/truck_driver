"""
__tests__/tests_person/test_user_registrition.py
"""

import pytest
import logging
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import AnonymousUser
from __tests__.__fixtures__.fix import fix_get_user_of_db
from logs import configure_logging
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
@pytest.mark.person_creat_valid
@pytest.mark.django_db
async def test_person_valid(
    fix_get_user_of_db, username, email, password, category, expected
) -> None:
    from person.views_api.users_views import UserViews

    log.info(
        "%s: START TEST WHERE 'username': %s & 'email': %s & 'password': %s & 'category': %s & 'expecteD': %s"
        % (
            test_person_valid.__name__,
            username,
            email,
            password,
            category,
            expected,
        )
    )
    fuctory = APIRequestFactory()
    log.info(
        "%s: GET FACTORY" % test_person_valid.__name__,
    )
    request = fuctory.post("/person/", content_type="application/json")
    request.__setattr__("user", AnonymousUser())
    request.user.__setattr__("is_active", False)
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
    log.info("%s: GET REQUEST.data['email'] %s" % (test_person_valid.__name__, email))
    # csrf = await CSRFTokenView().get(request)
    # request.headers.__setattr__("Set-Cookie", csrf)
    # log.info(
    #     "%s: GET REQUEST" % test_person_valid.__name__,
    # )

    response = await UserViews().create(request)

    log.info(
        "%s: GET 'user_factory'" % test_person_valid.__name__,
    )
    log.info(
        "%s: GET 'status_code': %s" % (test_person_valid.__name__, response.status_code)
    )
    res_bool = True if response.status_code < 400 else False
    log.info("%s: GET 'res_bool': %s" % (test_person_valid.__name__, res_bool))
    # await clear_db() if res_bool == expected else None
    assert res_bool == expected
    log.info("%s: RESPONSE 'res_bool': %s" % (test_person_valid.__name__, res_bool))
    # await clear_db() if response.data["data"].lower() == "Ok".lower() else None
    assert response.data["data"].lower() == "Ok".lower()

    log.info(
        "%s: RESPONSE 'res_bool.data' %s" % (test_person_valid.__name__, response.data)
    )
    # In the log file can see a quantity of line which was created to the 'Users' db. It's lines from the test.
    await fix_get_user_of_db()
