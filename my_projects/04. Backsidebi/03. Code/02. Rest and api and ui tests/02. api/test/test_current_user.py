import io
from unittest import mock

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Post, FavoritePost, Comment
from apps.notifications.models import Notification
from apps.users.models import User, Device


def generate_image(size=(100, 100), image_mode='RGB', image_format='PNG'):
    data = io.BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    return data.read()


class CurrentUserViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@gmail.com',
            first_name='first_name',
            last_name='last_name',
            password='1234',
            avatar='file.png'
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('api:current_user')

    def test_get_current_user(self):
        """
        Retrieving current user data
        """
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user = User.objects.filter(id=response.data['id']).first()
        self.assertEqual(user.id, self.user.id)

    def test_update_current_user(self):
        """
        Checking the update of the current user data
        """
        old_avatar = self.user.avatar
        data = {
            'first_name': 'now_first_name',
            'last_name': 'now_last_name',
        }
        response = self.client.patch(self.url, data=data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, old_avatar)
        self.assertEqual(self.user.first_name, data['first_name'])
        self.assertEqual(self.user.last_name, data['last_name'])

    def test_update_avatar_current_user(self):
        """
        Checking the update of the current user avatar
        """
        old_avatar = self.user.avatar
        avatar = SimpleUploadedFile(
            name='new_file.png', content=generate_image(),
            content_type='image/png',
        )
        data = {'avatar': avatar}
        response = self.client.patch(self.url, data=data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.avatar, old_avatar)


class CurrentUserDeleteViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@gmail.com',
            first_name='first_name',
            last_name='last_name',
            password='1234',
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse('api:current_user_delete')

        self.post = Post.objects.create(
            user_id=self.user.id,
            title='title',
            content='content',
        )
        self.device = Device.objects.create(
            user_id=self.user.id,
            device_id='device_id',
            registration_token='registration_token',
            os_version='os_version',
            auth_token='auth_token',
        )

    def test_delete_current_user(self):
        """
        Checking that the current user is deleted
        """
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(User.objects.filter(id=self.user.id).first())

    def test_delete_device_current_user(self):
        """
        When deleting a user, all of his devices must be deleted
        """
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(Device.objects.filter(id=self.device.id).first())

    def test_delete_post_current_user(self):
        """
        When deleting a user, all his posts must be deleted
        """
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(Post.objects.filter(id=self.post.id).first())

    def test_delete_favorite_post_current_user(self):
        """
        When deleting a user, all of his favorite posts should be deleted
        """
        favorite_post = FavoritePost.objects.create(
            user_id=self.user.id,
            post_id=self.post.id,
        )
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(
            FavoritePost.objects.filter(id=favorite_post.id).first()
        )

    @mock.patch(
        'services.notifications.signals.send_notification_multicast',
        return_value=None,
    )
    def test_delete_notification_current_user(self, fake_func):
        """
        Checking that when a user is deleted, notifications will be deleted
        """
        notification = Notification.objects.create(
            recipient_id=self.user.id,
            type=Notification.TYPE.POST_BLOCKED,
            object_id=self.post.id,
        )
        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNone(
            Notification.objects.filter(id=notification.id).first()
        )

    def test_delete_comments_post_current_user(self):
        """
        When deleting a user, his comments should be depersonalized but not deleted
        so as not to violate nesting
        """
        user_2 = User.objects.create(
            email='test2@gmail.com',
            first_name='first_name',
            last_name='last_name',
            password='1234',
        )
        post_2 = Post.objects.create(
            user_id=user_2.id,
            title='title_2',
            content='content',
        )
        comment = Comment.objects.create(
            user_id=self.user.id,
            post_id=post_2.id,
            content='content'
        )

        response = self.client.delete(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertIsNotNone(Comment.objects.filter(id=comment.id).first())
