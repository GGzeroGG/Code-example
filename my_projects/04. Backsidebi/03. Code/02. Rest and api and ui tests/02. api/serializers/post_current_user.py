from rest_framework import serializers

from apps.main.models import Post
from .base import BasePostSerializer
from .post_images import PostImgListSerializer
from .post_moderation import PostModerationSerializer


class PostCurrentUserCreateUpdateSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'user', 'language', 'title', 'content')


class PostCurrentUserListSerializer(BasePostSerializer):
    in_favorites = serializers.BooleanField(read_only=True)
    number_of_comments = serializers.IntegerField(read_only=True)

    class Meta(BasePostSerializer.Meta):
        fields = BasePostSerializer.Meta.fields + (
            'number_of_comments', 'in_favorites',
            'created_timestamp', 'updated_timestamp',
        )


class PostCurrentUserRetrieveSerializer(serializers.ModelSerializer):
    images = PostImgListSerializer(many=True, read_only=True)
    moderation_history = PostModerationSerializer(many=True, read_only=True)
    in_favorites = serializers.BooleanField(read_only=True)
    number_of_comments = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id', 'language', 'title', 'content', 'images', 'status',
            'moderation_history', 'number_of_comments', 'in_favorites',
            'created_timestamp', 'updated_timestamp',
        )
