from http.client import responses

from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from adrf.views import APIView
from drf_yasg import openapi
from typing import Coroutine


class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="csrf-token",
        tags=["csrf"],
        responses={
            200: openapi.Response(
                description="CSRF токен",
                headers={
                    "Set-Cookie": openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="CSRF token cookie",
                        example="csrftoken=GiehvEXjNiYqp3bOVtA...; Path=/; Secure; HttpOnly; SameSite=Lax",
                    ),
                },
            ),
        },
    )
    async def get(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponse | JsonResponse:
        if request.method == "GET":
            token = get_token(request)
            response = JsonResponse({"csrfToken": token})
            response.status_code = status.HTTP_200_OK
            return response
        response = Response(status=status.HTTP_400_BAD_REQUEST)
        response.data = "csrfToken not Ok"
        return response
