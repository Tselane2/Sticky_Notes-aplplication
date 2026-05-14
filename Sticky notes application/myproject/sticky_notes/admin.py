# admin.py — Registers models with Django's built-in admin panel.
# Once registered, staff users can view, search, create, edit, and delete
# records directly from /admin/ without touching the database manually.

from django.contrib import admin
from .models import Note  # Import the Note model we want to manage


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """
    Customises how Note objects appear and behave inside the admin panel.
    """

    # Columns to show in the list view of all notes at /admin/sticky_notes/note/
    list_display = ('title', 'created_at', 'updated_at')

    # Enables the search bar at the top of the list — searches across title and content.
    search_fields = ('title', 'content')

    # These fields will be visible in the detail view but cannot be edited,
    # because they are auto-managed by Django (auto_now_add / auto_now).
    readonly_fields = ('created_at', 'updated_at')
