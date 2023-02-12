from unittest import TestCase
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from posts.forms import PostForm
from posts.models import Group, Post, User


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
            text='TEXT_FOR_TEST',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create_page_show_correct_context(self):
        """Проверка: Форма создания поста - post_create."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_form(self):
        """Проверка: Создаётся ли новая запись в базе данных, создавая пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'TEXT_FOR_TEST',
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
            'text': 'TEXT_FOR_TEST'
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

    def test_edit_show_correct_context(self):
        """Проверка: форма редактирования поста, по id"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
