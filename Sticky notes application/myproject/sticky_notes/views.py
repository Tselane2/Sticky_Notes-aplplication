# views.py — Handles the request/response logic for the sticky_notes app.
# Each function here corresponds to one page or action in the app.
# All views are protected with @login_required, so unauthenticated users
# are redirected to the login page automatically.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required  # Protects views from anonymous users
from .models import Note
from .forms import NoteForm


@login_required
def note_list(request):
    """
    Display all notes that belong to the currently logged-in user.
    Notes are sorted by newest first using '-created_at' (the minus sign reverses the order).
    """
    # Filter to only show notes owned by the current user — other users' notes are never returned.
    notes = Note.objects.filter(user=request.user).order_by('-created_at')

    # Pass the queryset to the template so it can loop over and display each note.
    return render(request, 'notes/note_list.html', {'notes': notes})


@login_required
def note_create(request):
    """
    Handle creating a new note.
    - GET  request: show a blank form.
    - POST request: validate and save the form data as a new Note.
    """
    if request.method == 'POST':
        # Populate the form with the submitted data.
        form = NoteForm(request.POST)

        if form.is_valid():
            # commit=False gives us the Note object without saving it to the database yet.
            # This lets us attach the current user before the final save.
            note = form.save(commit=False)
            note.user = request.user  # Assign ownership to the logged-in user
            note.save()              # Now save to the database

            # After a successful save, redirect to the note list page.
            return redirect('note_list')
    else:
        # GET request — show an empty form for the user to fill in.
        form = NoteForm()

    return render(request, 'notes/note_form.html', {'form': form})


@login_required
def note_update(request, pk):
    """
    Handle editing an existing note.
    - pk: the primary key (unique ID) of the note to edit.
    - GET  request: show the form pre-filled with the existing note data.
    - POST request: validate the updated data and save it.

    get_object_or_404 automatically returns a 404 page if the note doesn't
    exist OR doesn't belong to this user — preventing users from editing
    each other's notes.
    """
    # Fetch the note, making sure it belongs to the logged-in user.
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        # Bind the submitted data to the existing note instance.
        form = NoteForm(request.POST, instance=note)

        if form.is_valid():
            form.save()  # Save the updated fields to the database
            return redirect('note_list')
    else:
        # GET request — pre-fill the form with the note's current values.
        form = NoteForm(instance=note)

    return render(request, 'notes/note_form.html', {'form': form})


@login_required
def note_delete(request, pk):
    """
    Handle deleting a note.
    - GET  request: show a confirmation page before deleting.
    - POST request: permanently delete the note and redirect to the list.

    Using a POST for the actual delete (not just a GET link) is a security
    best practice — it prevents accidental or malicious deletion via a URL.
    """
    # Fetch the note, ensuring it belongs to the logged-in user.
    note = get_object_or_404(Note, pk=pk, user=request.user)

    if request.method == 'POST':
        # The user confirmed the deletion — remove the record from the database.
        note.delete()
        return redirect('note_list')

    # GET request — show the confirmation page with the note's details.
    return render(request, 'notes/note_confirm_delete.html', {'note': note})
