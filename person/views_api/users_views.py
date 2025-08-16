"""
person/views_api/users_views.py
"""

import logging
import asyncio
import re

from typing import Any
from collections.abc import Callable
from kombu.exceptions import OperationalError

from django.db import connections
from django.http import HttpRequest
from rest_framework.response import Response
from rest_framework import serializers, status
from adrf.viewsets import ViewSet

from django.contrib.auth.models import Group
from person.apps import signal_user_registered
from person.tasks.task_cache_hew_user import task_postman_for_user_id
from person.models import Users
from person.hasher import Hasher
from person.views_api.redis_person import RedisOfPerson
from person.views_api.serializers import AsyncUsersSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from dotenv_ import SECRET_KEY_DJ

from logs import configure_logging
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)
configure_logging(logging.INFO)


async def sync_for_async(fn: Callable[[Any], Any], *args, **kwargs):
    return await asyncio.create_task(asyncio.to_thread(fn, *args, **kwargs))


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
                % (data.get("username"), data.get("email"))
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
        TODO: validate for the user's email need add
        :param request:
        :return:
        """
        user = request.user
        data = request.data
        try:
            # Validators
            check_validate = [self.validate_username(data.get("username"))]
            check_validate.append(self.validate_password(data.get("password")))
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
            # RESPONSE WILL SEND. CODE 401
            response.data = {"data": error.args}
            response.status_code = status.HTTP_401_UNAUTHORIZED
            return response

        if not user.is_authenticated and len(users_list) == 0:
            # Open transaction
            try:
                password_hes = self.get_hash_password(data.get("password"))
                serializer = AsyncUsersSerializer(data=data)
                # CHECK - VALID DATA
                await self.serializer_validate(serializer)
                serializer.validated_data["password"] = password_hes
                await serializer.asave()

                data: dict = dict(serializer.data).copy()
                group_list = [
                    view
                    async for view in Group.objects.filter(
                        name=serializer.data.get("category")
                    )
                ]
                if len(group_list) > 0:
                    user_new = [
                        view async for view in Users.objects.filter(pk=data.get("id"))
                    ]
                    add = user_new[0].groups.add
                    # Below, is my synct_to_async (not from django).
                    await sync_for_async(add, *group_list)
                    user_new[0].is_active = False
                    await user_new[0].asave()
                # # RUN THE TASK - Update CACHE's USER -send id to the redis from celer's task

                res = task_postman_for_user_id.delay((data.__getitem__("id"),))
                print(res.status)
                # (threading.Thread(
                #     target=delay, args=(data.__getitem__("id"),), daemon=True
                # )).start()

            except (OperationalError, Exception) as error:
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
                response.data = {"data": error.args.__getitem__(0)}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response

        response.data = {"data": "User was created before."}
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
