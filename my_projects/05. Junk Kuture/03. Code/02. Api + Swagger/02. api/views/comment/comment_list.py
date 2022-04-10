from django.utils.decorators import method_decorator
from rest_framework import status

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from apps.post.models import Comment

from services.api.serializers.comment.comment_list import CommentListSerializer
from services.api.swagger.docs.coment_list import doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class CommentListView(ListAPIView):
    serializer_class = CommentListSerializer
    queryset = Comment.objects.all()
    filterset_fields = ('post',)

    def list(self, request, *args, **kwargs):
        if 'post' not in self.request.query_params:
            return Response(data={
                'detail': 'Post id not passed',
            }, status=status.HTTP_400_BAD_REQUEST)
        return super().list(request, *args, **kwargs)
