"""
person/tasks/task_cache_hew_user.py
"""

import json
import logging
import os
from typing import Union

from celery import shared_task
from celery.utils.log import get_task_logger
from redis import Redis, TimeoutError

from logs import configure_logging
from person.interfaces import TypeUser
from person.models import Users
from person.redis_utils import get_redis_client
from person.views_api.serializers import CacheUsersSerializer
from project.settings_conf.settings_env import DB_TO_RADIS_CACHE_USERS, DB_TO_RADIS_HOST

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

log = logging.getLogger(__name__)
configure_logging(logging.INFO)

logger = get_task_logger(__name__)


@shared_task(
    name=__name__,
    bind=True,
    ignore_result=True,
    autoretry_for=(TimeoutError,),
    retry_backoff=False,
)
def task_postman_for_user_id(self, user_id_list: list[int]) -> Union[TypeUser, dict]:
    """
    retry_backoff - https://docs.celeryq.dev/en/stable/userguide/tasks.html#Task.autoretry_for
    ignore_result - If False, it means we don't have a response. Or conversely if we have a True.
    https://docs.celeryq.dev/en/stable/userguide/tasks.html#Task.ignore_result

    This Task is a POSTMAN. Here only transmits the user id. It happens from the entry point to the handler function
    :param self:
    :param user_id_list: Index from new user, we receive in list format.
    :return:
    """
    if len(user_id_list) == 0:
        log.error(ValueError("[%s]: No users found" % __name__))
        return {}
    return person_to_redis(user_id_list)


def person_to_redis(user_id_list: list[int]) -> Union[TypeUser, dict]:
    """
    In entry-point, we should receive a list from number. By this the list then we will be caching of users
    Here, we will be caching of new user after registration/ From entrypoint,we get an id.
    After that, we find the user by id and send it to the cache.
    :param self:
    :param user_id_list: Index from new user, we receive in list format.
    :return:
    """

    log.info("START CACHE: %s" % __name__)
    r = get_redis_client()
    # client = Redis(
    #     host=f"{DB_TO_RADIS_HOST}",
    #     port=6380,
    #     db=DB_TO_RADIS_CACHE_USERS,
    # )
    # переписать redis черех client
    try:

        if not r.ping():
            log.error(ConnectionError("Redis connection failed"))
            return {}
        log.info("Client is ping")
        response_last: Union[TypeUser, dict] = {}
        # Basis db
        for index in user_id_list:
            person_list = Users.objects.filter(id=index)
            if not person_list.exists():
                log.error(
                    ValueError(
                        "[%s]: No users found in Users's db. Length from 'person_list' is %s "
                        % (__name__, str(len(person_list)))
                    )
                )
                return {}
            user_serializer = CacheUsersSerializer(person_list.__getitem__(0))
            user_dict: TypeUser = user_serializer.data.copy()
            log.info("Received user ID: %s" % user_dict.__getitem__("id"))
            # Redis's cache
            # Now will be saving on the 27 hours.
            # 'task_user_from_cache' task wil be to upgrade postgres at ~ am 01:00
            # Timetable look the 'project.celery.app.base.Celery.conf'
            look_key = (f"user:{str(user_dict.__getitem__("id"))}:person",)
            try:
                r.set(
                    look_key,
                    json.dumps(user_dict),
                    nx=True,
                    ex=97200,
                )
                r.close()
                log.info(
                    "User with %s ID was saved in Redis. The End"
                    % str(user_dict.__getitem__("id"))
                )
                response_last.update(user_dict)
            except Exception as e:
                log.error("[%s]:ERROR =>  %s" % (__name__, e.args[0]))
                r.delete(look_key)
        return response_last
    except Exception as error:
        log.error("[%s]: ERROR => %s" % (__name__, error.args.__getitem__(0)))

        return {}
