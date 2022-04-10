from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from ..base import unauthorized_response, forbidden_response

doc_decorator = swagger_auto_schema(
    responses={
        **unauthorized_response,
        **forbidden_response,
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'farmers_count': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
                'farmers_conventional_count': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
                'aggregated_data': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
            },
        ),
    },
)
