from drf_yasg import openapi

from rest_framework import status

status_404_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Invalid pk or object not found due to search filter',
        ),
    },
)

status_404_response = {
    status.HTTP_404_NOT_FOUND: status_404_schema,
}
