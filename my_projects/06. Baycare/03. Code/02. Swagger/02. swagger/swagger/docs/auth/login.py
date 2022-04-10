from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.serializers.auth import LoginRequestSerializer
from ..base import validation_error_response


doc_decorator = swagger_auto_schema(
    request_body=LoginRequestSerializer,
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            description='User successfully logged in',
            properties={
                'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                'expires_in': openapi.Schema(type=openapi.TYPE_INTEGER),
                'token_type': openapi.Schema(type=openapi.TYPE_STRING),
                'scope': openapi.Schema(type=openapi.TYPE_STRING),
                'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'type': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        **validation_error_response,
    },
)
