import asyncio
import base64
import json
import logging
import re
from typing import Dict, Union, Any
from redis.asyncio.client import Redis
from redis.exceptions import ConnectionError

from dotenv_ import DB_TO_RADIS_HOST, DB_TO_RADIS_PORT
from logs import configure_logging
from person.binaries import Binary
from person.views_api.serializers import CacheUsersSerializer, AsyncUsersSerializer
from project.service import sync_for_async

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class RedisOfPerson(Redis, Binary):
    def __init__(
        self,
        host: str = f"{DB_TO_RADIS_HOST}",
        port: int = f"{DB_TO_RADIS_PORT}",
        db: Union[str, int] = 1,
    ):
        """
        This is class for a work with Redis. Then your need open the access to the redis's db and done all tasks, don't forget to close the connection.
        :param str host: Redis server host is specified in '.env' file.
        :param str port: Redis port of server is specified in '.env' file, too.
        :param int db: This the param has number 1, by default.
        """
        super().__init__(host=host, port=port, db=db)
        self.client_state = None
        self.db = db

    async def ping(self, **kwargs) -> bool:
        ping = await super().ping(**kwargs)
        if not ping:
            raise ConnectionError("Redis connection failed")
        return True

    async def async_has_key(self, one_key: str = "") -> bool:
        """
        :param one_key: Key for get data from redis's db. Example. User after registration hase the 'user:<user_index>:person' of key.
        If you can't get data? check the db number. It where you are connected. Example.
        :return: bool. If we have - True, it means - we have a key in the general list
        """

        log.info(
            "%s: BEFORE GET KEYS: KEY %s"
            % (RedisOfPerson.__class__.__name__ + self.async_has_key.__name__, one_key)
        )
        k_list_encode = await self.keys()
        if len(k_list_encode) == 0:
            log.info(
                "%s: KEYS was not found: %s"
                % (
                    RedisOfPerson.__class__.__name__ + self.async_has_key.__name__,
                    one_key,
                )
            )
            return False
        log.info(
            "%s: GOT b_KEYS: length KEY's LIST %s"
            % (
                RedisOfPerson.__class__.__name__ + self.async_has_key.__name__,
                len(k_list_encode),
            )
        )
        k_list = [s.decode() for s in k_list_encode]
        log.info(
            "%s: GOT KEYS: %s"
            % (
                RedisOfPerson.__class__.__name__ + self.async_has_key.__name__,
                True if one_key in k_list else False,
            )
        )
        return True if one_key in k_list else False

    async def async_get_cache_user(self, key: str) -> dict[str, Any] | bool:
        """
        :param str key: Key for get data from redis's db. Example. User after registration hase the 'user:<user_index>:person' of key.
        If you can't get data? check the db number. It where you are connected. Example.
        For person's cache is number '1'.
        :return: dict/json | False.
        """
        # result = await self.async_has_key(key)
        get_ = await self.get(key)
        return json.loads(get_.decode())

    async def async_set_cache_user(
        self, key: str, **kwargs: Dict[str, Union[str, int]]
    ) -> bool:
        """
        :param str key: Template is "user:< user_id >:person". This is key element, by key look up where it will be saved
        :param dict kwargs: Redis's cache.
        Session of user saving in cache's session db (Redis 0). "kwargs={'user': <Users's object >}".
        HEre, in db = 0 used the object transformation to the binary data through the library 'pickle'. Then, transformation in string's type through JSON

        Caching of user's db it's to the cache's db (Redis's db 1). Here, user's data presented to the dict type.
        Now will be saving on the 27 hours.
        'task_user_from_cache' task wil be to upgrade postgres at ~ am 01:00
        Timetable look the 'project.celery.app.base.Celery.conf'

        :return bool
        """
        try:
            user = kwargs.__getitem__("user")
            if user:
                """
                User's object save in cache's session (Redis 0)
                """
                result = AsyncUsersSerializer(user)
                result = await sync_for_async(lambda: result.data)
                b_user = (
                    base64.b64encode(self.object_to_binary(user))
                    if self.db == 0
                    else json.dumps(result).encode()
                )
                log.info(
                    "%s: 'b_user': %s "
                    % (
                        RedisOfPerson.__class__.__name__
                        + "."
                        + self.async_set_cache_user.__name__,
                        b_user,
                    )
                )
                result_str: str = (
                    b_user.decode(
                        "utf-8",
                        errors="DECODE ERROR - %s:" % RedisOfPerson.__class__.__name__
                        + "."
                        + self.async_set_cache_user.__name__,
                    )
                    if self.db == 1
                    else json.dumps({"b_user": b_user.decode()})
                )

                await self.set(key, value=result_str)
                log.info(
                    "%s: WAS SAVED "
                    % (
                        RedisOfPerson.__class__.__name__
                        + "."
                        + self.async_set_cache_user.__name__
                    )
                )
                return True

        except Exception as error:
            log.info(
                ValueError(
                    "%s: ERROR => %s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + "."
                        + self.async_set_cache_user.__name__,
                        error.args[0],
                    )
                )
            )
            return False
        try:
            """
            Cache's db
            """
            await self.set(key, json.dumps(kwargs), 97200)
            return True
        except Exception as error:
            log.info(
                ValueError(
                    "%s: ERROR => %s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_set_cache_user.__name__,
                        error.args[0],
                    )
                )
            )
            return False

    async def async_del_cache_user(self, key: str) -> bool:
        """

        :param str key: Here, 'key' this is line from  the template it's 'user:< user_id>:person'
        :return:
        """
        result = re.match(r"user:[0-9]+:person", key)
        if not result:
            raise ValueError(
                "%s is not a valid key: '%s'"
                % (
                    RedisOfPerson.__class__.__name__
                    + "."
                    + self.async_del_cache_user.__name__,
                    key,
                )
            )
        await self.delete(key)

        return True

    async def async_basis_collection(self, user_id: int) -> dict[str, Any]:
        """
        Here, woas collected the code which ofter we could meet in to the operation by the data update to Redis. It's by 'person'.
        :param int user_id: user's index,
        :return: dict/json string. This is an image of user.
        """
        key = f"user:{user_id}:person"

        # Check tha ping for cache's db
        if not await self.ping():
            raise ConnectionError("Redis connection failed")
        try:
            # Check a key into the db for the cached user
            res_bool = await self.async_has_key(key)

            # User was not found in cache/ It means the registration was unsuccessful.
            # On the stage be avery one user is saved in cache
            if not res_bool:
                raise (
                    ValueError(
                        "%s: ERROR => User not was founded"
                        % (
                            RedisOfPerson.__class__.__name__
                            + self.async_basis_collection.__name__,
                        )
                    )
                )

        except Exception as error:
            log.error(error)
            return {}
        log.info(
            "%s: GOT MESSAGE: %s"
            % (
                RedisOfPerson.__class__.__name__ + self.async_basis_collection.__name__,
                "Passed the check ",
            )
        )
        try:
            user_json = await self.async_get_cache_user(key)
            if not user_json:
                log.info(
                    ValueError(
                        "%s: ERROR => User not was founded in cache: %s"
                        % (
                            RedisOfPerson.__class__.__name__
                            + self.async_basis_collection.__name__,
                            user_json,
                        )
                    )
                )
                return {}
            log.info(
                "%s: GOT 'user_json'. It's BOOL: %s"
                % (
                    RedisOfPerson.__class__.__name__
                    + self.async_basis_collection.__name__,
                    isinstance(user_json, dict),
                )
            )
            if not isinstance(user_json, dict):
                log.error(
                    ValueError(
                        f"%s: Expected dict, got {type(user_json)}"
                        % (
                            RedisOfPerson.__class__.__name__
                            + self.async_basis_collection.__name__
                        )
                    )
                )
            else:
                log.info(
                    "%s: GOT 'user_json' #%s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_basis_collection.__name__,
                        user_id,
                    )
                )
                return user_json
            return {}
        except Exception as error:
            log.error(
                ValueError(
                    "%s: ERROR => %s"
                    % (
                        RedisOfPerson.__class__.__name__
                        + self.async_basis_collection.__name__,
                        error,
                    )
                )
            )
            return {}
