from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Region
from apps.post.models import Post, Comment
from apps.users.choices import Gender, UserType
from apps.users.models import User


class CommentListTestCase(APITestCase):
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
        self.post_1 = Post.objects.create(
            text='Test 1',
            user_id=self.user_auth.id,
        )
        self.post_2 = Post.objects.create(
            text='Test 1',
            user_id=self.user_auth.id,
        )
        self.comment_1 = Comment.objects.create(
            post_id=self.post_1.id,
            user_id=self.user_auth.id,
            text='text',
        )
        self.comment_2 = Comment.objects.create(
            post_id=self.post_2.id,
            user_id=self.user_auth.id,
            text='text',
        )
        self.comment_3 = Comment.objects.create(
            post_id=self.post_2.id,
            user_id=self.user_auth.id,
            text='text',
        )
        self.url = reverse('api:comment_list')

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        response = self.client.get(
            self.url, {'post': self.post_2.id}, format='json',
        )

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receiving_comments(self):
        """
        Successful display of post comments
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(
            self.url, {'post': self.post_2.id}, format='json',
        )

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_comments = (self.comment_2.id, self.comment_3.id)
        self.assertEqual(2, len(response.data['results']))
        for comment in response.data['results']:
            self.assertIn(comment['id'], expected_comments)

    def test_post_not_transferred(self):
        """
        If the post id is not passed, then a 400 error is triggered
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)