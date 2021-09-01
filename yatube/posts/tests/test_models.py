from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_text_label(self):
        """Проверяем, что у моделей корректно работает __str__."""
        verbose_name = 'Текст поста'
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, verbose_name)

    def test_models_text_help_text(self):
        """Проверяем, что у моделей корректно работает __str__."""
        help_text = 'Введите текст поста'
        post = PostModelTest.post
        help_texts = post._meta.get_field('text').help_text
        self.assertEqual(help_texts, help_text)

    def test_models_title_label(self):
        """Проверяем, что у моделей корректно работает __str__."""
        verbose_name = 'Название группы'
        group = PostModelTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEqual(verbose, verbose_name)

    def test_object_name_is_title_fild(self):
        """__str__  group - это строчка с содержимым group.title."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_object_name_is_text_fild(self):
        """__str__  post - это строчка с содержимым post.text."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))
