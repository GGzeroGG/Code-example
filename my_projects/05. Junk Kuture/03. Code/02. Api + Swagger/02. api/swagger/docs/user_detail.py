from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status

from services.api.swagger.doc_templates.models.post.sets.post import (
    docs_post_set,
)
from services.api.swagger.doc_templates.models.region.sets.region import (
    docs_region_set,
)
from services.api.swagger.doc_templates.models.user.sets.user import (
    docs_user_set,
)
from services.api.swagger.doc_templates.models.user.special_fields import (
    docs_special_user_fields,
)


doc_decorator = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter(
            'latest_posts', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
            default=0, description='max value == 30',
        ),
    ],
    responses={
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
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'region': openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        **docs_region_set,
                    },
                ),
                **docs_user_set,
                **docs_special_user_fields['total_posts'],
                **docs_special_user_fields['is_followed'],
                'posts': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            **docs_post_set,
                        },
                    ),
                ),
            },
        ),
        status.HTTP_404_NOT_FOUND: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_not_exist': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example='User with this id does not exist',
                    description='Invalid id',
                ),
            },
        ),
    },
)
