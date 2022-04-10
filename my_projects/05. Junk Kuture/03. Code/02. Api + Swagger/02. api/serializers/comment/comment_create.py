from rest_framework import serializers

from apps.post.models import Comment
from apps.users.models import User


class UserCommentInlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'name', 'avatar_small',)


class CommentCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('post', 'text', 'user')
