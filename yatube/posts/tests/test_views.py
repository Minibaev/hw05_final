import shutil
import tempfile

import datetime as dt

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, Follow

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='StasBasov')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
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
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': f'{self.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': f'{self.user.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/post_detail.html',
            reverse('posts:create'): 'posts/create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': f'{self.post.id}'}
            ): 'posts/create.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        group = PostPagesTests.group
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_pub_date_0 = first_object.pub_date.today().strftime('%d/%m/%Y')
        task_author_0 = first_object.author.username
        task_group_0 = first_object.group
        task_image_0 = first_object.image
        post = self.post.text
        image = self.post.image
        self.assertEqual(task_text_0, f'{post}')
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        user = self.user.username
        self.assertEqual(task_author_0, f'{user}')
        self.assertEqual(task_group_0, group)
        self.assertEqual(task_image_0, image)

    def test_group_list_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group_slug = self.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': f'{group_slug}'})
        )
        first_object_p = response.context['page_obj'][0]
        first_object_g = response.context['group']
        task_text_0 = first_object_p.text
        task_pub_date_0 = first_object_p.pub_date.today().strftime('%d/%m/%Y')
        task_author_0 = first_object_p.author.username
        task_title_0 = first_object_g.title
        task_description_0 = first_object_g.description
        task_image_0 = first_object_p.image
        image = self.post.image
        post = self.post.text
        self.assertEqual(task_text_0, f'{post}')
        self.assertEqual(task_image_0, image)
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        user = self.user.username
        self.assertEqual(task_author_0, f'{user}')
        group_title = self.group.title
        group_desc = self.group.description
        self.assertEqual(task_title_0, f'{group_title}')
        self.assertEqual(task_description_0, f'{group_desc}')

    def test_profile_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        user = self.user.username
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{user}'}
            )
        )
        first_object_p = response.context['page_obj'][0]
        first_object_u = response.context['user_profile']
        task_text_0 = first_object_p.text
        task_pub_date_0 = first_object_p.pub_date.today().strftime('%d/%m/%Y')
        task_author_0 = first_object_p.author.username
        task_username_0 = first_object_u.username
        task_image_0 = first_object_p.image
        image = self.post.image
        post = self.post.text
        self.assertEqual(task_text_0, f'{post}')
        self.assertEqual(task_image_0, image)
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        self.assertEqual(task_author_0, f'{user}')
        self.assertEqual(task_username_0, f'{user}')

    def test_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        group = PostPagesTests.group
        post = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post}'})
        )
        first_object = response.context['post']
        task_group_0 = first_object.group
        task_pub_date_0 = first_object.pub_date.today().strftime('%d/%m/%Y')
        task_author_0 = first_object.author.username
        task_image_0 = first_object.image
        image = self.post.image
        self.assertEqual(task_image_0, image)
        self.assertEqual(task_group_0, group)
        self.assertEqual(
            task_pub_date_0, dt.datetime.now().strftime('%d/%m/%Y')
        )
        user = self.user.username
        self.assertEqual(task_author_0, f'{user}')

    def test_create_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        post = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': f'{post}'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_contains_records(self):
        number_of_post = 12
        for i in range(number_of_post):
            Post.objects.create(
                text=f'Testtext_{i}',
                author=self.user,
                group=self.group,
            )
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_posts_page_contains_records(self):
        number_of_post = 12
        for i in range(number_of_post):
            Post.objects.create(
                text=f'Testtext_{i}',
                author=self.user,
                group=self.group,
            )
        group = self.group.slug
        response = self.client.get(
            reverse('posts:group_posts', kwargs={'slug': f'{group}'})
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(
            reverse(
                'posts:group_posts', kwargs={'slug': f'{group}'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_page_contains_records(self):
        number_of_post = 12
        for i in range(number_of_post):
            Post.objects.create(
                text=f'Testtext_{i}',
                author=self.user,
                group=self.group,
            )
        user = self.user.username
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{user}'}
            )
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{user}'}
            ) + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_index_post_view(self):
        """На главной странице отображаются посты."""
        groups_posts = PostPagesTests.group
        new_test_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=groups_posts,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_test_post, first_object)

    def test_post_group_view(self):
        """На странице группы отображаются посты."""
        groups_posts = PostPagesTests.group
        new_test_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=groups_posts,
        )
        group_slug = self.group.slug
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': f'{group_slug}'})
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_test_post, first_object)

    def test_profile_view(self):
        """На странице профиля отображаются посты."""
        groups_posts = PostPagesTests.group
        new_test_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=groups_posts,
        )
        user = self.user.username
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={'username': f'{user}'}
            )
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_test_post, first_object)

    def test_cache(self):
        """Тестирование кэширования главной страницы"""
        def response_page():
            response = self.authorized_client.get(
                reverse('posts:index')).content.decode('UTF-8')
            return response

        cache.clear()
        text_cache = self.post.text
        self.assertIn(text_cache, response_page())
        Post.objects.filter(text=text_cache).delete()
        self.assertIn(text_cache, response_page())
        cache.clear()
        self.assertNotIn(text_cache, response_page())

    def test_follow_user(self):
        '''Тестирование возможности подписаться и отписаться'''
        follower_count = Follow.objects.count()
        another_user = User.objects.create_user(username='Leo')
        self.another_client = Client()
        self.another_client.force_login(another_user)
        self.another_client.get(reverse(
            'posts:profile_follow', args=[self.user.username]), follow=True)
        self.assertEqual(follower_count + 1, Follow.objects.count())
        self.another_client.get(reverse(
            'posts:profile_unfollow', args=[self.user.username]), follow=True)
        self.assertEqual(follower_count, Follow.objects.count())

    def test_new_post_for_follower_true(self):
        '''Проверка наличия нового поста у подписчиков'''
        Follow.objects.create(
            user=self.user, author=self.user
        )
        new_post = Post.objects.create(
            author=self.user,
            text='Новое тестовое сообщение',
            group=self.group,
        )
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        first_object = response.context['page_obj'][0]
        self.assertEqual(new_post, first_object)

    def test_new_post_for_follower_false(self):
        '''Проверка отсутствие поста у тех, кто не подписан на автора'''
        Follow.objects.create(
            user=self.user, author=self.user
        )
        new_post = Post.objects.create(
            author=self.user,
            text='Testtext',
            group=self.group,
        )
        Follow.objects.filter(
            user=self.user, author=self.user).delete()
        response = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        first_object = response.context['page_obj']

        self.assertNotEqual(first_object, new_post)
