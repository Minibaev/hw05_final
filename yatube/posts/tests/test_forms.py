import shutil
import tempfile
# from yatube.posts.models import Comment

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        group = self.group.id
        posts_count = Post.objects.count()
        text = 'Testtext'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': text,
            'group': group,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        user = self.user.username
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': f'{user}'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post_text = text
        self.assertTrue(
            Post.objects.filter(
                text=post_text,
            ).exists()
        )

    def test_create_edit_post(self):
        """Валидная форма изменяет запись в Post."""
        edited_post = 'Исправленный текст'
        post = self.post.id
        user = self.user.id
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': f'{post}'}),
            data={'text': edited_post},
            follow=True
        )
        test_post = Post.objects.first()
        self.assertNotEqual(test_post.text, edited_post)
        self.assertEqual(test_post.author_id, user)
        self.assertNotEqual(test_post.group_id, None)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{post}'})
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент',
        )
        cls.form = CommentForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Comment."""
        comments_count = Comment.objects.count()
        text = 'Testcomment'
        form_data = {
            'text': text,
        }
        post = self.post.id
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': f'{post}'}
            ),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': f'{post}'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=text,
            ).exists()
        )
