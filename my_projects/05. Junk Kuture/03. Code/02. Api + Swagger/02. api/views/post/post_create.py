from django.conf import settings
from django.utils.decorators import method_decorator

from easy_thumbnails.files import get_thumbnailer

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from services.api.serializers.post.post_create import PostCreateSerializer
from services.api.swagger.docs.post_create import doc_decorator

from apps.post.models import Post, PostImage
from apps.users.choices import users_choices_map


@method_decorator(name='post', decorator=doc_decorator)
class PostCreateView(GenericAPIView):
    serializer_class = PostCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post = Post.objects.create(
            user_id=request.user.id,
            text=serializer.validated_data['text'],
        )
        images_data = []

        if 'images' in serializer.validated_data:
            images = serializer.validated_data['images']

            for image in images:
                post_image = PostImage.objects.create(
                    post_id=post.id, image=image, image_small=None,
                )
                image_small = get_thumbnailer(
                    post_image.image,
                ).get_thumbnail(settings.THUMBNAIL_ALIASES['']['post'])
                post_image.image_small = image_small.name
                post_image.save(update_fields=['image_small'])
                images_data.append({
                    'id': post_image.id,
                    'image': post_image.image.url,
                    'image_small': post_image.image_small.url,
                })

        avatar_small = None
        if self.request.user.avatar_small:
            avatar_small = self.request.user.avatar_small.url

        return Response({
            'id': post.id,
            'text': post.text,
            'liked': False,
            'created_timestamp': post.created_timestamp,
            'images': images_data,
            'is_fixed': post.is_fixed,
            'is_author': True,
            'user': {
                'id': request.user.id,
                'name': request.user.name,
                'avatar_small': avatar_small,
                'type': users_choices_map['user_type'][request.user.type],
            }}, status=status.HTTP_201_CREATED)
