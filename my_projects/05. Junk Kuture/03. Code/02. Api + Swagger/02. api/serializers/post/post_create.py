from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from apps.post.models import Post
from apps.users.choices import UserType


class PostCreateSerializer(serializers.ModelSerializer):
    default_error_messages = {
        'invalid_user_type': _('Only creator and educator can create posts'),
    }

    images = serializers.ListField(
        child=serializers.FileField(), max_length=5, allow_null=True,
        required=False,
    )

    class Meta:
        model = Post
        fields = ('text', 'images',)

    def validate(self, attrs):
        user_type = self.context['request'].user.type
        allowed_types = [UserType.CREATOR.value, UserType.EDUCATOR.value]

        if not user_type in allowed_types:
            self.fail('invalid_user_type')

        return attrs
