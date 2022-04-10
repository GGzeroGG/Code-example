from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.swagger.docs.base.status_401 import status_401_response
from services.api.swagger.docs.base.status_403 import status_403_response

doc_decorator = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'view_all', openapi.IN_QUERY, type=openapi.TYPE_STRING,
            description='The filter is responsible for what part of the '
                        'records to output | '
                        'False - withdraw 1 part | True - withdraw 2 part'
                        'default=False | Available Values: False, True',
        ),
        openapi.Parameter(
            'buy', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN,
            description='Depending on the value of the filter it will show '
                        'either bought or sold shares '
                        'True - purchased and pre-orders '
                        'False - sold',
        ),
    ],

    responses={
        **status_401_response,
        **status_403_response,

        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'count': openapi.Schema(type=openapi.TYPE_NUMBER),
                    'results': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(
                                    type=openapi.TYPE_NUMBER,
                                ),
                                'count_shares': openapi.Schema(
                                    type=openapi.TYPE_NUMBER,
                                ),
                                'price': openapi.Schema(
                                    type=openapi.FORMAT_DECIMAL,
                                ),
                                'created_timestamp': openapi.Schema(
                                    type=openapi.FORMAT_DATETIME,
                                ),
                                'artist': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'photo': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                        ),
                                        'name': openapi.Schema(
                                            type=openapi.TYPE_STRING,
                                        ),
                                    },
                                ),
                                'price_sum': openapi.Schema(
                                    type=openapi.FORMAT_DATETIME,
                                ),
                                'is_preorder': openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN,
                                ),
                            },
                        ),
                    ),
                },
            ),
        ),
    },
)
