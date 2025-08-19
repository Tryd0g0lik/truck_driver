# REGISTRATION
from person.models import Users
from rest_framework import serializers
from adrf.serializers import ModelSerializer


class AsyncUsersSerializer(ModelSerializer):
    """
    This is the basis serialize of 'person/views_api/users_views.py::UserViews'
    """

    class Meta:
        model = Users
        # fields = [
        #     "id",
        #     "username",
        #     "first_name",
        #     "last_name",
        #     "email",
        #     "password",
        #     "category",
        #     "date_joined",
        # ]
        fields = "__all__"


class CacheUsersSerializer(serializers.ModelSerializer):
    """
    This serializer for caching a new user. This when it on level registration.
    Data from serializer send to the redis
    """

    class Meta:
        model = Users
        fields = "__all__"
