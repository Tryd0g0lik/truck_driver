"""
person/tasks/task_user_from_cache_to_td_repeat.py
"""

import json
import logging
from celery import shared_task
from redis import Redis

from dotenv_ import DB_TO_RADIS_HOST, DB_TO_RADIS_PORT, DB_TO_RADIS_CACHE_USERS
from logs import configure_logging
from person.views_api.serializers import CacheUsersSerializer

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


@shared_task(
    name=__name__,
    bind=True,
    authretry_for=(TimeoutError,),
)
def task_user_from_cache(self) -> bool:
    """
    Task of Celery will be to upgrade postgres at ~ am 01:00
    Timetable look the 'project.celery.app.base.Celery.conf'
    Note: Everything task be close in self body. Before, every new task need run a new client.
    :param self:
    :return: True it means what all OK, or not.
    """
    log.info("%s: START TO UPGRADE DB." % task_user_from_cache.__name__)
    client: type(Redis.client) = None
    try:
        client = Redis(
            host=f"{DB_TO_RADIS_HOST}",
            port=f"{DB_TO_RADIS_PORT}",
            db=DB_TO_RADIS_CACHE_USERS,
        )
    except Exception as error:
        log.error(
            ValueError(
                "%s: Error => %s" % (task_user_from_cache.__name__, error.args[0])
            )
        )
        return False

    return person_upgrade_data_of_user(client)


def person_upgrade_data_of_user(client: type(Redis.client)) -> bool:
    """
    Function is handler for upgrade the db Users.
    Timetable look the 'project.celery.app.base.Celery.conf'
    :param Redis.client client: Client from Redis for commands/
    :return: True it means what all OK, or not.
    """

    status = False
    if not client.ping():
        raise ConnectionError(
            "%s: Redis connection failed" % person_upgrade_data_of_user.__name__
        )
    log.info("CLient is ping")
    keys_list = [item.decode() for item in client.keys("user:*")]
    try:
        # Upgrade basis db.
        for k_name in keys_list:
            # Redis's CACHE
            user_json = json.loads((client.get(k_name)).decode("utf-8"))
            # Basis db
            CacheUsersSerializer(data=user_json).save()
            log.info(
                "%s: ID №: %s was upgraded"
                % (person_upgrade_data_of_user.__name__, k_name)
            )
        status = True
    except Exception as error:
        log.error(
            "%s: ERROR => %s" % (person_upgrade_data_of_user.__name__, error.args[0])
        )
        return False
    finally:
        if client:
            client.close()
        log.info(
            "%s: END TO UPGRADE DB. STATUS: %s"
            % (person_upgrade_data_of_user.__name__, str(status))
        )
    return status
