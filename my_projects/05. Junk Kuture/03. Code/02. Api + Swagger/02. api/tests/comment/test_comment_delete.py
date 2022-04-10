from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Region
from apps.post.models import Post, Comment
from apps.users.choices import Gender, UserType
from apps.users.models import User


class CommentDeleteTestCase(APITestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='region name',
            code='RN',
            phone_number_code='123',
        )
        self.user_auth = User.objects.create(
            region_id=self.region.id,
            type=UserType.CREATOR,
            phone_number='+79999999991',
            name='name',
            birthday='1111-11-11',
            username='username 1',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
            avatar='asd.png',
            avatar_small='asd_small.png',
        )
        self.user_comment = User.objects.create(
            region_id=self.region.id,
            type=UserType.CREATOR,
            phone_number='+79999999992',
            name='name',
            birthday='1111-11-11',
            username='username 2',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
            avatar='asd.png',
            avatar_small='asd_small.png',
        )
        self.post_1 = Post.objects.create(
            text='Test 1',
            user_id=self.user_auth.id,
        )
        self.post_2 = Post.objects.create(
            text='Test 2',
            user_id=self.user_comment.id,
        )
        self.comment_1 = Comment.objects.create(
            post_id=self.post_1.id,
            user_id=self.user_auth.id,
            text='text',
        )
        self.comment_2 = Comment.objects.create(
            post_id=self.post_1.id,
            user_id=self.user_comment.id,
            text='text',
        )
        self.comment_3 = Comment.objects.create(
            post_id=self.post_2.id,
            user_id=self.user_auth.id,
            text='text',
        )
        self.comment_4 = Comment.objects.create(
            post_id=self.post_2.id,
            user_id=self.user_comment.id,
            text='text',
        )

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        url = reverse('api:comment_delete', kwargs={'pk': self.comment_1.id})
        response = self.client.delete(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment(self):
        """
        Successful comment delete
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:comment_delete', kwargs={'pk': self.comment_1.id})
        response = self.client.delete(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment_1.id).exists())

    def test_check_deletion_of_other_peoples_comments_of_my_post(self):
        """
        I, as the owner of the post, can delete any comments on my post.
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:comment_delete', kwargs={'pk': self.comment_2.id})
        response = self.client.delete(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment_2.id).exists())

    def test_i_can_delete_my_comments_on_someone_elses_post(self):
        """
        I can delete my comment on someone else's post
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:comment_delete', kwargs={'pk': self.comment_3.id})
        response = self.client.delete(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Comment.objects.filter(id=self.comment_3.id).exists())

    def test_deleting_someone_elses_comment_on_someone_elses_post(self):
        """
        I cannot delete someone else's comment on someone else's post there
        will be an error 404
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:comment_delete', kwargs={'pk': self.comment_4.id})
        response = self.client.delete(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
