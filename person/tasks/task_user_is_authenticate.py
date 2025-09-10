"""
person/tasks/task_user_is_authenticate.py
"""

import asyncio
import logging
from datetime import datetime
from json import JSONDecodeError

from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError
from celery import shared_task

from logs import configure_logging
from person.interfaces import TypeUser
from person.views_api.redis_person import RedisOfPerson


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@shared_task(
    name=__name__,
    bind=True,
    ignore_result=True,
    autoretry_for=(TimeoutError,),
    retry_backoff=False,
)
def task_user_authenticate(self, user_id: int) -> dict | bool:
    log.info("START CACHE: %s" % __name__)

    """ "
    Here, we get a dict from non-relational(Redis 1) DB and updating the properties (then saved to the Redis 1).
    If all 'OK' we return True or empty dict (when wea have an Error), to the outside.
    """
    try:
        asyncio.get_event_loop().run_until_complete(
            async_task_user_authenticate(user_id)
        )
    except (ConnectionError, Exception) as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error.args.__getitem__(0))))
        return {}
    return True


async def async_task_user_authenticate(user_id: int) -> dict | bool:
    """
    When is all OK, function returns the answer of Bool type. It's True. When we have Error or
     not all is OK then we have an empty dictionary.
    :param int user_id: Index of user.
    :return:
    """
    client: type(Redis.client) = None
    key = f"user:{user_id}:person"
    user_json: TypeUser | None = None
    try:
        # Redis client with retries on custom errors
        client = RedisOfPerson() if not client else client
    except (ConnectionError, Exception) as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error.args.__getitem__(0))))
        return {}
    # Check tha ping for cache's db

    try:
        user_json = await client.async_basis_collection(user_id)
        log.info(f"%s: Expected dict, got {user_json}" % (__name__))
        if not user_json or not isinstance(user_json, dict):
            log.error(
                ValueError(f"%s: Expected dict, got {type(user_json)}" % (__name__))
            )
            return {}
    except Exception as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error)))
        return {}

    try:
        # UPDATE DATE FROM NON-RELATION DB
        if user_json.get("is_active", False):
            user_json.__setitem__("is_active", True)
        if user_json.get("is_activated", False):
            user_json.__setitem__("is_activated", True)
        if user_json.get("is_verified", False):
            user_json.__setitem__("is_verified", True)
        user_json.__setitem__(
            "date_joined", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%u")
        )
        user_json.__setitem__(
            "last_login", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%u")
        )

        await client.async_set_cache_user(key, **user_json)
        return True
    except (JSONDecodeError, Exception) as error:
        log.error(ValueError("%s: ERROR => %s" % (__name__, error)))
        return {}
    finally:
        await client.aclose()
