from django.contrib.auth.hashers import make_password
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Region
from apps.post.models import Post, PostImage
from apps.users.choices import Gender, UserType, users_choices_map
from apps.users.models import User


class UserDetailTestCase(APITestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='region name 1',
            code='RN1',
            phone_number_code='123',
        )
        self.user_auth = User.objects.create(
            region_id=self.region.id,
            type=UserType.CREATOR,
            phone_number='+79999999991',
            name='creator',
            birthday='1111-11-11',
            username='creator',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
        )
        self.user_1 = User.objects.create(
            region_id=self.region.id,
            type=UserType.CREATOR,
            phone_number='+79999999992',
            name='name',
            birthday='1111-11-11',
            username='user 1',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
            avatar='avatar.png',
            avatar_small='avatar_small.png',
            bio='test bio',
        )
        self.post_1 = Post.objects.create(
            text='Test 1',
            user_id=self.user_1.id,
        )
        self.post_1__image_1 = PostImage.objects.create(
            post_id=self.post_1.id,
            image='post_1__image_1.png',
            image_small='post_1__image_small_1.png',
        )
        self.post_1__image_2 = PostImage.objects.create(
            post_id=self.post_1.id,
            image='post_1__image_2.png',
            image_small='post_1__image_small_2.png',
        )
        self.post_2 = Post.objects.create(
            text='Test 2',
            user_id=self.user_1.id,
        )
        self.post_2__image_1 = PostImage.objects.create(
            post_id=self.post_2.id,
            image='post_2__image_1.png',
            image_small='post_2__image_small_1.png',
        )
        self.post_3 = Post.objects.create(
            text='Test 3',
            user_id=self.user_1.id,
        )

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        url = reverse('api:user_detail', kwargs={'pk': self.user_1.id})
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_viewing_someone_elses_page(self):
        """
        Successful space for someone else's profile
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:user_detail', kwargs={'pk': self.user_1.id})
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        posts = Post.objects.filter(user_id=self.user_1.id)
        posts_id = []
        for post in posts:
            posts_id.append(post.id)
        expected_fields = {
            'id': self.user_1.id,
            'name': self.user_1.name,
            'type': users_choices_map['user_type'][self.user_1.type],
            'region': {
                'id': self.user_1.region.id,
                'name': self.user_1.region.name,
                'code': self.user_1.region.code,
                'phone_number_code': self.user_1.region.phone_number_code,
            },
            'username': self.user_1.username,
            'bio': self.user_1.bio,
            'avatar': self.user_1.avatar.url,
            'avatar_small': self.user_1.avatar_small.url,
            'total_posts': Post.objects.filter(user_id=self.user_1.id).count(),
        }
        for field in expected_fields:
            self.assertIn(field, response.data)
            self.assertEqual(expected_fields[field], response.data[field])
        for post in response.data['posts']:
            self.assertIn(post['id'], posts_id)

    def test_viewing_someone_elses_page_no_avatar(self):
        """
        Successful space for someone else's profile no avatar
        """
        self.client.force_authenticate(user=self.user_auth)
        self.user_1.avatar.delete()
        self.user_1.avatar_small.delete()
        url = reverse('api:user_detail', kwargs={'pk': self.user_1.id})
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        posts = Post.objects.filter(user_id=self.user_1.id)
        posts_id = []
        for post in posts:
            posts_id.append(post.id)
        expected_fields = {
            'id': self.user_1.id,
            'name': self.user_1.name,
            'type': users_choices_map['user_type'][self.user_1.type],
            'region': {
                'id': self.user_1.region.id,
                'name': self.user_1.region.name,
                'code': self.user_1.region.code,
                'phone_number_code': self.user_1.region.phone_number_code,
            },
            'username': self.user_1.username,
            'bio': self.user_1.bio,
            'avatar': None,
            'avatar_small': None,
            'total_posts': Post.objects.filter(user_id=self.user_1.id).count(),
        }
        for field in expected_fields:
            self.assertIn(field, response.data)
            self.assertEqual(expected_fields[field], response.data[field])
        for post in response.data['posts']:
            self.assertIn(post['id'], posts_id)

    def test_viewing_someone_elses_page_latest_posts(self):
        """
        Filter check number of posts
        """
        self.client.force_authenticate(user=self.user_auth)
        self.user_1.avatar.delete()
        self.user_1.avatar_small.delete()
        url = reverse('api:user_detail', kwargs={'pk': self.user_1.id})
        response = self.client.get(url, {'latest_posts': 2}, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        posts = Post.objects.filter(user_id=self.user_1.id)[:2:]
        posts_id = []
        for post in posts:
            posts_id.append(post.id)
        expected_fields = {
            'id': self.user_1.id,
            'name': self.user_1.name,
            'type': users_choices_map['user_type'][self.user_1.type],
            'region': {
                'id': self.user_1.region.id,
                'name': self.user_1.region.name,
                'code': self.user_1.region.code,
                'phone_number_code': self.user_1.region.phone_number_code,
            },
            'username': self.user_1.username,
            'bio': self.user_1.bio,
            'avatar': None,
            'avatar_small': None,
            'total_posts': Post.objects.filter(user_id=self.user_1.id).count(),
        }
        for field in expected_fields:
            self.assertIn(field, response.data)
            self.assertEqual(expected_fields[field], response.data[field])
        for post in response.data['posts']:
            self.assertIn(post['id'], posts_id)

    def test_wrong_id(self):
        """
        If you pass the id of a user who is not there will be a 404 error
        """
        self.client.force_authenticate(user=self.user_auth)
        url = reverse('api:user_detail', kwargs={'pk': 123})
        response = self.client.get(url, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
