from rest_framework import serializers

from apps.notifications.models import Notification
from .user import UserDetailSerializer


class NotificationSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(source='sender', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id', 'created_timestamp', 'type', 'object_id', 'meta', 'read',
            'title', 'body', 'user'
        )
