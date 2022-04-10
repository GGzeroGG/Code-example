from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status

from services.api.swagger.doc_templates.models.post.sets.post import \
    docs_post_set
from services.api.swagger.doc_templates.models.user.sets.user_small import \
    docs_user_small_set

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
                'images': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    description='if the number of pictures exceeds 5 this '
                                'error will be caused',
                ),
                'not_field_error': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_STRING,
                    ),
                    description='if the user account type is not educator '
                                'or creator this error will be raised',
                ),
            },
        ),

        status.HTTP_201_CREATED: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                **docs_post_set,
                'user': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        **docs_user_small_set,
                    },
                ),
            },
        ),
    },
)
