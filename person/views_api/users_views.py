import base64
import json
import time
import asyncio
import re
from datetime import datetime
from typing import Any
from django.db import connections
from django.http import JsonResponse, HttpRequest, HttpResponse
from rest_framework.response import Response
from rest_framework import serializers, status
from adrf.viewsets import ViewSet
from person.apps import signal_user_registered
from person.tasks.task_cache_hew_user import task_postman_for_user_id
from person.models import Users
from person.views_api.redis_person import RedisOfPerson
from person.views_api.serializers import (
    AsyncUsersSerializer
)
from drf_yasg.utils import swagger_auto_schema


from project.settings import SIMPLE_JWT
from person.binaries import Binary
import logging
from logs import configure_logging
from dotenv import load_dotenv
def new_connection(data) -> list:
    """
    new user cheks on the duplicate
    :param data:
    :return:
    """
    with connections["default"].cursor() as cursor:
        cursor.execute(
            """SELECT * FROM person_users WHERE username = '%s' AND email = '%s';"""
            % (data.get("username"), data.get("email"))
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
    async def create(self, request: HttpRequest) -> type(Response):
        user = request.user
        data = request.data
        response = Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            # sync to async - user's checker on the duplicate
            users_list: list[Users.objects] = await asyncio.create_task(
                asyncio.to_thread(new_connection, data=data)
            )

        except Exception as error:
            # RESPONSE WILL SEND. CODE 500
            response.data = {"data": error.args}
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response
        # Condition - If the length of the users_list has more zero, it's mean what user has a duplicate.
        # Response will be return 401.
        if not user.is_authenticated and len(users_list) == 0:
            try:
                password_hes = self.get_hash_password(data.get("password"))
                serializer = AsyncUsersSerializer(data=data)
                # CHECK - VALID DATA
                await self.serializer_validate(serializer)
                serializer.validated_data["password"] = password_hes
                await serializer.asave()
                data: dict = dict(serializer.data).copy()
                # # RUN THE TASK - Update CACHE's USER -send id to the redis from celer's task
                task_postman_for_user_id.delay((data.__getitem__("id"),))
            except Exception as error:
                # RESPONSE WILL BE TO SEND. CODE 500
                response.data = {"data": error.args}
                response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                return response
            # RESPONSE WILL BE TO SEND. CODE 200
            response.data = {"data": "OK"}
            try:
                if serializer.data.__getitem__("id"):
                    user_id_list = [
                        view async for view in Users.objects.filter(pk=data["id"])
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

