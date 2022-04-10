from drf_yasg import openapi

from rest_framework import status

status_401_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(
            type=openapi.TYPE_STRING,
            example='User is not authorized',
            description='Authentication credentials were not'
                        ' provided.',
        ),
    },
)

status_401_response = {
    status.HTTP_401_UNAUTHORIZED: status_401_schema,
}
