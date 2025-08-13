"""
person/contribute/sessions.py
    HASH for work with the cacher (from session) table of db.
    Look to the settings.py::CACHES
 """

import bcrypt
from django.core.cache import cache
from django.core.signing import Signer

from person.contribute.hashers import hashpw_password
from person.models import Users

signer = Signer()


def create_signer(user: Users) -> str:
    """
    https://docs.djangoproject.com/en/5.2/topics/signing/
    Читать Readme.COOKIE
     Here, user's email be CACHING! It's before sending message/letter to the user for an authentification
    :param user:
    :return:
    """
    hash_bstring = "".encode()
    try:

        s = signer.sign(user.email)
        hash_bstring += hashpw_password(s)
    except Exception as e:
        raise ValueError("Mistake => %s:  %s" % (type(e), str(e))) from e
    finally:
        hash_string = hash_bstring.decode("utf-8")
    return hash_string


def hash_check_user_session(pk: int, session_val: str) -> bool:
    """

    :param int pk Index of single object from db.
    :param str session_val This is a value from the key of session.
    :return:
    """
    # Get b-code
    status_bool = False
    try:
        # GET B-CODE
        res = session_val.encode(encoding="utf-8")
        # Get signer
        user_list = Users.objects.filter(id=pk)
        if len(user_list) != 0:
            s = signer.sign(user_list[0].email)
            # CHECK
            status_bool = bcrypt.checkpw(s.encode("utf-8"), res)
        else:
            raise ValueError(
                "[%s::%s]: \
Mistake => 'user_list' empty. 'pk' invalid."
                % (__name__, hash_check_user_session.__name__),
            )
    except Exception as e:
        raise ValueError(
            "[%s::%s]: \
Mistake => %s: %s"
            % (__name__, hash_check_user_session.__name__, type(e), str(e)),
        ) from e
    return status_bool


def hash_create_user_session(pk: int, session_key: str, live_time: int = 86400):
    """
    Create the hash's value for 'session_key'.
     Time live is 86400 seconds\
     (or 24 hours) This is for the single object from user's db.
    :param int pk Index of single object from db.
    :param str session_key By default is "user_session_{id}".\
    It is the key name/
    :param int live_time: This is a time live for key of session.\
     By the default value is the 86400 hours.
    :return: False means what the updates have can not get or Ture,
    """
    user_list = Users.objects.filter(id=pk)
    if len(user_list) == 0:
        return False
    status_bool = False
    try:
        # GREAT SIGNER
        signer_str = create_signer(user_list[0])

        # SAVE in db the key of session and HASH's value for our key
        session_key = session_key if session_key else f"user_session_{pk}"
        cache.set(session_key, signer_str, live_time)
        status_bool = True
    except Exception as e:
        raise ValueError(
            "[%s::%s]: Mistake => %s: %s"
            % (__name__, hash_create_user_session.__name__, type(e), str(e)),
        ) from e
    return status_bool


def check(session_key: str, session_val: str, **kwargs) -> False:
    """
    Checks the hash from "request.COOKIE.get('user_session_{id}')"  and\
the object single user from db. This the 'single user' take of\
'pk' parameter from the URL.
    :param session_key: 'user_session_{id}'\
    :param str session_val: This the value from \
    "request.COOKIE.get('user_session_{id}')"
    :param kwargs:  We need get the 'pk' parameter from the URL. Index \
of single object from db.)
    :return:
    """

    try:
        if not session_val or not session_key:
            return False
        session_key_value = cache.get(session_key)
        session_key_value_checker = hash_check_user_session(
            kwargs["pk"], session_key_value
        )
        # if not session_key_value or not session_key_value_checker:
        if not session_key_value_checker:
            return False
        return True
    except Exception as e:
        raise ValueError(
            "[%s::%s]: \
Mistake => %s: %s"
            % (__name__, check.__name__, type(e), str(e)),
        ) from e


def update(pk: int, session_key: str, live_time: int = 86400):
    """"
    TODO: Create the new value for 'user_session_{id}'. \
     Time live is 86400 seconds \
     (or24 hours) This is for the single object from user's db.
    :param int pk: Index of single object from db.
    :param str session_key: It is the key name
    :param int live_time: This is a time live for session key. By the default \
value is the 86400 hours.
    :return: False means what the updates have can not get or Ture,
    """
    status_bool = False
    try:
        status_bool = hash_create_user_session(pk, session_key, live_time)
    except Exception as e:
        raise ValueError(
            "[%s::%s]: Mistake => %s: %s" % (__name__, update.__name__, type(e), str(e))
        ) from e
    return status_bool
