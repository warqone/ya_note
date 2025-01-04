from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(
            username='Test_author',
        )
        cls.else_author = User.objects.create(
            username='Else_Author',
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.author,
        )

    def test_pages_availability_for_note_author_user(self):
        """Проверка отображения страниц для залогиненного автора."""
        self.client.force_login(self.author)
        urls = (
            ('notes:home', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:list', None),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_else_author(self):
        """Проверка на управление заметкой другого автора."""
        self.client.force_login(self.else_author)
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_for_anonymous_client(self):
        """Проверка на редирект для незалогиненного пользователя."""
        login_url = reverse('users:login')
        urls = (
            ('notes:add', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
