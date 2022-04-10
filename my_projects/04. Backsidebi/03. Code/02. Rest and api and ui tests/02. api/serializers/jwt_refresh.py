from rest_framework import serializers
from rest_framework_jwt.serializers import RefreshJSONWebTokenSerializer

from apps.users.models import Device


class JwtRefreshSerializer(serializers.ModelSerializer,
                           RefreshJSONWebTokenSerializer):
    class Meta:
        model = Device
        fields = ('token',)
