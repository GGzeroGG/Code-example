from django.db import models
from django.db.models import (
    Case, Exists, IntegerField, OuterRef, Value, When,
)
from django.db.models.functions import Coalesce
from django.utils.decorators import method_decorator

from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from services.api.filters import PostFeedFilter
from services.api.serializers.post.post_feed import PostFeedSerializer
from services.api.swagger.docs.posts_feed_detail import doc_decorator as doc_decorator_detail # noqa
from services.api.swagger.docs.posts_feed_list import doc_decorator as doc_decorator_list # noqa

from apps.post.models import Like, Post
from apps.users.models import FollowRequest


@method_decorator(name='list', decorator=doc_decorator_list)
@method_decorator(name='retrieve', decorator=doc_decorator_detail)
class PostFeedViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                      GenericViewSet):
    queryset = Post.objects.all().\
        select_related('user').prefetch_related('images')
    serializer_class = PostFeedSerializer
    filterset_class = PostFeedFilter

    def get_queryset(self):
        return self.queryset.annotate(
            weight=Case(
                When(is_fixed=True, then=Value(2)),
                When(user_id=self.request.user.id, then=Value(1)),
                When(
                    Exists(FollowRequest.objects.filter(
                        follower_id=self.request.user.id,
                        user_id=OuterRef('user_id'),
                    )), then=Value(1),
                ),
                default=Value(0),
                output_field=IntegerField(),
            ),
            total_comments=Coalesce(
                models.Count('comments'),
                models.Value(0),
                output_field=models.IntegerField(),
            ),
            liked=Exists(
                Like.objects.filter(
                    post_id=OuterRef('id'),
                    user_id=self.request.user.id,
                ),
            ),
        ).order_by('-weight', '-created_timestamp')
