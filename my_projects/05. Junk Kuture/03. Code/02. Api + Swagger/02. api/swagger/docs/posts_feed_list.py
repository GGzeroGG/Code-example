from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status

doc_decorator = swagger_auto_schema(
    responses={
        status.HTTP_401_UNAUTHORIZED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example='User is not authorized',
                    description='Authentication credentials were not'
                                ' provided.',
                ),
            },
        ),
    },
)
