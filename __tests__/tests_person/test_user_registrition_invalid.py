"""
__tests__/tests_person/test_user_registrition.py
"""

import pytest
import logging
from logs import configure_logging
from rest_framework.test import APIRequestFactory
from __tests__.__fixtures__.fix import fix_clear_db
from django.contrib.auth.models import AnonymousUser

from person.models import Users
from project.service import sync_for_async
from project.views import CSRFTokenView

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.mark.parametrize(
    "username, email, password, category, expected",
    [
        ("0Serge", "serge@his.com", "123456789", "BASE", False),
        ("Serge", "serge@his.com", "", "BASE", False),
        ("Serge", "", "123456789", "BASE", False),
        ("", "serge@his.com", "123456789", "BASE", False),
        ("Serge", "serge@hiscom", "123456789", "BASE", False),
        ("Serge", "serge@hiscom", "123456789", "BASE", False),
        ("Serge", "serge@hiscom", "123456789", "BASE", False),
        ("Serge", "sergehis.com", "123456789", "BASE", False),
    ],
)
@pytest.mark.invalid
@pytest.mark.xfail
@pytest.mark.django_db
async def test_person_invalid(
    fix_clear_db, username, email, password, category, expected
) -> None:
    from person.views_api.users_views import UserViews

    # Here , we clear of db
    await fix_clear_db()

    log.info(
        "%s: START TEST WHERE 'username': %s & 'email': %s & 'password': %s & 'category': %s & 'expecteD': %s"
        % (
            test_person_invalid.__name__,
            username,
            email,
            password,
            category,
            expected,
        )
    )
    fuctory = APIRequestFactory()
    log.info(
        "%s: GET FACTORY" % test_person_invalid.__name__,
    )
    request = fuctory.post("/person/", content_type="application/json")
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
    log.info("%s: GET REQUEST.data['email'] %s" % (test_person_invalid.__name__, email))
    csrf = await CSRFTokenView().get(request)
    request.headers.__setattr__("Set-Cookie", csrf)
    log.info(
        "%s: GET REQUEST" % test_person_invalid.__name__,
    )

    response = await UserViews().create(request)

    log.info(
        "%s: GET 'user_factory'" % test_person_invalid.__name__,
    )
    log.info(
        "%s: GET 'status_code': %s"
        % (test_person_invalid.__name__, response.status_code)
    )
    res_bool = False if response.status_code >= 400 else True
    log.info("%s: GET 'res_bool': %s" % (test_person_invalid.__name__, res_bool))
    assert not res_bool
    log.info("%s: RESPONSE 'res_bool': %s" % (test_person_invalid.__name__, res_bool))
    assert response.data["data"].lower() != "Ok".lower()

    log.info(
        "%s: RESPONSE 'res_bool.data' %s"
        % (test_person_invalid.__name__, response.data)
    )


async def clear_db():
    filter_list = [view async for view in Users.objects.all()]
    log.info(
        "%s: GET ASYNC FILTER LEN: %s"
        % (test_person_invalid.__name__, str(len(filter_list)))
    )
    res = [await sync_for_async(view.delete) for view in filter_list]
    log.info("%s: RES: %s" % (test_person_invalid.__name__, res))
    log.info(
        "%s: FINALLY" % test_person_invalid.__name__,
    )
