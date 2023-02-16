from unittest import TestCase
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
# from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User

TEXT = "TEST_FOR_THE_TEST"
NEW_TEXT = 'CHANGING_THE_TEXT'


class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Описание'
        )
        cls.group2 = Group.objects.create(
            title='Название_2',
            slug='slug_2',
            description='Описание_2',
        )
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_create_post_form(self):
        """Проверка: Создаётся ли новая запись в базе данных, создавая пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': TEXT,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.first()
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'User'})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)

    def test_edit_post_form(self):
        """Проверка: происходит ли изменение поста в базе данных"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group2.id,
            'text': TEXT
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertEqual(self.post.text, form_data['text'])

    def test_post_edit_not_create_guest_client(self):
        """Проверка: не изменится ли запись в Post если неавторизован."""
        posts_count = Post.objects.count()
        form_data = {"text": NEW_TEXT, "group": self.group.id}
        response = self.guest_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text=NEW_TEXT).exists())
