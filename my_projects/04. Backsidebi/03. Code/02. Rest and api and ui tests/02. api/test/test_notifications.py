from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Post
from apps.notifications.models import Notification
from apps.users.models import User


class NotificationTest:
    def setUp(self):
        self.user_1 = User.objects.create(
            email='test@gmail.com',
            password='1234',
        )
        self.client.force_authenticate(user=self.user_1)
        self.user_2 = User.objects.create(
            email='test2@gmail.com',
            password='1234',
        )
        self.notification_1 = Notification.objects.create(
            user_id=self.user_1.id,
            type=Notification.TYPE.COMM,
            object_id=1,
        )
        self.notification_2 = Notification.objects.create(
            user_id=self.user_1.id,
            type=Notification.TYPE.DEVICE_INPUT,
            object_id=2,
        )
        self.notification_3 = Notification.objects.create(
            user_id=self.user_2.id,
            type=Notification.TYPE.DEVICE_INPUT,
            object_id=2,
        )

    def stub_test_notification_list(self):
        """
        Checking the report of the current user
        """
        url = reverse('api:notification_list')
        response = self.client.get(url, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for notification in response.data['results']:
            self.assertEqual(
                Notification.objects.get(id=notification['id']).user_id,
                self.user_1.id
            )

    def test_notification_read_all(self):
        """
        We check that all messages will be read
        """
        url = reverse('api:notification_read_all')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notifications = Notification.objects.filter(
            user_id=self.user_1.id,
        )
        for notification in notifications:
            self.assertEqual(notification.read, True)

    def test_notification_read(self):
        """
        The requested message will be read
        """
        url = reverse(
            'api:notification_read',  kwargs={'pk': self.notification_1.id}
        )
        response = self.client.put(url, data=None, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.notification_1.refresh_from_db()
        self.notification_2.refresh_from_db()
        self.assertEqual(self.notification_1.read, True)
        self.assertEqual(self.notification_2.read, False)
