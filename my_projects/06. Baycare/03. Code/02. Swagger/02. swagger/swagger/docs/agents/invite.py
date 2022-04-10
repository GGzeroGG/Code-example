from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

from services.api.serializers.agents import AgentInviteSerializer
from ..base import validation_error_response


doc_decorator = swagger_auto_schema(
    request_body=AgentInviteSerializer,
    responses={
        status.HTTP_201_CREATED: openapi.Response(
            'Invite was sent provided email'
        ),
        **validation_error_response,
    },
)
