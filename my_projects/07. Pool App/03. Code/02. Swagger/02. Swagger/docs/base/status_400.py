from drf_yasg import openapi

from rest_framework import status
from rest_framework.settings import api_settings

status_400_schema = openapi.Schema(
    'Validation Error',
    type=openapi.TYPE_OBJECT,
    properties={
        api_settings.NON_FIELD_ERRORS_KEY: openapi.Schema(
            description='List of validation errors not related to any field',
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(type=openapi.TYPE_STRING),
        ),
    },
    additional_properties=openapi.Schema(
        description=(
            'A list of error messages for each field that triggered a validation error'  # noqa: E501
        ),
        type=openapi.TYPE_ARRAY,
        items=openapi.Schema(type=openapi.TYPE_STRING),
    ),
)

status_400_response = {
    status.HTTP_400_BAD_REQUEST: status_400_schema,
}
