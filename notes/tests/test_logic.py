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
        """Проверка что залогиненный пользователь может создать заметку,
        а анонимный - не может.
        """
        # Создание заметки залогиненным пользователем.
        self.create_note_w_default_data()
        self.assertEqual(Note.objects.count(), 1)
        # Выход из аккаунта пользователя и затем повторное создание заметки.
        self.client.logout()
        self.create_note_w_default_data()
        # Проверка что количество заметок не изменилось.
        self.assertEqual(Note.objects.count(), 1)

    def test_not_unique_slug(self):
        """Проверка что невозможно создать две заметки с одинаковым slug."""
        # Создание двух заметок, и проверка что второе не создалось.
        self.create_note_w_default_data()
        self.create_note_w_default_data()
        self.assertEqual(Note.objects.count(), 1)

    def test_empty_slug(self):
        """Проверка что при пустом slug создаётся сгенерированный."""
        # Тут я думаю всё понятно.
        self.create_note_w_default_data()
        note = Note.objects.get()
        expected_slug = slugify(note.slug)
        self.assertEqual(note.slug, expected_slug)

    def test_author_can_edit_and_delete_note(self):
        """Проверка что автор может редактировать и удалять заметку."""
        # Создание заметки и получение заметки, объявление нового заголовка.
        self.create_note_w_default_data()
        note = Note.objects.get()
        new_title = 'Новый заголовок'
        # Запрос на изменение заголовка.
        self.auth_user.post(
            reverse('notes:edit', args=(note.slug,)),
            data={'title': new_title}
        )
        # Проверка что заголовок изменился.
        note.refresh_from_db()
        self.assertNotEqual(note.title, new_title)
        # Запрос на удаление и проверка что заметка исчезла с бд.
        self.auth_user.delete(
            reverse('notes:delete', args=(note.slug,)),
        )
        self.assertEqual(Note.objects.count(), 0)

    def test_else_user_cant_edit_and_delete_note(self):
        """Проверка что другой пользователь не может редактировать
        и удалять заметки.
        """
        # Создание заметки от auth_user и объявление else_user.
        self.create_note_w_default_data()
        else_auth_user = Client()
        else_auth_user.force_login(self.else_user)
        # Получение заметки и объявление заголовка.
        note = Note.objects.get()
        new_title = 'Новый заголовок'
        # post- запрос на изменение заголовка.
        else_auth_user.post(
            reverse('notes:edit', args=(note.slug,)),
            data={'title': new_title}
        )
        # Проверка что заголовок остался старым.
        self.assertEqual(note.title, note.title)
        # Запрос на удаление заметки.
        else_auth_user.delete(
            reverse('notes:delete', args=(note.slug,)),
        )
        # Проверка что кол-во заметок не изменилось.
        self.assertEqual(Note.objects.count(), 1)
