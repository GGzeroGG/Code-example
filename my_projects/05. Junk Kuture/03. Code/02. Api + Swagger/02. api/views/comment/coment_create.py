from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.post.models import Comment

from services.api.serializers.comment.comment_create import (
    CommentCreateSerializer, UserCommentInlineSerializer,
)
from services.api.swagger.docs.comment_create import doc_decorator


@method_decorator(name='post', decorator=doc_decorator)
class CommentCreateView(GenericAPIView):
    serializer_class = CommentCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        comment = serializer.save()
        user = UserCommentInlineSerializer(comment.user)

        return Response(
            {
                'id': comment.id,
                'text': comment.text,
                'created_timestamp': comment.created_timestamp,
                'user': {
                    **user.data,
                },
            },
            status=status.HTTP_201_CREATED,
        )
