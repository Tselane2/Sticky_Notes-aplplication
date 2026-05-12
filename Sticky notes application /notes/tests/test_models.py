from django.test import TestCase
from django.contrib.auth.models import User
from notes.models import Note

class NoteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass1234")
        self.note = Note.objects.create(
            user=self.user,
            title="Test Note",
            content="This is a test note."
        )

    def test_note_string_method(self):
        self.assertEqual(str(self.note), "Test Note")

    def test_note_is_linked_to_user(self):
        self.assertEqual(self.note.user.username, "testuser")
