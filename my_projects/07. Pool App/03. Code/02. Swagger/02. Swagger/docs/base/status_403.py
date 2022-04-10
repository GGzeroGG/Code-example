from drf_yasg import openapi

from rest_framework import status

status_403_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(
            type=openapi.TYPE_STRING,
            example='You do not have permission to perform this action.',
            description='User is authenticated, '
                        'but not authorized to perform this action',
        ),
    },
)

status_403_response = {
    status.HTTP_403_FORBIDDEN: status_403_schema,
}
