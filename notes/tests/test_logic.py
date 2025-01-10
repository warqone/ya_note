from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestCreateNote(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='TestUser',
        )
        cls.else_user = User.objects.create(
            username='ElseUser',
        )
        cls.auth_user = Client()
        cls.auth_user.force_login(cls.user)
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
            'author': cls.user,
        }

    def create_note_w_default_data(self):
        return self.auth_user.post(reverse('notes:add'), data=self.form_data)

    def test_user_can_create_note(self):
        """Пользователь может создать заметку, а анонимный - не может."""
        self.create_note_w_default_data()
        self.assertEqual(Note.objects.count(), 1)
        self.client.logout()
        self.create_note_w_default_data()
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        self.create_note_w_default_data()
        self.create_note_w_default_data()
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """При пустом slug создаётся сгенерированный."""
        self.create_note_w_default_data()
        note = Note.objects.get()
        expected_slug = slugify(note.slug)
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_edit_and_delete_note(self):
        """Автор может редактировать и удалять заметку."""
        self.create_note_w_default_data()
        note = Note.objects.get()
        new_title = 'Новый заголовок'
        self.auth_user.post(
            reverse('notes:edit', args=(note.slug,)),
            data={'title': new_title}
        )
        note.refresh_from_db()
        self.assertNotEqual(note.title, new_title)
        self.auth_user.delete(
            reverse('notes:delete', args=(note.slug,)),
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_else_user_cant_edit_and_delete_note(self):
        """Пользователь не может редактировать и удалять чужие заметки."""
        self.create_note_w_default_data()
        else_auth_user = Client()
        else_auth_user.force_login(self.else_user)
        note = Note.objects.get()
        new_title = 'Новый заголовок'
        else_auth_user.post(
            reverse('notes:edit', args=(note.slug,)),
            data={'title': new_title}
        )
        self.assertEqual(note.title, note.title)
        else_auth_user.delete(
            reverse('notes:delete', args=(note.slug,)),
        )
        self.assertEqual(Note.objects.count(), 1)
