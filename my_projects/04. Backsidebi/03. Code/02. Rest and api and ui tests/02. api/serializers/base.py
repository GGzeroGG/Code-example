from django.conf import settings
from rest_framework import serializers

from apps.main.models import Post
from apps.users.models import User
from apps.users.utils import number_of_weeks


class BaseUserSerializer(serializers.ModelSerializer):
    current_avatar = serializers.SerializerMethodField(read_only=True)
    preview_avatar = serializers.SerializerMethodField(read_only=True)
    weeks_of_pregnancy = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'target_date',
            'avatar', 'target_date', 'current_avatar', 'preview_avatar',
            'weeks_of_pregnancy'
        )
        extra_kwargs = {
            'avatar': {'write_only': True},
        }

    def get_current_avatar(self, obj):
        if obj.avatar:
            avatar_url = obj.avatar.url
        else:
            avatar_url = settings.DEFAULT_AVATAR_PREVIEW_URL
        return self.context['request'].build_absolute_uri(avatar_url)

    def get_weeks_of_pregnancy(self, obj):
        return number_of_weeks(target_date=obj.target_date)

    def get_preview_avatar(self, obj: User):
        if obj.avatar:
            try:
                avatar_url = obj.avatar['avatar'].url  # noqa
            except:
                avatar_url = settings.DEFAULT_AVATAR_PREVIEW_URL
        else:
            avatar_url = settings.DEFAULT_AVATAR_PREVIEW_URL
        return self.context['request'].build_absolute_uri(avatar_url)


class BasePostSerializer(serializers.ModelSerializer):
    preview_img = serializers.SerializerMethodField(read_only=True)
    short_content = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'language', 'title', 'short_content', 'preview_img',
                  'status')

    def get_preview_img(self, obj: Post):
        if obj.preview:
            preview_url = self.context['request'].build_absolute_uri(
                obj.preview.img_preview.url
            )
        else:
            preview_url = None
        return preview_url
