from django.db import models
from django.db.models import Exists, OuterRef
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.post.models import Post, Like
from apps.users.models import User, FollowRequest

from services.api.serializers.users.user_detail import (
    UserDetailSerializer, UserPostsSerializer,
)
from services.api.swagger.docs.user_detail import doc_decorator


@method_decorator(name='get', decorator=doc_decorator)
class UserDetailView(APIView):
    error_messages = {
        'user_not_exist': _('User with this id does not exist'),
    }

    def get(self, request, *args, **kwargs):
        user: User = User.objects.filter(id=self.kwargs['pk']).first()
        if user is None:
            return Response({
                'user_not_exist': [
                    self.error_messages['user_not_exist'],
                ]},
                status=status.HTTP_404_NOT_FOUND,
            )
        user_serializer = UserDetailSerializer(user)

        latest_posts = 0
        if 'latest_posts' in self.request.query_params:
            try:
                latest_posts = int(
                    self.request.query_params['latest_posts'] # noqa
                )
            except ValueError:
                pass

        posts = Post.objects.filter(
            user_id=user.id,
        ).prefetch_related('images').annotate(
            total_comments=Coalesce(
                models.Count('comments'),
                models.Value(0),
                output_field=models.IntegerField(),
            ),
            liked=Exists(
                Like.objects.filter(
                    post_id=OuterRef('id'),
                    user_id=self.request.user.id,
                )
            ),
        ).order_by('-created_timestamp')
        total_posts = posts.count()
        posts_serializer = UserPostsSerializer(
            posts[:min(latest_posts, 30)], many=True,
            context={'request': self.request},
        )
        is_followed = FollowRequest.objects.filter(
            follower_id=self.request.user.id,
            user_id=user.id,
        ).exists()

        return Response({
            **user_serializer.data,
            'is_followed': is_followed,
            'total_posts': total_posts,
            'posts': posts_serializer.data,
        })
