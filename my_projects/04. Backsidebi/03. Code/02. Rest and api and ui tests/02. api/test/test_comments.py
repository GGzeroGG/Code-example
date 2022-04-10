from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.main.models import Post, Comment
from apps.users.models import User


class CommentViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            email='test@gmail.com',
            password='1234',
        )
        self.post = Post.objects.create(
            user_id=self.user.id,
            title='title',
            content='content',
        )
        self.main_comment = Comment.objects.create(
            user_id=self.user.id,
            post_id=self.post.id,
            content='content_1',
        )
        self.answer_comment = Comment.objects.create(
            user_id=self.user.id,
            post_id=self.post.id,
            comment_id=self.main_comment.id,
            content='content_1.1',
        )
        self.url = reverse('api:comments', kwargs={'pk': self.post.id, })

        self.client.force_authenticate(user=self.user)

    def test_create_main_comment(self):
        """
        Creating the main document
        """
        data = {
            'comment': None,
            'content': 'content_2',
            'post': self.post.id,
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.filter(id=response.data['id']).first()
        self.assertTrue(comment)
        self.assertEqual(comment.comment, None)

    def test_create_answer_comment(self):
        """
        Create a response
        """
        data = {
            'comment': self.main_comment.id,
            'content': 'This answer',
            'post': self.post.id,
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        comment = Comment.objects.filter(id=response.data['id']).first()
        self.assertTrue(comment)
        self.assertEqual(comment.comment.id, self.main_comment.id)

    def test_create_no_main_comment(self):
        """
        Reply to comment which is not
        """
        data = {
            'comment': 1321123,
            'content': 'This answer',
            'post': self.post.id,
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        comment = Comment.objects.filter(content=data['content']).first()
        self.assertIsNone(comment)

    def test_get_comments(self):
        """
        Checking the display of comments this post
        """
        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comments = response.data['results']
        for comment in comments:
            self.assertTrue(
                comment['id'] == self.main_comment.id or
                comment['id'] == self.answer_comment.id
            )

    def test_get_filter_is_parent(self):
        """
        Checking a filter that displays all parent comments
        """
        response = self.client.get(
            self.url, {'is_parent': True}, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comments = response.data['results']
        for comment in comments:
            self.assertEqual(comment['comment'], None)

    def test_get_filter_comment_subsidiaries(self):
        """
        Checking to get all children of this comment
        """
        main_comment_2 = Comment.objects.create(
            user_id=self.user.id,
            post_id=self.post.id,
            content='content_2',
        )
        Comment.objects.create(
            user_id=self.user.id,
            post_id=self.post.id,
            comment_id=main_comment_2.id,
            content='content_2.1',
        )
        response = self.client.get(
            f'{self.url}?comment={self.main_comment.id}', format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        comments = response.data['results']
        for comment in comments:
            self.assertEqual(comment['comment'], self.main_comment.id)
