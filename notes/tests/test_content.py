from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='TestAuthor',
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='slug',
            author=cls.user,
        )
        cls.else_user = User.objects.create(
            username='ElseAuthor',
        )
        cls.else_note = Note.objects.create(
            title='Другой заголовок',
            text='Другой текст',
            slug='else slug',
            author=cls.else_user,
        )
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.notes_list = reverse('notes:list')
        cls.note_detail = reverse('notes:detail', args=(cls.note.slug,))

    def test_notes_have_note(self):
        """Заметка есть в списке заметок."""
        response = self.auth_user.get(self.notes_list)
        self.assertIn('object_list', response.context)
        objects = response.context['object_list']
        self.assertIn(self.note, objects)

    def test_notes_from_another_user_not_availability(self):
        """Заметки другого пользователя недоступны."""
        response = self.auth_user.get(self.notes_list)
        objects = response.context['object_list']
        self.assertNotIn(self.else_note, objects)

    def test_form_in_add_and_edit_note(self):
        """Форма заполнения присутствует в добавлении и удалении заметки."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,))
        )
        for name, args in urls:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.auth_user.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
