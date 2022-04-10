from rest_framework import serializers

from apps.post.models import Post, PostImage
from apps.users.models import User
from services.api.serializers.fields import TypeField


class PostImageInLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ('id', 'image', 'image_small')


class UserInlineSerializer(serializers.ModelSerializer):
    type = TypeField(source='*')

    class Meta:
        model = User
        fields = ('id', 'name', 'avatar_small', 'type',)


class PostFeedSerializer(serializers.ModelSerializer):
    images = PostImageInLineSerializer(many=True)
    user = UserInlineSerializer()
    is_author = serializers.SerializerMethodField()
    total_comments = serializers.IntegerField()
    liked = serializers.BooleanField()

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'created_timestamp', 'images', 'user', 'is_author',
            'is_fixed', 'total_comments', 'liked',
        )

    def get_is_author(self, obj: Post) -> bool:
        return self.context['request'].user.id == obj.user_id
