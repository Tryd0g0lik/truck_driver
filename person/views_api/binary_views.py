"""
person/views_api/binary_views.py
"""

import base64
import logging
from adrf.viewsets import ViewSet
from rest_framework import status

from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.request import Request

from logs import configure_logging
from person.binaries import Binary

log = logging.getLogger(__name__)
configure_logging(logging.INFO)


class BinaryViews(ViewSet):
    binary = Binary()

    async def str_to_binary(self, request: Request) -> JsonResponse | Response:
        data = request.data
        if request.headers["User-Agent"].startswith("AsyncHttpClient/1.0"):
            try:

                result = self.binary.str_to_binary(data["data"][0])
                response_dict: dict = {"data": result}
                response = Response(data=[response_dict], status=status.HTTP_200_OK)
                return response
            except Exception as error:
                log.error(f"{self.str_to_binary.__name__}{error.args[0]}")
                return Response(
                    {"data": error.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response({"data": []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def binary_to_object(self, request: Request) -> JsonResponse | Response:
        data = request.data
        if request.headers["User-Agent"].startswith("AsyncHttpClient/1.0"):
            try:
                result = self.binary.binary_to_object(
                    base64.b64decode(data.__getitem__("b_user"))
                )
                return Response(data=[result], status=status.HTTP_200_OK)
            except Exception as error:
                log.error(f"{self.str_to_binary.__name__}{error.args[0]}")
                return Response(
                    {"data": error.args}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response({"data": []}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
