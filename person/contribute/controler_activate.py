"""
person/contribute/controler_activate.py
This a function for control an authentication (from registrasion). \
This is, when, the user \
makes registration on the site.\
The 'send_activation_notificcation' from 'app.py' makes sending \
the email-message \
to the user email. \
Email contains the tokken-link. When user presses by the token-link, this run \
the function (below).
Срабатывает по запросы урла который содержит подпись

"""

from datetime import datetime, timezone
import asyncio
from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.core.signing import BadSignature
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import status
from person.contribute.sessions import create_signer
from person.contribute.utilite import signer
from person.models import Users
from dotenv_ import (
    URL_REDIRECT_IF_GET_AUTHENTICATION,
    URL_REDIRECT_IF_NOTGET_AUTHENTICATION,
)
from person.tasks.task_user_is_authenticate import task_user_authenticate
from project.settings import SESSION_COOKIE_AGE


def user_activate(request, sign):
    """
    From the *_user/serializers.py::UserSerializer.create the message \
(contain referral link) go out to the user's email.\
\
Function changes the 'sign' of signer from the url 'activate/<str:sign>'.\
If all is OK,  we get the 301 code by \
the var 'URL_REDIRECT_IF_GET_AUTHENTICATION'. Plus, variables:
- user.is_active = True
- user.is_activated = True (of table 'Users').
\
Response (of HttpResponseRedirect)  has data for the cookie. Data of \
variable `user_session_{id}` and 'is_staff__{id}'. It is \
more info in README::COOKIE.
1. The user is registered on the site.\
2. The function is `send_activation_notification` from` app.py` sends \
an email with a tkene link to the user email address.\
3. The user presses on a token link.\
4. The function is `user_activate`.\
5. The function `user_activate` processes the URL requests \
containing a signature.\
6. The function accepts two parameters: `request` and` sign`. The `sign` \
parameter is a signature from the URL` Activate/<Str: Sign> `.\
7. The function is trying to decipher the signature and get the user name.\
8. If the decoding is successful, the function receives the user's object from\
 the database.\
9. If the user is already activated, the function returns a redirection with \
code 301.\
10. Otherwise, the function activates the user, sets the appropriate values
 in the user object and creates a user session.\
11. The function sets cuckoos for the user session and redirects the user to\
 the activation page.\
12. If an error occurs, the function returns redirecting with a code of 400.\
    :param request:\
    :param sign: str. It is 'sign' of signer from the url 'activate/<str:sign>'
    :return:
    """
    _text = f"[{user_activate.__name__}]:"
    username = ""
    try:
        sign = str(sign).replace("_null_", ":")
        """
        person/urls.py
        After sent the letter to the user's email, we receiving the 'sign' param.
        After, getting the the sign, it's value user's email(or username) in hash we getting
        a string of email(or username).
        """
        username += signer.unsign(sign)
    except BadSignature as e:
        _text = " %s Mistake => 'BadSignature': %s", (_text, e)
        # https://docs.djangoproject.com/en/5.1/ref/request-response
        # /#httpresponse-objects

        # REDIRECT IF ALL BAD
        return HttpResponseRedirect(
            redirect_to=f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}",
            status=status.HTTP_400_BAD_REQUEST,
        )
    # https://docs.djangoproject.com/en/5.1/topics/http
    # /shortcuts/#get-object-or-404
    try:
        """ "
        Get object from db or 404 status-code.
        We are checking user.
        Below, we will be change the active status of user.
        """
        user: Users | None = get_object_or_404(Users, username=username)
        try:
            _text = "%s Get 'user': %s", (_text, user.__dict__.__str__())
            # logging, it if return error
        except Exception as e:
            _text = " %s Get 'user': %s", (_text, e)
        # get the text from the basis value
        _text = (str(_text).split(":"))[0] + ":"
        # CHECK OF ACTIVATED
        if not user or user.is_active:
            _text = (
                " %s the object 'user' has 'True' value \
from 'is_activated'. Redirect. 301",
                _text,
            )
            response = HttpResponseRedirect(
                redirect_to=f"{URL_REDIRECT_IF_NOTGET_AUTHENTICATION}",
                status=status.HTTP_400_BAD_REQUEST,
            )
            return response
        _text = (
            "Mistake: %s ",
            _text,
        )

        task_user_authenticate.apply_async(
            kwargs={"user_id": user.__getattribute__("id")}
        )

        # if user_authenticate is not None:
        if user.__setattr__("id", True):
            login(request, user)
        # CREATE SIGNER
        user_session = create_signer(user)
        cache.set(
            f"user_session_{user.__getattribute__("id")}",
            user_session,
            SESSION_COOKIE_AGE,
        )
        """ New object has the `user_session_{id}` variable"""
        redirect_url = f"{request.scheme}://{request.get_host()}{URL_REDIRECT_IF_GET_AUTHENTICATION}"
        response = HttpResponseRedirect(redirect_url)
        return response

    except Exception as e:
        _text = f"{_text} Mistake => {str(e)}"
        # :-(
        return HttpResponseRedirect(
            redirect_to=f"{request.scheme}://{request.get_host()}/",
            status=400,
        )
