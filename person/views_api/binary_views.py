import json
import logging

from adrf.views import APIView
from adrf.viewsets import ViewSet
from django.contrib.auth.models import AnonymousUser
from rest_framework import status

# from rest_framework.response import (
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.request import Request

from logs import configure_logging
from person.binaries import Binary
from person.interfaces import U
from person.permissions import is_active, is_all

# from person.permissions import IsAll get_extra_actions
log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class BinaryViews(ViewSet):

    async def str_to_binary(self, request: Request) -> JsonResponse | Response:
        data = request.data
        # if is_active(request) and is_all(request):
        try:
            binary = Binary()
            result = binary.str_to_binary(json.loads(data["string"])[0])
            response_dict: dict = {"str_to_binary": result}
            response = Response(data=response_dict, status=status.HTTP_200_OK)
            return response
        except Exception as error:
            log.error(error.args[0])
            return Response(
                {"data": error.args[0]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
