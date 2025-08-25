import threading
import base64
import logging
import asyncio
from django.http import HttpRequest
from django.contrib.auth.models import AnonymousUser


from person.binaries import Binary
from person.models import Users
from person.views_api.redis_person import RedisOfPerson


from logs import configure_logging


log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class RedisAuthMiddleware:
    # https://docs.djangoproject.com/en/4.2/topics/http/middleware/#:~:text=Middleware
    def __init__(self, get_response):
        # super().__init__(get_response)
        self.get_response = get_response
        self.client = None
        self.user_key = ""

    async def async_get_user(
        self, request: HttpRequest, session_key: str
    ) -> AnonymousUser | Users:

        self.client = RedisOfPerson(db=0)
        try:
            b = Binary()

            b_session_key = b.binary_to_str(session_key)
            user_obj = b.binary_to_object(b_session_key)

            redis_key = f"user:{user_obj["user_id"]}:session"
            redis_key_bool = await self.client.async_has_key(redis_key)
            if not redis_key_bool:
                return AnonymousUser()
            session_data = await self.client.async_get_cache_user(redis_key)
            b = Binary()
            user_obj = b.binary_to_object(
                base64.b64decode(session_data.__getitem__("b_user"))
            )
            if user_obj and not isinstance(user_obj, AnonymousUser):
                request.user = user_obj
                request.user.is_active = True

            return user_obj
        except ValueError as error:
            log.error(
                "%s: ERROR => %s"
                % (
                    RedisAuthMiddleware.__class__.__name__
                    + "."
                    + self.async_get_user.__name__,
                    error.args[0],
                )
            )
            return AnonymousUser()
        finally:
            await self.client.aclose()

    def __call__(self, request: HttpRequest) -> HttpRequest:
        """
        Here is we checking the user's session key in cookies.By this key we will get the cache of user's object.
        The cache of user's object it is JSON str 'session: {"user": < binary code Users's object >}' < === > 'cockie_key: {key: binary data}'.
        :param HttpRequest request:
        :return:
        """
        try:
            log.info(
                "%s: SESSION_KEY 'session_user': %s"
                % (
                    RedisAuthMiddleware.__class__.__name__
                    + "."
                    + self.async_get_user.__name__,
                    request.COOKIES.get("session_user"),
                )
            )
            if request.COOKIES and request.COOKIES.get("session_user"):
                if not hasattr(request, "user"):
                    request.user = AnonymousUser()
                session_key = request.COOKIES["session_user"]
                # self.async_get_user(session_key)
                asyncio.run(self.async_get_user(request, session_key))

        except Exception as error:
            log.error(
                "%s: %s"
                % (
                    RedisAuthMiddleware.__class__.__name__ + self.__call__.__name__,
                    list(error.args).__getitem__(0),
                )
            )

        response = self.get_response(request)

        return response
