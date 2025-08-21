import base64
import json
import time
import logging
import asyncio
import re
from datetime import datetime


from typing import List

from django.shortcuts import get_object_or_404
from kombu.exceptions import OperationalError
from django.contrib.auth import login as login_user
from django.db import connections, transaction
from django.http import JsonResponse, HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework import serializers, status
from adrf.viewsets import ViewSet
from django.contrib.auth.models import Group
from person.apps import signal_user_registered
from person.cookies import Cookies
from person.interfaces import U
from person.tasks.task_cache_hew_user import task_postman_for_user_id
from person.models import Users
from person.hasher import Hasher
from person.views_api.redis_person import RedisOfPerson
from person.views_api.serializers import AsyncUsersSerializer
from person.access_tokens import AccessToken
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from project.service import sync_for_async
from project.settings import SIMPLE_JWT
from person.binaries import Binary
from dotenv_ import SECRET_KEY_DJ

from logs import configure_logging
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)
configure_logging(logging.INFO)


def new_connection(data) -> list:
    """
    new user cheks on the duplicate
    :param data:
    :return:
    """
    with connections["default"].cursor() as cursor:
        try:
            cursor.execute(
                """SELECT * FROM person WHERE username = '%s' AND email = '%s';"""
                % (data.get("username"), data.get("email").strip())
            )
        except Exception as error:
            log.error(
                "%s: Error => %s"
                % (__name__ + "::" + new_connection.__name__, error.args[0])
            )
            raise ValueError(
                "%s: Error => %s"
                % (__name__ + "::" + new_connection.__name__, error.args[0])
            )
        # POSTGRES_DB
        resp_list = cursor.fetchall()
        users_list = [view for view in resp_list]
    return users_list


async def iterator_get_person_cache(client: type(RedisOfPerson)):
    """
    Get all collections of keys from person's cache.
    :return:
    """
    keys = await client.keys("user:*")
    for key in keys:
        yield key


class UserViews(ViewSet):

    @swagger_auto_schema(
        operation_description="""
            Method: POST and the fixed pathname of '/api/auth/person/'\
            Example PATHNAME: "{{url_base}}/api/auth/person/"\
            @param: str category: Single line from total list, it user must choose/select.\
            Total list from category: BASE, DRIVER, MANAGER, ADMIN. It's roles for user. Everyone \
            role contain the list permissions.
            """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="BodyData",
            in_=openapi.IN_BODY,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(
                    example="<user_name>", type=openapi.TYPE_STRING
                ),
                "email": openapi.Schema(
                    example="<user_email>", type=openapi.TYPE_STRING
                ),
                "password": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
                "category": openapi.Schema(example="BASE", type=openapi.TYPE_STRING),
            },
        ),
        responses={
            201: "Ok",
            401: "Not Ok",
            500: "Something what wrong. Read the response variable 'data'",
        },
        tags=["person"],
    )
    async def create(self, request: HttpRequest) -> type(Response):
        """
        TODO: 'group_list' and code is below from 'group_list' take to the outside for Celery or the thread
        :param request:
        :return:
        """
        user = request.user
        data = request.data
        try:
            # Validators
            check_validate = [self.validate_username(data.get("username").strip())]
            check_validate.append(self.validate_password(data.get("password").strip()))
            fals_data = [item for item in check_validate if not item]
            if len(fals_data) > 0:
                log.error(
                    "%s: data is not validate" % UserViews.__class__.__name__
                    + "."
                    + self.create.__name__
                )
                raise ValueError(
                    "%s: data is not validate" % UserViews.__class__.__name__
                    + "."
                    + self.create.__name__
                )
        except (AttributeError, TypeError, Exception) as error:
            log.error(
                "%s: ERROR => %s"
                % (
                    UserViews.__class__.__name__ + "." + self.create.__name__,
                    error.args[0],
                )
            )
            return Response(
                {"data": " Data type is not validate: %s" % error.args},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        response = Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            # sync to async - user's checker on the duplicate
            users_list: list[Users.objects] = await asyncio.create_task(
                asyncio.to_thread(new_connection, data=data)
            )

        except Exception as error:
            log.error(
                "%s: ERROR => %s"
                % (
                    UserViews.__class__.__name__ + "." + self.create.__name__,
                    error.args[0],
                )
            )
            # RESPONSE WILL SEND. CODE 401
            response.data = {"data": error.args}
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response

        if not user.is_authenticated and user.is_active and len(users_list) == 0:
            # Open transaction

            try:
                password_hes = self.get_hash_password(data.get("password"))
                serializer = AsyncUsersSerializer(data=data)
                # CHECK - VALID DATA
                await self.serializer_validate(serializer)
                serializer.validated_data["password"] = password_hes
                await serializer.asave()

                data: dict = await sync_for_async(lambda: serializer.data)
                group_list = [
                    view
                    async for view in Group.objects.filter(
                        name=serializer.data.get("category")
                    )
                ]
                if len(list(group_list)) > 0:
                    user_new = [
                        view async for view in Users.objects.filter(pk=data.get("id"))
                    ]
                    add = user_new[0].groups.add
                    # Below, is my synct_to_async (not from django).
                    await sync_for_async(add, *group_list)
                    user_new[0].is_active = False
                    await user_new[0].asave()
                # # RUN THE TASK - Update CACHE's USER -send id to the redis from celer's task
                task_postman_for_user_id.delay((data.__getitem__("id"),))

            except (OperationalError, Exception) as error:
                log.error(
                    "%s: ERROR => %s"
                    % (
                        UserViews.__class__.__name__ + "." + self.create.__name__,
                        error.args[0],
                    )
                )
                # RESPONSE WILL BE TO SEND. CODE 500
                response.data = {"data": error.args}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
            # RESPONSE WILL BE TO SEND. CODE 200
            response.data = {"data": "OK"}
            # Close transaction
            try:
                if serializer.data["id"]:
                    user_id_list = [
                        view
                        async for view in Users.objects.filter(pk=serializer.data["id"])
                    ]
            except Exception as error:
                log.error(
                    "%s: ERROR => %s"
                    % (
                        UserViews.__class__.__name__ + "." + self.create.__name__,
                        error.args[0],
                    )
                )
                return Response(
                    {"data": error.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            response.status_code = status.HTTP_201_CREATED
            try:
                # SEND MESSAGE TO THE USER's EMAIL
                send = signal_user_registered.send
                asyncio.create_task(
                    asyncio.to_thread(
                        send,
                        sender=self.create,
                        named=data,
                        isinstance=user_id_list.__getitem__(0),
                    )
                )
            except (AttributeError, Exception) as error:
                log.error(
                    "%s: ERROR => %s"
                    % (
                        UserViews.__class__.__name__ + "." + self.create.__name__,
                        error.args[0],
                    )
                )
                response.data = {"data": error.args.__getitem__(0)}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response
        log.error(
            "%s: User was created before."
            % (UserViews.__class__.__name__ + "." + self.create.__name__,)
        )
        response.data = {"data": "User was created before."}
        return response

    @swagger_auto_schema(
        operation_description="""
                Method: POST and the fixed pathname of url
                Example PATHNAME: "/api/auth/person/0/active/"

                """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            title="BodyData",
            in_=openapi.IN_BODY,
            required=["username", "password"],
            properties={
                "username": openapi.Schema(example="Serge", type=openapi.TYPE_STRING),
                "password": openapi.Schema(
                    example="nH2qGiehvEXjNiYqp3bOVtAYv....", type=openapi.TYPE_STRING
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="User data: access & refresh the tokens.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "data": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                allOf=[
                                    openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "user": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    # Здесь добавьте свойства пользователя,
                                                    # аналогично вашему первому примеру
                                                    "id": openapi.Schema(
                                                        type=openapi.TYPE_INTEGER,
                                                        format=openapi.FORMAT_INT64,
                                                        example=123,
                                                    ),
                                                    "username": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        example="Serge",
                                                    ),
                                                    "last_login": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_DATETIME,
                                                        example="2025-07-20 00:39:14.739 +0700",
                                                    ),
                                                    "first_name": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        example="",
                                                    ),
                                                    "email": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_EMAIL,
                                                    ),
                                                    "is_staff": openapi.Schema(
                                                        type=openapi.TYPE_BOOLEAN
                                                    ),
                                                    "is_active": openapi.Schema(
                                                        type=openapi.TYPE_BOOLEAN
                                                    ),
                                                    "date_joined": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_DATETIME,
                                                        example="2025-07-20 00:39:14.739 +0700",
                                                    ),
                                                    "created_at": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_DATETIME,
                                                        example="2025-07-20 00:39:14.739 +0700",
                                                    ),
                                                    "updated_at": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_DATETIME,
                                                        example="2025-07-20 00:39:14.739 +0700",
                                                    ),
                                                    "category": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        example="DRIVER",
                                                    ),
                                                    "password": openapi.Schema(
                                                        type=openapi.TYPE_STRING
                                                    ),
                                                    "is_sent": openapi.Schema(
                                                        type=openapi.TYPE_BOOLEAN
                                                    ),
                                                    "is_verified": openapi.Schema(
                                                        type=openapi.TYPE_BOOLEAN
                                                    ),
                                                    "verification_code": openapi.Schema(
                                                        type=openapi.TYPE_STRING
                                                    ),
                                                    "balamce": openapi.Schema(
                                                        type=openapi.TYPE_NUMBER,
                                                        format=openapi.FORMAT_INT64,
                                                    ),
                                                },
                                            ),
                                        },
                                    ),
                                    openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "access": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "token_access": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        example="nH2qGiehvEXjNiYqp3bOVtAYv....",
                                                    ),
                                                    "live_time": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_DATETIME,
                                                        example="465998",
                                                    ),
                                                },
                                            )
                                        },
                                    ),
                                    openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "reffresh": openapi.Schema(
                                                type=openapi.TYPE_OBJECT,
                                                properties={
                                                    "token_refresh": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        example="nH2qGiehvEXjNiYqp3bOVtAYv....",
                                                    ),
                                                    "live_time": openapi.Schema(
                                                        type=openapi.TYPE_STRING,
                                                        format=openapi.FORMAT_DATETIME,
                                                        example="12349679.02",
                                                    ),
                                                },
                                            )
                                        },
                                    ),
                                ],
                            ),
                        )
                    },
                ),
            ),
            401: "Some wink what wrong/ Check you data",
            400: "Bad request",
            500: "Internal server error",
        },
        tags=["person"],
        manual_parameters=[
            openapi.Parameter(
                # https://drf-yasg.readthedocs.io/en/stable/custom_spec.html?highlight=properties
                name="X-CSRFToken",
                title="X-CSRFToken",
                in_=openapi.IN_HEADER,
                type=openapi.TYPE_STRING,
                example="nH2qGiehvEXjNiYqp3bOVtAYv....",
            )
        ],
    )
    async def active(self, request: HttpRequest, pk=0, **kwargs) -> HttpResponse:
        from person.tasks.task_user_is_login import task_user_login

        user = request.user
        data = request.data
        # Validate of data
        response = Response(status=status.HTTP_401_UNAUTHORIZED)
        password = data.get("password").split().__getitem__(0).strip()
        username = data.get("username").split().__getitem__(0).strip()
        try:
            response_validate = await asyncio.gather(
                asyncio.to_thread(self.validate_password, password),
                asyncio.to_thread(self.validate_username, username),
            )

        except Exception as error:
            response.data = {"data": error.args[0]}
            return response
        if not user.is_authenticated and user.is_active:
            try:
                if not user.is_authenticated and None in response_validate:
                    # DATA IS NOT VALIDATED
                    response.data = {
                        "data": "User is authenticated ot data have not corrected"
                    }
                    return response
                hash_password = self.get_hash_password(password)
                # Check exists of user to the both db
                client = RedisOfPerson(db=1)
                user_list: List[dict] = []
                # 1/2 db
                # we see to the redis. If there, we won't find, means that we would be
                # looking to the relational db.
                async for key_one in iterator_get_person_cache(client):
                    # Here is a Radis
                    b_caches_user = await client.get(key_one)
                    caches_user = json.loads(b_caches_user.decode())
                    # check username
                    if (
                        caches_user
                        and isinstance(caches_user, dict)
                        and caches_user.__getitem__("username") == username
                    ):
                        # We do actively for user when found his to the cache.
                        caches_user["is_active"] = True
                        user_list.append(caches_user)
                        break
                await client.aclose()
                if len(user_list) == 0:
                    # Redis, didn't give for us anything, and we go to the relational db.
                    user_list: List[U] = [
                        view async for view in Users.objects.filter(username=username)
                    ]
                    user_one = user_list.__getitem__(0).__getattribute__("id")
                    # RUN THE CELERY's TASK - Update CACHE's USER. CHECK the  async_task_user_login by steps!!
                    task_user_login.apply_async(kwargs={"user_id": user_one})
                    # we do actively for user when found his to the Users's model
                    user_list[0].is_active = True
                    serializ = AsyncUsersSerializer(user_list[0])
                    res = await sync_for_async((lambda: serializ.data))
                    user_list = [res.copy()]
                if len(user_list) == 0:
                    response.data = {"data": "User was not found."}
                    response.status_code = status.HTTP_404_NOT_FOUND
                    return response
            except Exception as error:
                # SERVER HAS ERROR
                response.data = {"data": error.args[0]}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
            user_one = user_list.__getitem__(0)
            # Check password of user
            if type(user_list) == List[U]:
                if not (user_one.__getattribute__("password") == hash_password):
                    log.error("Invalid password")
                    return response
                # RUN THE CELERY's TASK
                task_user_login.apply_async(
                    kwargs={"user_id": user_one.__getattribute__("id")}
                )
            # GET AUTHENTICATION (USER SESSION) IN DJANGO
            kwargs = {"username": username, "password": hash_password}
            user = await asyncio.to_thread(get_object_or_404, Users, **kwargs)
            request.__setattr__("user", user)
            # SET, Caching a new session & person of user.
            kwargs = {"user": user, "db": 1}
            task1 = asyncio.create_task(
                self._async_caching(
                    f"user:{user.__getattribute__("id")}:person", **kwargs
                )
            )

            if user is not None:
                request.user = user
                await asyncio.to_thread(login_user, request, user=user)

            kwargs.__setitem__("db", 0)
            task2 = asyncio.create_task(
                self._async_caching(
                    f"user:{user.__getattribute__('id')}:session", **kwargs
                )
            )

            try:
                """
                Cashing of user's session
                """
                b = Binary()
                session_key_user_str: str = b.str_to_binary(
                    f"user:{user.__getattribute__('id')}:session"
                ).decode()
                coockie = Cookies(session_key_user_str, response)
                response: HttpResponse = coockie.session_user()
            except Exception as error:
                log.error(
                    "%s: CACHE OF USER is invalid. ERROR => %s"
                    % (UserViews.__class__.__name__ + self.login.__name__, error)
                )
            try:
                # GET ACCESS TOKENS
                accesstoken = AccessToken(user)
                tokens = await accesstoken.async_token()
                current_time = datetime.now()
                access_time = (SIMPLE_JWT.__getitem__("ACCESS_TOKEN_LIFETIME")).seconds
                refresh_time = (
                    SIMPLE_JWT.__getitem__("REFRESH_TOKEN_LIFETIME") + current_time
                ).timestamp() + time.time()

            except Exception as ex:
                return Response({"data": ex.args}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                """BELOW IS TASKS"""

                # Get properties of user for publication
                def task_get_user_prop(item_list: list) -> dict:
                    return {
                        k: v for k, v in item_list[0].items() if k not in ["password"]
                    }

                # Token base64
                def task_get_usertoken(item) -> str:
                    access_binary = Binary()
                    access_base64_binary = access_binary.object_to_binary(
                        item.access_token
                    )
                    return base64.b64encode(access_base64_binary).decode()

                """RUN TASKS: access & refresh token base64 & user properties"""
                result_list = await asyncio.gather(
                    asyncio.to_thread(task_get_usertoken, tokens),
                    asyncio.to_thread(task_get_usertoken, tokens),
                    asyncio.to_thread(task_get_user_prop, user_list),
                    task1,
                    task2,
                )

                data = {
                    "data": [
                        {
                            "user": {**result_list[2]},
                            "access": {
                                "token_access": (
                                    result_list[0] if len(result_list) > 0 else ""
                                ),
                                "live_time": access_time,
                            },
                            "refresh": {
                                "token_refresh": (
                                    result_list[1] if len(result_list) > 1 else ""
                                ),
                                "live_time": refresh_time,
                            },
                        }
                    ]
                }
                JsonResponse.cookies = response.cookies
                return JsonResponse(data=data, safe=False, status=status.HTTP_200_OK)
            except Exception as error:
                return Response(
                    {"data": error.args.__getitem__(0)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        response.data = {"data": "User have was activated before"}
        return response

    @staticmethod
    def get_hash_password(password: str) -> str:
        """
        This method for hashing user password.
        :param password: Password of user before hashing (from request)
        :return: password hashed
        """
        try:
            # HASH PASSWORD OF USER
            hash = Hasher()
            salt = SECRET_KEY_DJ.replace("$", "/")
            hash_password = hash.hashing(password, salt)
            return hash_password
        except Exception as error:
            raise ValueError(error)

    @staticmethod
    async def serializer_validate(serializer):
        is_valid = await asyncio.create_task(asyncio.to_thread(serializer.is_valid))
        if not is_valid:
            raise serializers.ValidationError(serializer.errors)

    @staticmethod
    def validate_username(value: str) -> None | object:
        regex = re.compile(r"(^[a-zA-Z]\w{3,50}_{0,2})")
        return regex.match(value)

    @staticmethod
    def validate_password(value: str) -> None | object:
        regex = re.compile(r"([\w%]{9,255})")
        return regex.match(value)

    @staticmethod
    async def _async_caching(key: str, **kwargs) -> bool:
        """
        by default:
        - host: str = f"{DB_TO_RADIS_HOST}",
        - port: int = 6380,
        - db: Union[str, int] = 1 (db from redis. 1 - it's cache params of user. 0 - it's cache session of user ),

        Redis's cache
        Session of user saving in cache's session db (Redis 0). "kwargs={'user': <Users's object >}

        Caching of user's db in cache's db (Redis 1). Below, it's cache's db.
        Now will be saving on the 27 hours.
        'task_user_from_cache' task wil be to upgrade postgres at ~ am 01:00
        Timetable look the 'project.celery.app.base.Celery.conf'
        :param str key: This is key element, by key look up where it will be saved. Example: "user:25:person"

        :param kwargs: {'user': < user_object >, "db": < integer it's 0 or 1>}
        :return: bool. If returning the True, it means all OK/ If the False, - not OK and look the log's file.
        """
        db_numb: int = kwargs.__getitem__("db")
        client = RedisOfPerson(db=db_numb)
        if not client.ping():
            return False
        try:
            kwargs = {"user": kwargs.__getitem__("user")}
            await client.async_set_cache_user(key=key, **kwargs)
            return True
        except Exception as error:
            log.error(
                "%s: CACHE OF USER is invalid. ERROR => %s"
                % (UserViews.__class__.__name__ + UserViews.login.__name__, error)
            )
            return False
        finally:
            await client.aclose()
