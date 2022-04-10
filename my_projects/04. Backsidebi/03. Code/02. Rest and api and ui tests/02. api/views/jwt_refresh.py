from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import JSONWebTokenAPIView

from apps.users.models import Device

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class JwtRefreshView(JSONWebTokenAPIView):
    serializer_class = RefreshJSONWebTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = serializer.validated_data['token']
        response_data = jwt_response_payload_handler(token, user, request)
        response = Response(response_data)
        if api_settings.JWT_AUTH_COOKIE:
            expiration = (datetime.utcnow() +
                          api_settings.JWT_EXPIRATION_DELTA)
            response.set_cookie(
                api_settings.JWT_AUTH_COOKIE, token, expires=expiration,
                httponly=True,
            )

        device = Device.objects.filter(
            auth_token=request.data['token'],
        ).first()

        if device:
            device.auth_token = response_data['token']
            device.save()
        else:
            return Response({
                'detail': 'Device not found please login'
            }, status=status.HTTP_404_NOT_FOUND)
        return response
