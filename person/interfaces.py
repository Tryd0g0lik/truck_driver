from typing import TypeVar, Sequence, List, TypedDict, NotRequired

from person.models import Users

# Determine the Type for Users model
U = Users


class UserData(TypedDict):
    """
    Type for register, login, etc.
    """

    username: str
    password: str
    email: NotRequired[str]


# USER
class InitialUser(TypedDict):
    username: str
    password: str
    email: str
    is_active: bool | None
    is_staff: bool | None
    is_superuser: bool
    date_joined: str | None
    created_at: str | None
    is_verified: bool
    updated_at: str
    is_sent: bool
    balance: int


# FOr cache to the redis
class TypeUser(InitialUser):
    id: int
    first_name: str
    last_name: str | None
    verification_code: bool
