from django.db.models import Q
from django.utils.decorators import method_decorator

from rest_framework.generics import DestroyAPIView

from apps.post.models import Comment

from services.api.swagger.docs.comment_delete import doc_decorator


@method_decorator(name='delete', decorator=doc_decorator)
class CommentDeleteView(DestroyAPIView):
    queryset = Comment.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            Q(post__user_id=self.request.user.id) |
            Q(user_id=self.request.user.id),
        )
