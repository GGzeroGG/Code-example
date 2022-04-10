from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.swagger.doc_templates.models.comment.sets.comment import (
    docs_comment_set,
)
from services.api.swagger.doc_templates.models.user.sets.user_comment import (
    docs_user_comment_set,
)


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
        status.HTTP_400_BAD_REQUEST: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    description='fasting does not exist',
                ),
            },
        ),

        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                **docs_comment_set,
                'user': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        **docs_user_comment_set,
                    },
                ),
            },
        ),
    },
)
