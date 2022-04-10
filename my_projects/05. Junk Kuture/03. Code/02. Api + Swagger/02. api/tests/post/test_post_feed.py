from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Region
from apps.post.models import Post, PostImage
from apps.users.choices import Gender, UserType
from apps.users.models import User

from services.api.tests.utils import generate_image # noqa


class PostFeedTestCase(APITestCase):
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
            avatar='test_1.png',
            avatar_small='test_2_small.png',
        )
        self.user_2 = User.objects.create(
            region_id=self.region.id,
            type=UserType.CREATOR,
            phone_number='+79999999992',
            name='name',
            birthday='1111-11-11',
            username='username 2',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
            avatar='test_2.png',
            avatar_small='test_2_small.png',
        )
        self.image_1 = SimpleUploadedFile(
            name='file_1.png', content=generate_image(),
            content_type='image/png',
        )
        self.image_1 = SimpleUploadedFile(
            name='file_1.png', content=generate_image(),
            content_type='image/png',
        )
        self.post_1 = Post.objects.create(
            text='Test 1',
            user_id=self.user_auth.id,
        )
        self.post_1__image_1 = PostImage.objects.create(
            image='test_1.png',
            image_small='test_1_small.png',
            post_id=self.post_1.id,
        )
        self.post_2 = Post.objects.create(
            text='Test 2',
            user_id=self.user_2.id,
        )
        self.post_2__image_1 = PostImage.objects.create(
            image='test_1.png',
            image_small='test_1_small.png',
            post_id=self.post_2.id,
        )

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        url = reverse('api:posts_feed-list')
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_posts_feed(self):
        """
        Сheck the output of the list of posts
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:posts_feed-list')
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_posts = (self.post_1.id, self.post_2.id)
        for post in response.data['results']:
            self.assertIn(post['id'], expected_posts)

    def test_list_posts_feed_filter_user(self):
        """
        Checking post filtering by user
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:posts_feed-list')
        response = self.client.get(
            url, {'user': self.user_2.id}, format='json',
        )

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_posts = (self.post_2.id,)
        for post in response.data['results']:
            self.assertIn(post['id'], expected_posts)
            self.assertNotEqual(post['id'], self.post_1.id)

    def test_detail_posts_feed(self):
        """
        Checking the detail of posts
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse(
            'api:posts_feed-detail', kwargs={'pk': self.post_1.id},
        )
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.post_1.id, response.data['id'])

    def test_detail_posts_feed_does_not_exist(self):
        """
        If you search for a post that does not exist, you will
        receive a 404 error
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse(
            'api:posts_feed-detail', kwargs={'pk': 123},
        )
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
