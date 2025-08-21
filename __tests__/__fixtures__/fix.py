import pytest
import logging
from logs import configure_logging
from person.models import Users
from project.service import sync_for_async
from rest_framework.response import Response

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@pytest.fixture(autouse=True, scope="function")
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
