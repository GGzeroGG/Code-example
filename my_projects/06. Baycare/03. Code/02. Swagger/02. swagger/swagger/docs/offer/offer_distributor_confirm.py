from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ..base import validation_error_response, unauthorized_response, \
    forbidden_response, object_not_found_response

doc_decorator = swagger_auto_schema(
    manual_parameters=(
        openapi.Parameter(
            'token', openapi.IN_QUERY, description='offer token',
            type=openapi.TYPE_STRING,
        ),
    ),

    responses={
        **validation_error_response,
        **unauthorized_response,
        **forbidden_response,
        **object_not_found_response,
    },
)
