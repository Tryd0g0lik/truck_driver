from http.client import responses

from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from rest_framework.permissions import AllowAny
from rest_framework.request import HttpRequest
from rest_framework.response import Response
from rest_framework import status
from adrf.views import APIView
from typing import Coroutine


class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

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
