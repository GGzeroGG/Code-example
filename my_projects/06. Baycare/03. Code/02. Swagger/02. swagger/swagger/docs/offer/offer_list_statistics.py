from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from .offer_list_filters_doc import offers_list_filters_doc
from ..base import unauthorized_response

doc_decorator = swagger_auto_schema(
    manual_parameters=offers_list_filters_doc,
    responses={
        **unauthorized_response,
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'offers_count': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
                'offers_confirmed_count': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
                'farmers_conventional_count': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
                'farmers_organic_count': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                ),
            },
        ),
    },
)
