import datetime

from django.contrib.auth.hashers import make_password
from django.urls import reverse
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Application, Competition, Region
from apps.users.choices import Gender, UserType
from apps.users.models import User


class UserSearchTestCase(APITestCase):
    def setUp(self):
        self.region = Region.objects.create(
            name='region name 1',
            code='RN1',
            phone_number_code='123',
        )
        self.region_2 = Region.objects.create(
            name='region name 2',
            code='RN2',
            phone_number_code='123',
        )
        self.competition = Competition.objects.create(
            name='name 1',
            description='description 1',
            starts_at=timezone.now() - datetime.timedelta(hours=5),
            ends_at=timezone.now() + datetime.timedelta(hours=10),
            background_image='img.png',
            background_clip='clip.h264',
        )
        self.competition.regions.set([self.region])
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
        )
        self.user_2 = User.objects.create(
            region_id=self.region_2.id,
            type=UserType.CREATOR,
            phone_number='+79999999993',
            name='storm',
            birthday='1111-11-11',
            username='spirit',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
        )
        self.user_3 = User.objects.create(
            region_id=self.region.id,
            type=UserType.FAN,
            phone_number='+79999999994',
            name='fan',
            birthday='1111-11-11',
            username='fan',
            password=make_password('pass'),
            gender=Gender.NOT_SPECIFIED,
        )
        self.application = Application.objects.create(
            school_address='school address',
            school_name='school name',
            video_link='video link',
            name='name',
            description='description',
            materials='materials',
            competition_id=self.competition.id,
            user_id=self.user_auth.id,
        )
        self.url = reverse('api:user_search')

    def test_no_user_authorization(self):
        """
        User not logged in authorization error
        """
        response = self.client.get(self.url, {
            'search': 'name',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_search_by_name(self):
        """
        Search for a user by name
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(self.url, {
            'search': 'na',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.user_1.id)

    def test_search_by_username(self):
        """
        Search for a user by username
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(self.url, {
            'search': 'use',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.user_1.id)

    def test_search_no_region(self):
        """
        Users with a region that is not in the competition will not display
        applications
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(self.url, {
            'search': 'storm',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_search_no_fan(self):
        """
        Users with tp account fan do not withdraw
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(self.url, {
            'search': 'fan',
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_dont_deduce_the_creator(self):
        """
        Do not display the creator of the application
        """
        self.client.force_authenticate(user=self.user_auth)
        response = self.client.get(self.url, {
            'search': self.user_auth.username,
        }, format='json')

        # Check
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)
