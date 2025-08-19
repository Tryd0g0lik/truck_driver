import base64
import pickle
from typing import Generic, List
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

from person.interfaces import U
from person.models import Users
from typing import Optional, Dict


class AccessToken(JWTAuthentication):
    def __init__(self, user_object: Optional[Users] = None):
        self.user_object = user_object

    async def async_token(self):
        """
        This is method for getting token for user.
        :param user_object: This is a user's object for a which will be token generating \
        :return: this dictionary with 4 values
        :return: {
                {"token_access": "< access_token >", "live_time": "< life_time_of_token >"},
                {"token_refresh": "< refresh_token >", "live_time": "< life_time_of_token >"}
            }
        """
        if not self.user_object:
            raise ValueError("Invalid user")
        tokens = await self.__async_generate_jwt_token(self.user_object)
        return tokens

    @staticmethod
    async def __async_generate_jwt_token(
        user_object: Optional[Users],
    ) -> {Dict[str, str]}:
        """
            Only, after registration user we will be generating token for \
            user through 'rest_framework_simplejwt.serializers.TokenObtainPairSerializer'
            This is a generator token of user.\
            The 'SIMPLE_JWT' is variable from the project's 'settings.py' file.\
            @SIMPLE_JWT.ACCESS_TOKEN_LIFETIME this is minimum quantity for life of token\
             It is for the access.\
            @REFRESH_TOKEN_LIFETIME this is maximum quantity fro life token. \
            It is for the refresh.
            'TokenObtainPairSerializer' it has own db/
            :return:
        """
        """GET TOKEN"""
        try:
            token = TokenObtainPairSerializer.get_token(user_object)
            token["name"] = (lambda: user_object.username)()
            return token
        except Exception as ex:
            raise ValueError("Value Error: %s" % ex)

    async def get_user_from_token(self, request) -> type(Users):
        """
        This method is used for getting the user object from the token.
        """
        bytes_token: bytes = None
        """GET TOKENS FROM THE HEADERS"""
        origin_token_access = request.META.get("HTTP_ACCESSTOKEN").split(" ")[1]
        if not origin_token_access:
            raise ValueError("Invalid token")

        if origin_token_access:
            try:
                bytes_token = self.string_to_byte_tokens(origin_token_access)
            except Exception as error:
                raise AuthenticationFailed(error)
        if not bytes_token:
            raise ValueError("Invalid token")
        # """GET USER ID AND USER NAME"""
        obj = pickle.loads(bytes_token)
        user_id = obj.payload["user_id"]
        user_name = obj.payload["name"]
        try:
            user_list: List[U] = [
                view
                async for view in Users.objects.filter(
                    id=int(user_id), username=user_name
                )
            ]
            if len(user_list) != 0:
                return user_list
            raise AuthenticationFailed("Invalid token")
        except Exception as error:
            raise AuthenticationFailed(error)

    @staticmethod
    def string_to_byte_tokens(string: str) -> bytes:
        """
        This method for converting from string to bytes
        :param string: string for convert to bytes
        :return: byte string
        """
        try:
            byte_string = base64.b64decode(string)
            return byte_string
        except Exception as ex:
            raise ValueError(f"Error converting to bytes: {ex}")
