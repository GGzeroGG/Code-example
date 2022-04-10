from django.db.models import Count
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.viewsets import ModelViewSet

from apps.main.models import Comment
from ..filters import CommentFilter
from ..mixins import SerializerMapMixin
from ..serializers import comments
from ..serializers.comments import CommentUpdateSerializer


class CommentView(ListCreateAPIView):
    permission_classes = ()
    serializer_class = comments.CommentSerializer
    filterset_class = CommentFilter
    queryset = Comment.objects.all().select_related('user').annotate(
        number_of_answers=Count('child_comments'),
    )

    def get_queryset(self):
        return self.queryset.filter(post_id=self.kwargs.get('pk'))

    def perform_create(self, serializer):
        serializer.save(
            user_id=self.request.user.id,
            post_id=self.kwargs['pk'],
        )
        serializer.instance.number_of_answers = 0


class CommentsViewSet(SerializerMapMixin, ModelViewSet):
    permission_classes = ()
    serializer_class = comments.CommentSerializer
    serializer_map = {
        'update': CommentUpdateSerializer,
        'partial_update': CommentUpdateSerializer,
    }
    filterset_class = CommentFilter
    queryset = Comment.objects.all().select_related('user').annotate(
        number_of_answers=Count('child_comments'),
    )

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied

        serializer.save(user_id=self.request.user.id)
        serializer.instance.number_of_answers = 0

    def perform_update(self, serializer):
        if serializer.instance.user_id != self.request.user.id:
            raise PermissionDenied
        super().perform_update(serializer)

    def perform_destroy(self, instance: Comment):
        if instance.user_id != self.request.user.id:
            raise PermissionDenied
        super().perform_destroy(instance)
