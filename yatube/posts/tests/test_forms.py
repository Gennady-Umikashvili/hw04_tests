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
        cls.user2 = User.objects.create_user(username='User2')
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
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

    def test_create_post_form(self):
        """Проверка: Создаётся ли новая запись в базе данных, создавая пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': NEW_TEXT,
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

    def test_create_post_form_without_group(self):
        """Проверка: Создаётся ли новая запись в базе данных,
        создавая пост без группы"""
        post_count = Post.objects.count()
        form_data = {
            'text': NEW_TEXT,
            'group': ""
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
        self.assertEqual(post.group, None)
        self.assertEqual(post.author, self.user)

    def test_create_post_form_by_guest(self):
        """Проверка: Не создаётся новая запись в базе данных,
        создавая пост неавторизованным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'text': NEW_TEXT,
            'group': self.group.id
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        new_post_count = Post.objects.count()
        self.assertRedirects(
            response,
            "/auth/login/?next=/create/"
        )
        self.assertEqual(post_count, new_post_count)

    def test_edit_post_form(self):
        """Проверка: происходит ли изменение поста в базе данных"""
        post_count = Post.objects.count()
        post = Post.objects.get(pk=self.post.pk)
        form_data = {
            'group': self.group2.id,
            'text': NEW_TEXT
        }
        response = self.authorized_client.post(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertNotEqual(post.text, edited_post.text)
        self.assertNotEqual(post.group, edited_post.group)
        self.assertEqual(post.author, edited_post.author)
        self.assertEqual(post.pub_date, edited_post.pub_date)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.id, form_data['group'])

    def test_post_not_edit_by_guest_client(self):
        """Проверка: не изменится ли запись в Post если неавторизован."""
        posts_count = Post.objects.count()
        post = Post.objects.get(pk=self.post.pk)
        form_data = {"text": NEW_TEXT, "group": self.group.id}
        response = self.guest_client.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(
            response,
            f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, edited_post.text)
        self.assertEqual(post.group, edited_post.group)
        self.assertEqual(post.author, edited_post.author)
        self.assertEqual(post.pub_date, edited_post.pub_date)

    def test_post_not_edit_by_not_author(self):
        """Проверка: не изменится ли запись в Post если не автор."""
        posts_count = Post.objects.count()
        post = Post.objects.get(pk=self.post.pk)
        form_data = {"text": NEW_TEXT, "group": self.group.id}
        response = self.authorized_client2.post(
            reverse("posts:post_edit", args=({self.post.id})),
            data=form_data,
            follow=True,
        )
        edited_post = Post.objects.get(pk=self.post.pk)
        self.assertRedirects(
            response,
            f"/posts/{self.post.id}/"
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(post.text, edited_post.text)
        self.assertEqual(post.group, edited_post.group)
        self.assertEqual(post.author, edited_post.author)
        self.assertEqual(post.pub_date, edited_post.pub_date)
