from django.test import TestCase

from posts.models import Group, Post, User


CHARACTERS_TEXT = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.post = Post.objects.create(
            author=cls.user,
            text='TEXT_FOR_THE_TEST',
        )

    def test_models_have_correct_object_names(self):
        """Проверка: что у моделей корректно работает __str__, title"""
        field_posts = {
            self.post.text[:CHARACTERS_TEXT]: str(self.post)
        }
        for key, value in field_posts.items():
            with self.subTest():
                self.assertEqual(key, value)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Описание',
        )

    def test_models_have_correct_object_names(self):
        """Проверка: что у моделей корректно работает __str__, title"""
        field_posts_group = {
            self.group.title: str(self.group)
        }
        for key, value in field_posts_group.items():
            with self.subTest():
                self.assertEqual(key, value)
