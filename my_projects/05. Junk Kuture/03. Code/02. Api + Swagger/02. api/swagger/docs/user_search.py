from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status

from services.api.swagger.doc_templates.models.user.fields import \
    docs_user_fields

doc_decorator = swagger_auto_schema(
    responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                    ),
                    'name': openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    'username': openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    'type': openapi.Schema(
                        title='Account type',
                        type=openapi.TYPE_STRING,
                        enum=[
                            'creator',
                            'educator',
                            'fan',
                        ],
                    ),
                    **docs_user_fields['avatar_small'],
                },
            ),
        ),
        status.HTTP_401_UNAUTHORIZED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'not_authenticated': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example='User is not authorized',
                    description='Happens if the user is not logged in.',
                ),
            },
        ),
    },
)
