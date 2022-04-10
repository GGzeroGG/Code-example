from rest_framework import serializers

from services.api.serializers.fields import TypeField

from apps.users.models import User


class UserSearchSerializer(serializers.ModelSerializer):
    type = TypeField(source='*')

    class Meta:
        model = User
        fields = ('id', 'name', 'username', 'type', 'avatar_small')
