from drf_yasg.utils import swagger_auto_schema

from ..base import unauthorized_response

doc_decorator = swagger_auto_schema(
    responses={
        **unauthorized_response,
    },
)
