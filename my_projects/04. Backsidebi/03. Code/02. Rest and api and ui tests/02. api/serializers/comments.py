from rest_framework import serializers

from .user import UserDetailSerializer
from apps.main.models import Comment


class CommentAnswerSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'user')


class CommentSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer(read_only=True)
    number_of_answers = serializers.IntegerField(read_only=True)
    answered_on = CommentAnswerSerializer(read_only=True,
                                          source='comment')

    class Meta:
        model = Comment
        fields = (
            'id', 'user', 'comment', 'content', 'number_of_answers',
            'created_timestamp', 'answered_on', 'post',
        )


class CommentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)
