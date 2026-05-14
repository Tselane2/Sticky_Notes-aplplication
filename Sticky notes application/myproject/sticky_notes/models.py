# models.py — Defines the database structure for the sticky_notes app.
# Each class here maps directly to a table in the database.

from django.db import models
from django.contrib.auth.models import User  # Django's built-in User model


class Note(models.Model):
    """
    Represents a single sticky note created by a user.

    Fields:
        user       — the owner of this note (links to Django's auth User)
        title      — short heading for the note (max 200 characters)
        content    — the main body text of the note
        created_at — automatically set to the date/time when the note is first saved
        updated_at — automatically updated every time the note is saved
    """

    # Link each note to the user who created it.
    # on_delete=CASCADE means if the user is deleted, all their notes are deleted too.
    # null=True / blank=True allows notes that were created before auth was added.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    # Short title shown on the note card — limited to 200 characters.
    title = models.CharField(max_length=200)

    # Main body of the note — no character limit (TextField stores long text).
    content = models.TextField()

    # Timestamp set once when the note is first created. auto_now_add means
    # Django fills this in automatically; we never set it manually.
    created_at = models.DateTimeField(auto_now_add=True)

    # Timestamp updated every time the note is saved. auto_now means Django
    # refreshes this field on every .save() call.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # This controls how a Note object is displayed in the admin panel
        # and in the Django shell. Returning the title keeps it human-readable.
        return self.title
