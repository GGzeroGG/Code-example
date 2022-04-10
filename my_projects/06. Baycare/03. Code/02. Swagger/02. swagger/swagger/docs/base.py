from drf_yasg import openapi

from rest_framework import status
from rest_framework.settings import api_settings


validation_error_schema = openapi.Schema(
    'Validation Error',
    type=openapi.TYPE_OBJECT,
    properties={
        api_settings.NON_FIELD_ERRORS_KEY: openapi.Schema(
            description='List of validation errors not related to any field',
            type=openapi.TYPE_ARRAY, items=openapi.Schema(
                type=openapi.TYPE_STRING),
        ),
    },
    additional_properties=openapi.Schema(
        description=(
            'A list of error messages for each field that triggered a validation error'  # noqa: E501
        ),
        type=openapi.TYPE_ARRAY, items=openapi.Schema(
            type=openapi.TYPE_STRING),
    ),
)

validation_error_response = {
    status.HTTP_400_BAD_REQUEST: validation_error_schema,
}


unauthorized_schema = openapi.Schema(
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

unauthorized_response = {
    status.HTTP_401_UNAUTHORIZED: unauthorized_schema,
}


forbidden_schema = openapi.Schema(
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

forbidden_response = {
    status.HTTP_403_FORBIDDEN: forbidden_schema,
}

object_not_found_schema = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'detail': openapi.Schema(
            type=openapi.TYPE_STRING,
            description='Invalid pk or object not found due to search filter',
        ),
    },
)

object_not_found_response = {
    status.HTTP_404_NOT_FOUND: object_not_found_schema,
}
