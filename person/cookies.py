"""
cloud/cookies.py
"""

from django.core.cache import cache
from django.http import HttpResponse

from project.settings import (
    SESSION_COOKIE_AGE,
    SESSION_COOKIE_HTTPONLY,
    SESSION_COOKIE_SAMESITE,
    SESSION_COOKIE_SECURE,
)


class Cookies:
    """
    Cookies
    """

    def __init__(self, session_key_user: str, response: HttpResponse):
        """

        :param str session_key_user: It's cookie's key by which can be will find needed content
        :param HttpResponse response:
        """
        self.response = response
        self.session_key_user = session_key_user

    def session_user(
        self,
        max_age_=SESSION_COOKIE_AGE,
        httponly_=True,
        secure_="true" if SESSION_COOKIE_SECURE else "false",
        samesite_=SESSION_COOKIE_SAMESITE,
    ) -> HttpResponse:
        self.response.set_cookie(
            "session_user",
            self.session_key_user,
            max_age=max_age_,
            httponly=httponly_,
            secure=secure_,
            samesite=samesite_,
        )
        return self.response

    def All(self, is_staff: bool, is_active: bool) -> HttpResponse:
        self.user_session(self.session_key_user)
        self.is_staff(is_staff)
        self.is_active(is_active)
        self.user_index(self.session_key_user)
        return self.response
