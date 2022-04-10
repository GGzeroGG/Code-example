from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from services.api.serializers.post.post_create import PostCreateSerializer
from services.api.tests.utils import generate_image

from apps.main.models import Region
from apps.post.models import Post, PostImage
from apps.users.choices import Gender, UserType
from apps.users.models import User


class PostCreateTestCase(APITestCase):
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
        self.image_1 = SimpleUploadedFile(
            name='file_1.png', content=generate_image(),
            content_type='image/png',
        )
        self.image_2 = SimpleUploadedFile(
            name='file_2.png', content=generate_image(),
            content_type='image/png',
        )
        self.image_3 = SimpleUploadedFile(
            name='file_3.png', content=generate_image(),
            content_type='image/png',
        )
        self.image_4 = SimpleUploadedFile(
            name='file_4.png', content=generate_image(),
            content_type='image/png',
        )
        self.image_5 = SimpleUploadedFile(
            name='file_5.png', content=generate_image(),
            content_type='image/png',
        )
        self.image_6 = SimpleUploadedFile(
            name='file_6.png', content=generate_image(),
            content_type='image/png',
        )
        self.url = reverse('api:post_create')

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        image_1 = SimpleUploadedFile(
            name='file_1.png', content=generate_image(),
            content_type='image/png',
        )
        data = {
            'text': 'Post text',
            'images': image_1,
        }
        response = self.client.post(self.url, data=data, format='multipart')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_successful_post_retention(self):
        """
        Successful saving of the post and its pictures
        """
        self.client.force_authenticate(user=self.user_auth)
        data = {
            'text': 'Post text',
            'images': [self.image_1, self.image_2],
        }
        response = self.client.post(self.url, data=data, format='multipart')

        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIsNotNone(Post.objects.filter(id=response.data['id']))
        self.assertIn('images', response.data)
        for image in response.data['images']:
            self.assertTrue(
                PostImage.objects.filter(id=image['id']).exists(),
            )

    def test_max_post_images_5(self):
        """
        The maximum number of pictures for a paste is 5
        if you load more there will be error 400
        """
        self.client.force_authenticate(user=self.user_auth)
        data = {
            'text': 'Post text',
            'images': [
                self.image_1, self.image_2, self.image_3, self.image_4,
                self.image_5, self.image_6,
            ],
        }
        response = self.client.post(self.url, data=data, format='multipart')

        # check
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('images', response.data)

    def test_min_post_images_0(self):
        """
        Images for the post are optional
        """
        self.client.force_authenticate(user=self.user_auth)
        data = {
            'text': 'Post text',
            'images': [],
        }
        response = self.client.post(self.url, data=data, format='multipart')

        # check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_user_type(self):
        """
        Only creator or educator can create posts otherwise error 400
        """
        self.user_auth.type = UserType.FAN.value
        self.user_auth.save()
        self.client.force_authenticate(user=self.user_auth)
        data = {
            'text': 'Post text',
            'images': [
                self.image_1, self.image_2, self.image_3, self.image_4,
                self.image_5,
            ],
        }
        response = self.client.post(self.url, data=data, format='multipart')

        # check
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
        self.assertEqual(
            response.data['non_field_errors'][0],
            PostCreateSerializer.default_error_messages['invalid_user_type'],
        )
