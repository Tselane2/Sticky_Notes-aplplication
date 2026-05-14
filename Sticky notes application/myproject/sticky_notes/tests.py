# tests.py — Unit tests for the sticky_notes app.
#
# Coverage:
#   - NoteModelTests   : model creation, __str__, timestamps, ownership
#   - NoteFormTests    : valid/invalid form submissions, excluded fields
#   - NoteListViewTests: authentication guard, per-user filtering
#   - NoteCreateViewTests : GET form render, POST create, ownership assigned
#   - NoteUpdateViewTests : GET pre-fill, POST save, cross-user 404
#   - NoteDeleteViewTests : GET confirm page, POST delete, cross-user 404
#   - NoteURLTests     : named URL -> path resolution

from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Note
from .forms import NoteForm
from . import views


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_user(username='alice', password='Testpass123!'):
    """Create and return a test user."""
    return User.objects.create_user(username=username, password=password)


def make_note(user, title='Test Note', content='Some content'):
    """Create and return a Note owned by *user*."""
    return Note.objects.create(user=user, title=title, content=content)


# ---------------------------------------------------------------------------
# Model Tests
# ---------------------------------------------------------------------------

class NoteModelTests(TestCase):
    """Tests for the Note model itself."""

    def setUp(self):
        self.user = make_user()
        self.note = make_note(self.user)

    def test_str_returns_title(self):
        """__str__ should return the note's title."""
        self.assertEqual(str(self.note), 'Test Note')

    def test_note_belongs_to_user(self):
        """The user FK should point to the creating user."""
        self.assertEqual(self.note.user, self.user)

    def test_created_at_is_set_automatically(self):
        """created_at should be populated on creation, not left None."""
        self.assertIsNotNone(self.note.created_at)
        # Should be a recent timestamp (within the last few seconds).
        self.assertLessEqual(
            (timezone.now() - self.note.created_at).total_seconds(),
            5,
        )

    def test_updated_at_changes_on_save(self):
        """updated_at should be refreshed every time the note is saved."""
        original = self.note.updated_at
        self.note.title = 'Updated Title'
        self.note.save()
        self.note.refresh_from_db()
        self.assertGreaterEqual(self.note.updated_at, original)

    def test_note_deleted_with_user(self):
        """Deleting the user should cascade-delete their notes."""
        note_pk = self.note.pk
        self.user.delete()
        self.assertFalse(Note.objects.filter(pk=note_pk).exists())

    def test_default_ordering_by_created_at_desc(self):
        """Notes queried with -created_at should be newest first."""
        older = make_note(self.user, title='Older')
        newer = make_note(self.user, title='Newer')
        notes = list(
            Note.objects.filter(user=self.user).order_by('-created_at')
        )
        # The newest note should appear before the older ones.
        self.assertEqual(notes[0].pk, newer.pk)
        self.assertIn(older, notes)


# ---------------------------------------------------------------------------
# Form Tests
# ---------------------------------------------------------------------------

class NoteFormTests(TestCase):
    """Tests for NoteForm validation and field exclusions."""

    def test_valid_form(self):
        """A form with title and content should be valid."""
        form = NoteForm(data={'title': 'Hello', 'content': 'World'})
        self.assertTrue(form.is_valid())

    def test_missing_title_is_invalid(self):
        """Title is required — omitting it should fail validation."""
        form = NoteForm(data={'title': '', 'content': 'World'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_missing_content_is_invalid(self):
        """Content is required — omitting it should fail validation."""
        form = NoteForm(data={'title': 'Hello', 'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)

    def test_form_only_exposes_title_and_content(self):
        """The form must not expose user, created_at, or updated_at."""
        form = NoteForm()
        self.assertIn('title', form.fields)
        self.assertIn('content', form.fields)
        self.assertNotIn('user', form.fields)
        self.assertNotIn('created_at', form.fields)
        self.assertNotIn('updated_at', form.fields)

    def test_title_max_length_enforced(self):
        """Titles longer than 200 characters should fail validation."""
        form = NoteForm(data={'title': 'x' * 201, 'content': 'ok'})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


# ---------------------------------------------------------------------------
# Note List View Tests
# ---------------------------------------------------------------------------

class NoteListViewTests(TestCase):
    """Tests for the note_list view."""

    def setUp(self):
        self.client = Client()
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.url = reverse('note_list')

    def test_redirects_anonymous_user_to_login(self):
        """Unauthenticated GET should redirect to the login page."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_authenticated_user_sees_200(self):
        """Logged-in user should receive a 200 response."""
        self.client.force_login(self.alice)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_user_only_sees_own_notes(self):
        """Notes from other users must not appear in the list."""
        alice_note = make_note(self.alice, title="Alice's Note")
        make_note(self.bob, title="Bob's Note")

        self.client.force_login(self.alice)
        response = self.client.get(self.url)
        notes = list(response.context['notes'])

        self.assertIn(alice_note, notes)
        self.assertEqual(len(notes), 1)

    def test_empty_list_when_user_has_no_notes(self):
        """A user with no notes should see an empty queryset."""
        self.client.force_login(self.alice)
        response = self.client.get(self.url)
        self.assertEqual(len(response.context['notes']), 0)


# ---------------------------------------------------------------------------
# Note Create View Tests
# ---------------------------------------------------------------------------

class NoteCreateViewTests(TestCase):
    """Tests for the note_create view."""

    def setUp(self):
        self.client = Client()
        self.alice = make_user('alice')
        self.url = reverse('note_create')

    def test_redirects_anonymous_user(self):
        """GET by an unauthenticated user should redirect to login."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_get_renders_blank_form(self):
        """GET by a logged-in user should return 200 with an empty form."""
        self.client.force_login(self.alice)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_post_valid_data_creates_note(self):
        """A valid POST should create a new Note in the database."""
        self.client.force_login(self.alice)
        self.client.post(self.url, {'title': 'My Note', 'content': 'Body'})
        self.assertEqual(Note.objects.filter(user=self.alice).count(), 1)

    def test_post_assigns_current_user_as_owner(self):
        """The created note should be owned by the logged-in user."""
        self.client.force_login(self.alice)
        self.client.post(self.url, {'title': 'Mine', 'content': 'Body'})
        note = Note.objects.get(user=self.alice)
        self.assertEqual(note.user, self.alice)

    def test_post_valid_data_redirects_to_list(self):
        """A successful POST should redirect to the note list page."""
        self.client.force_login(self.alice)
        response = self.client.post(
            self.url, {'title': 'My Note', 'content': 'Body'}
        )
        self.assertRedirects(response, reverse('note_list'))

    def test_post_invalid_data_shows_form_errors(self):
        """Submitting an empty title should re-render the form with errors."""
        self.client.force_login(self.alice)
        response = self.client.post(self.url, {'title': '', 'content': 'Body'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)


# ---------------------------------------------------------------------------
# Note Update View Tests
# ---------------------------------------------------------------------------

class NoteUpdateViewTests(TestCase):
    """Tests for the note_update view."""

    def setUp(self):
        self.client = Client()
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.note = make_note(self.alice, title='Original')

    def _url(self, pk=None):
        return reverse('note_update', kwargs={'pk': pk or self.note.pk})

    def test_redirects_anonymous_user(self):
        """Unauthenticated GET should redirect to login."""
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 302)

    def test_get_prefills_form_with_note_data(self):
        """GET should pre-fill the form with the note's existing values."""
        self.client.force_login(self.alice)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['form'].instance.pk, self.note.pk
        )

    def test_post_updates_note(self):
        """A valid POST should save the updated values to the database."""
        self.client.force_login(self.alice)
        self.client.post(self._url(), {'title': 'Updated', 'content': 'New'})
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated')

    def test_post_redirects_to_list(self):
        """A successful POST should redirect to the note list."""
        self.client.force_login(self.alice)
        response = self.client.post(
            self._url(), {'title': 'Updated', 'content': 'New'}
        )
        self.assertRedirects(response, reverse('note_list'))

    def test_other_user_gets_404(self):
        """Bob should receive a 404 when trying to edit Alice's note."""
        self.client.force_login(self.bob)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_note_returns_404(self):
        """Requesting a note that doesn't exist should return 404."""
        self.client.force_login(self.alice)
        response = self.client.get(self._url(pk=99999))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# Note Delete View Tests
# ---------------------------------------------------------------------------

class NoteDeleteViewTests(TestCase):
    """Tests for the note_delete view."""

    def setUp(self):
        self.client = Client()
        self.alice = make_user('alice')
        self.bob = make_user('bob')
        self.note = make_note(self.alice, title='To Delete')

    def _url(self, pk=None):
        return reverse('note_delete', kwargs={'pk': pk or self.note.pk})

    def test_redirects_anonymous_user(self):
        """Unauthenticated GET should redirect to login."""
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 302)

    def test_get_shows_confirmation_page(self):
        """GET should render the delete confirmation template."""
        self.client.force_login(self.alice)
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['note'], self.note)

    def test_post_deletes_note(self):
        """POST should remove the note from the database."""
        self.client.force_login(self.alice)
        self.client.post(self._url())
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

    def test_post_redirects_to_list(self):
        """Successful deletion should redirect to the note list."""
        self.client.force_login(self.alice)
        response = self.client.post(self._url())
        self.assertRedirects(response, reverse('note_list'))

    def test_other_user_cannot_delete(self):
        """Bob posting to delete Alice's note should return 404."""
        self.client.force_login(self.bob)
        response = self.client.post(self._url())
        self.assertEqual(response.status_code, 404)
        # Note must still exist after the failed attempt.
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())

    def test_nonexistent_note_returns_404(self):
        """Requesting deletion of a note that doesn't exist should 404."""
        self.client.force_login(self.alice)
        response = self.client.get(self._url(pk=99999))
        self.assertEqual(response.status_code, 404)


# ---------------------------------------------------------------------------
# URL Resolution Tests
# ---------------------------------------------------------------------------

class NoteURLTests(TestCase):
    """Confirm that named URLs resolve to the correct view functions."""

    def test_note_list_url(self):
        self.assertEqual(resolve(reverse('note_list')).func, views.note_list)

    def test_note_create_url(self):
        self.assertEqual(
            resolve(reverse('note_create')).func, views.note_create
        )

    def test_note_update_url(self):
        self.assertEqual(
            resolve(reverse('note_update', kwargs={'pk': 1})).func,
            views.note_update,
        )

    def test_note_delete_url(self):
        self.assertEqual(
            resolve(reverse('note_delete', kwargs={'pk': 1})).func,
            views.note_delete,
        )
