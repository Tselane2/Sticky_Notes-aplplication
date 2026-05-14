# myproject/urls.py — The root URL configuration for the entire project.
# Django reads this file first when a request comes in and decides which
# view function should handle it based on the URL pattern.

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views  # Django's built-in login/logout/reset views
from . import views as project_views                 # Our custom registration view


urlpatterns = [

    # --- Django Admin ---
    # The built-in admin panel. Access at /admin/ after running createsuperuser.
    path('admin/', admin.site.urls),

    # --- Sticky Notes App ---
    # All note-related URLs are defined in sticky_notes/urls.py and mounted here.
    # e.g. /notes/, /notes/create/, /notes/update/1/, /notes/delete/1/
    path('notes/', include('sticky_notes.urls')),

    # --- Authentication ---
    # Login and logout are handled by Django's built-in class-based views.
    # We just point them at the right URL and supply matching templates.
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Custom registration view — creates a new user and logs them in.
    path('accounts/register/', project_views.register, name='register'),

    # --- Password Reset Flow ---
    # Four steps that Django handles entirely — we only supply the templates.
    # Step 1: User enters their email address to request a reset link.
    path('accounts/password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    # Step 2: Confirmation page shown after the reset email has been sent.
    path(
        'accounts/password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),

    # Step 3: The link from the email — user sets their new password here.
    # <uidb64> is the base64-encoded user ID; <token> is a one-time security token.
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),

    # Step 4: Success page shown after the password has been changed.
    path(
        'accounts/reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),

    # --- Root Redirect ---
    # Visiting / redirects straight to /notes/ so there's no blank landing page.
    path('', lambda request: redirect('note_list'), name='home'),
]
