# myproject/views.py — Project-level views that don't belong to a specific app.
# Currently handles user registration. Login and logout are handled by
# Django's built-in auth views configured in urls.py.

from django.shortcuts import render, redirect
from django.contrib.auth import login                   # Logs the user in after registration
from django.contrib.auth.forms import UserCreationForm  # Django's built-in registration form


def register(request):
    """
    Handle new user registration.
    - GET  request: display the registration form.
    - POST request: validate the form, create the user, log them in, and redirect.

    If the user is already logged in, skip the form and send them straight
    to their notes — no point showing the register page to an active session.
    """

    # Redirect already-authenticated users away from the registration page.
    if request.user.is_authenticated:
        return redirect('note_list')

    if request.method == 'POST':
        # Bind the submitted form data to Django's built-in UserCreationForm.
        # This form validates username, password strength, and password confirmation.
        form = UserCreationForm(request.POST)

        if form.is_valid():
            # Save the new user to the database.
            user = form.save()

            # Automatically log the new user in so they don't have to sign in
            # immediately after registering — better user experience.
            login(request, user)

            # Send the newly registered user straight to their notes page.
            return redirect('note_list')
    else:
        # GET request — show an empty registration form.
        form = UserCreationForm()

    # Render the registration template, passing in the form (empty or with errors).
    return render(request, 'registration/register.html', {'form': form})
