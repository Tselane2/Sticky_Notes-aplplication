from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from notes.models import Note

class NoteViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.other_user = User.objects.create_user(username="otheruser", password="pass1234")

        self.note = Note.objects.create(
            user=self.user,
            title="My Note",
            content="Content"
        )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("note_list"))
        self.assertNotEqual(response.status_code, 200)

    def test_logged_in_user_can_view_notes(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.get(reverse("note_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Note")

    def test_user_cannot_see_other_users_notes(self):
        self.client.login(username="otheruser", password="pass1234")
        response = self.client.get(reverse("note_list"))
        self.assertNotContains(response, "My Note")

    def test_user_can_create_note(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.post(reverse("note_create"), {
            "title": "New Note",
            "content": "New content"
        })
        self.assertEqual(Note.objects.filter(user=self.user).count(), 2)

    def test_only_owner_can_update_note(self):
        self.client.login(username="otheruser", password="pass1234")
        response = self.client.post(reverse("note_update", args=[self.note.id]), {
            "title": "Hacked",
            "content": "Hacked"
        })
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, "My Note")

    def test_owner_can_delete_note(self):
        self.client.login(username="testuser", password="pass1234")
        response = self.client.post(reverse("note_delete", args=[self.note.id]))
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())
