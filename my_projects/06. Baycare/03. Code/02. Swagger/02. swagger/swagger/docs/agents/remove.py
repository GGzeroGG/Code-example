from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.serializers.agents import AgentRemoveRequestSerializer
from ..base import validation_error_response


doc_decorator = swagger_auto_schema(
    request_body=AgentRemoveRequestSerializer,
    responses={
        status.HTTP_204_NO_CONTENT: openapi.Response(
            'Invite and user was deleted'
        ),
        **validation_error_response,
    },
)
