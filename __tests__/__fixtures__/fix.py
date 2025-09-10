"""
__tests__/__fixtures__/fix.py
"""

import pytest
import logging

from django.http import HttpRequest

from logs import configure_logging
from person.models import Users
from project.service import sync_for_async
from django.contrib.sessions.middleware import SessionMiddleware

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.fixture
def fix_clear_db():

    async def factory():
        # Here , we clear of db
        filter_list = [view async for view in Users.objects.all()]
        log.info(
            "%s: GET ASYNC FILTER LEN: %s" % (factory.__name__, str(len(filter_list)))
        )
        res = [await sync_for_async(view.delete) for view in filter_list]
        log.info("%s: RES: %s" % (factory.__name__, res))
        log.info(
            "%s: FINALLY" % factory.__name__,
        )

    return factory


@pytest.fixture()
def fix_get_user_of_db():
    async def factory():
        filter_list = [view async for view in Users.objects.all()]
        log.info(
            "%s: FINALLY. LEN of 'filter_list': %s"
            % (fix_get_user_of_db.__name__, len(filter_list))
        )

    return factory


@pytest.fixture()
def fix_del_user_of_db():
    async def factory():
        [await view.adelete() async for view in Users.objects.all()]

    return factory


@pytest.fixture
def fix_get_session():
    async def factory(request: HttpRequest) -> HttpRequest:
        # CREATE AND ADDING a SESSION
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request_is_saving = request.session.save
        await sync_for_async(request_is_saving)
        return request

    return factory
