from rest_framework import serializers

from services.api.serializers.fields import TypeField
from services.api.serializers.post.post_feed import PostImageInLineSerializer
from services.api.serializers.region import RegionSerializer


from apps.post.models import Post
from apps.users.models import User


class UserDetailSerializer(serializers.ModelSerializer):
    region = RegionSerializer()
    type = TypeField(source='*')

    class Meta:
        model = User
        fields = (
            'id', 'name', 'type', 'region', 'username', 'bio',
            'avatar', 'avatar_small',
        )


class UserPostsSerializer(serializers.ModelSerializer):
    images = PostImageInLineSerializer(many=True)
    is_author = serializers.SerializerMethodField()
    total_comments = serializers.IntegerField()
    liked = serializers.BooleanField()

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'created_timestamp', 'images', 'is_author',
            'is_fixed', 'total_comments', 'liked',
        )

    def get_is_author(self, obj: Post) -> bool:
        return self.context['request'].user.id == obj.user_id
