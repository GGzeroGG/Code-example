from rest_framework.generics import RetrieveUpdateAPIView, DestroyAPIView

from ..serializers.current_user import CurrentUserSerializer


class CurrentUserView(RetrieveUpdateAPIView):
    serializer_class = CurrentUserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        new_avatar = 'avatar' in serializer.validated_data
        if new_avatar:
            try:
                self.request.user.avatar.delete_thumbnails()
                self.request.user.avatar.delete()
                self.request.user.avatar_preview.delete()
            except:
                pass

        serializer.save()

        if new_avatar and serializer.instance.avatar:
            preview = serializer.instance.avatar['avatar']
            serializer.instance.avatar_preview = preview.name
            serializer.instance.save(update_fields=['avatar_preview'])


class CurrentUserDeleteView(DestroyAPIView):
    def get_object(self):
        return self.request.user
