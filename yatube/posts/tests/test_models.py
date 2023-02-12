from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='User')
        cls.group = Group.objects.create(
            title='Название',
            slug='slug',
            description='Описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='TEXT_FOR_TEST',
        )

    def test_models_have_correct_object_names(self):
        """Проверка: что у моделей корректно работает __str__, title"""
        fields_posts_group = {
            self.post.text[:15]: str(self.post),
            self.group.title: str(self.group)
        }
        for key, value in fields_posts_group.items():
            with self.subTest():
                self.assertEqual(key, value)
