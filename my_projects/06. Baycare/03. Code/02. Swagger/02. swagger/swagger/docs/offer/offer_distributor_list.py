from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from ..base import unauthorized_response, \
    forbidden_response

doc_decorator = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'farmer_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
            description='Leave all offers that have a farmer id = ...',
        ),
    ],
    responses={
        **unauthorized_response,
        **forbidden_response,
    },
)
