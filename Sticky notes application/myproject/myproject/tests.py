# myproject/tests.py — Unit tests for project-level views.
#
# Coverage:
#   - RegistrationViewTests : GET render, POST valid/invalid, already-logged-in redirect

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class RegistrationViewTests(TestCase):
    """Tests for the custom register view at /accounts/register/."""

    def setUp(self):
        self.client = Client()
        self.url = reverse('register')
        self.valid_data = {
            'username': 'newuser',
            'password1': 'Testpass123!',
            'password2': 'Testpass123!',
        }

    def test_get_renders_registration_form(self):
        """GET should return 200 and render a form."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_post_valid_data_creates_user(self):
        """A valid POST should create a new User in the database."""
        self.client.post(self.url, self.valid_data)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_post_valid_data_logs_user_in(self):
        """After registration the user should be logged in automatically."""
        self.client.post(self.url, self.valid_data)
        # _auth_user_id in session means the user is authenticated.
        self.assertIn('_auth_user_id', self.client.session)

    def test_post_valid_data_redirects_to_note_list(self):
        """A successful registration should redirect to /notes/."""
        response = self.client.post(self.url, self.valid_data)
        self.assertRedirects(response, reverse('note_list'))

    def test_post_password_mismatch_shows_errors(self):
        """Mismatched passwords should re-render the form with errors."""
        data = {**self.valid_data, 'password2': 'WrongPassword!'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_post_duplicate_username_shows_errors(self):
        """Registering with an existing username should fail validation."""
        User.objects.create_user(username='newuser', password='Anything1!')
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_post_empty_form_shows_errors(self):
        """Submitting a blank form should return errors, not create a user."""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_already_authenticated_user_redirected(self):
        """A logged-in user visiting /register/ should go straight to /notes/."""
        user = User.objects.create_user(username='existing', password='Pass123!')
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('note_list'))
