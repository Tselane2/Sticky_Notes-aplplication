# forms.py — Defines the forms used in the sticky_notes app.
# Django's ModelForm automatically generates form fields from a model,
# so we don't have to define each field manually.

from django import forms
from .models import Note  # Import the Note model to base this form on


class NoteForm(forms.ModelForm):
    """
    A form for creating and editing Note objects.

    By using ModelForm, Django automatically:
      - Creates input fields for each listed field
      - Handles validation (e.g. required fields, max length)
      - Provides a .save() method that writes directly to the database

    We only expose 'title' and 'content' — the user field and timestamps
    are managed by the view and Django respectively, so they're excluded.
    """

    class Meta:
        # Tell Django which model this form is for.
        model = Note

        # Only include these fields in the rendered form.
        # 'user', 'created_at', and 'updated_at' are intentionally excluded.
        fields = ['title', 'content']
