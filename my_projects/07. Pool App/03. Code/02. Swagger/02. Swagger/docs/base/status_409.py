from drf_yasg import openapi

from rest_framework import status

status_409_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'non_field_errors': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_STRING,
            ),
        ),
    },
)

status_409_response = {
    status.HTTP_409_CONFLICT: status_409_schema,
}
