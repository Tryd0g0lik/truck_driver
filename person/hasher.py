from django.contrib.auth.hashers import (
    make_password,
    PBKDF2PasswordHasher,
)


class Hasher(PBKDF2PasswordHasher):
    """
    <algorithm>$<iterations>$<salt>$<hash>
    https://docs.djangoproject.com/en/5.2/topics/auth/passwords/
    """

    def hashing(selfself, password, salt_, iterations=None):
        hasher_password = make_password(password, salt=salt_)
        return hasher_password
