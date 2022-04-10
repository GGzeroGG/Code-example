from rest_framework import serializers

from apps.post.models import Comment
from apps.users.models import User


class UserCommentInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'avatar_small',)


class CommentListSerializer(serializers.ModelSerializer):
    user = UserCommentInlineSerializer()

    class Meta:
        model = Comment
        fields = ('id', 'text', 'created_timestamp', 'user')
