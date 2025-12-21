"""
person/tasks/task_user_is_login.py
"""

import asyncio
import logging
from datetime import datetime
from json import JSONDecodeError

from celery import shared_task
from redis.asyncio.client import Redis

from logs import configure_logging
from person.interfaces import TypeUser
from person.views_api.redis_person import RedisOfPerson

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@shared_task(
    name=__name__,
    bind=True,
    ignore_result=True,
    autoretry_for=(
        Exception,
        TimeoutError,
    ),
    retry_backoff=False,
)
def task_user_login(self, user_id: int) -> dict | bool:
    log.info("START CACHE: %s" % __name__)
    """ "
        Here, we get a dict from non-relational(Redis 1) DB and updating the properties (then saved to the Redis 1).
        If all 'OK' we return True or empty dict (when wea have an Error), to the outside.
        """
    try:
        asyncio.get_event_loop().run_until_complete(async_task_user_login(user_id))
    except (ConnectionError, Exception) as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error.args.__getitem__(0))))
        return {}
    return True


async def async_task_user_login(user_id: int) -> dict | bool:
    client: type(Redis.client) = None
    key = f"user:{user_id}:person"
    user_json: TypeUser | None = None
    try:
        # Redis client with retries on custom errors
        client = RedisOfPerson()
    except (ConnectionError, Exception) as error:
        log.error(
            ValueError(
                "%s: ERROR => %s"
                % (async_task_user_login.__name__, error.args.__getitem__(0))
            )
        )
        return {}

    try:
        # Check a key into the db for the cached user
        user_json = await client.async_basis_collection(user_id)
        # User was not found in cache/ It means the registration was unsuccessful.
        # On the stage be avery one user is saved in cache
        log.info(
            f"%s: Expected dict, Yes or Not: {user_json}"
            % async_task_user_login.__name__
        )
        log.info(
            f"%s: Expected TYPE: {type(user_json)}" % async_task_user_login.__name__
        )
        if len(user_json.keys()) == 0:
            log.error(
                ValueError(
                    f"%s: Expected dict, got {type(user_json)}"
                    % async_task_user_login.__name__
                )
            )
            return {}
    except Exception as error:
        log.error(
            ValueError("%s: ERROR => %s" % (async_task_user_login.__name__, error))
        )
        return {}

    try:
        # LOGIN
        if user_json.get("is_active", False):
            user_json.__setitem__("is_active", True)
        user_json.__setitem__(
            "last_login", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%u")
        )
        # SAVING
        await client.async_set_cache_user(key, **user_json)
        return True
    except (JSONDecodeError, Exception) as error:
        log.error(
            ValueError("%s: ERROR => %s" % (async_task_user_login.__name__, error))
        )
        return {}
    finally:
        await client.aclose()
