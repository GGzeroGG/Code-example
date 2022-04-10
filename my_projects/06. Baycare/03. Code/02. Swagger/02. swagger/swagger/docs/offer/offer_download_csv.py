from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from ..base import unauthorized_response

doc_decorator = swagger_auto_schema(
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'bate_csv': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='base64',
                ),
            },
        ),
        **unauthorized_response,
    },
)
