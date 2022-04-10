from .base import BaseUserSerializer


class CurrentUserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('notify_on_new_comments',
                                                   'language')
        read_only_fields = ('id', 'email',)
