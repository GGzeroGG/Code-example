from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Region
from apps.post.models import Post, Comment
from apps.users.choices import Gender, UserType
from apps.users.models import User


class CommentCreateTestCase(APITestCase):
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
        self.url = reverse('api:comment_create')

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        data = {
            'post': self.post_1.id,
            'text': 'test text',
        }
        response = self.client.post(self.url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_comment(self):
        """
        Successful comment creation
        """
        self.client.force_authenticate(user=self.user_auth)
        data = {
            'post': self.post_1.id,
            'text': 'test text',
        }
        response = self.client.post(self.url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        comment = Comment.objects.filter(
            id=response.data['id'],
        ).exists()
        self.assertTrue(comment)

    def test_post_does_not_exist(self):
        """
        If you pass the id of a post that does not exist, there will be
        an error 400
        """
        self.client.force_authenticate(user=self.user_auth)
        data = {
            'post': 123123123,
            'text': 'test text',
        }
        response = self.client.post(self.url, data=data, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('post', response.data)
        self.assertEqual(response.data['post'][0].code, 'does_not_exist')
