"""
settings.py — Django project configuration for myproject.

This file controls every aspect of the Django application:
database, installed apps, middleware, templates, static files,
authentication, and more. Keep secrets out of this file in production
— use environment variables instead (see SECRET_KEY below).
"""

import os
from pathlib import Path

# BASE_DIR points to the root of the Django project (the folder containing manage.py).
# All other paths in this file are built relative to it.
BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Security settings
# ---------------------------------------------------------------------------

# SECRET_KEY is used for cryptographic signing (sessions, CSRF tokens, etc.).
# We read it from an environment variable so it's never hard-coded in source
# control. The fallback value is only used locally during development.
SECRET_KEY = os.environ.get(
    'SESSION_SECRET',
    'django-insecure-53=no+z7leenfqyw2wnei2qv(98+9@(r)enfo_%)17@u3@zvx-'
)

# DEBUG=True enables detailed error pages. Must be False in production.
DEBUG = True

# Allow requests from any host. Fine for development; restrict this in production
# to your actual domain (e.g. ALLOWED_HOSTS = ['mysite.com']).
ALLOWED_HOSTS = ['*']

# CSRF_TRUSTED_ORIGINS tells Django which origins are allowed to submit forms.
# This is needed because Replit serves the app through a proxy domain that
# includes a port number, which Django's CSRF middleware checks against.
CSRF_TRUSTED_ORIGINS = [
    'https://*.replit.dev',         # General Replit preview domains
    'https://*.riker.replit.dev',   # Riker-specific Replit proxy domains
] + [
    # Add each domain listed in REPLIT_DOMAINS without a port
    f"https://{host}" for host in os.environ.get('REPLIT_DOMAINS', '').split(',') if host
] + [
    # Also trust the same domains with the Django dev server port (8000)
    f"https://{host}:8000" for host in os.environ.get('REPLIT_DOMAINS', '').split(',') if host
]


# ---------------------------------------------------------------------------
# Application definition
# ---------------------------------------------------------------------------

# INSTALLED_APPS lists every Django app that is active in this project.
# Django apps provide models, views, templates, management commands, etc.
INSTALLED_APPS = [
    'django.contrib.admin',         # The built-in admin panel (/admin/)
    'django.contrib.auth',          # Authentication framework (users, groups, permissions)
    'django.contrib.contenttypes',  # Framework for generic relations between models
    'django.contrib.sessions',      # Server-side session storage
    'django.contrib.messages',      # One-time flash messaging framework
    'django.contrib.staticfiles',   # Manages and serves CSS, JS, and image files
    'sticky_notes',                 # Our custom app for managing sticky notes
]

# Middleware runs on every request and response, in order.
# Each layer can inspect or modify the request before it reaches the view,
# or modify the response before it's sent back to the browser.
MIDDLEWARE = [
    # Enforces HTTPS, sets security headers.
    'django.middleware.security.SecurityMiddleware',
    # Enables server-side session storage.
    'django.contrib.sessions.middleware.SessionMiddleware',
    # URL normalisation — appends trailing slashes, handles redirects.
    'django.middleware.common.CommonMiddleware',
    # Protects all POST forms against Cross-Site Request Forgery attacks.
    'django.middleware.csrf.CsrfViewMiddleware',
    # Attaches the logged-in User object to every incoming request.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # Enables one-time flash messages between views.
    'django.contrib.messages.middleware.MessageMiddleware',
    # Sends X-Frame-Options headers to prevent clickjacking.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Points Django to the root URL configuration file.
ROOT_URLCONF = 'myproject.urls'

# Template engine configuration.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Extra directories to search for templates (empty = app dirs only).
        'DIRS': [],
        # Automatically find templates inside each app's /templates/ folder.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Makes the request object available in every template
                'django.template.context_processors.request',
                # Makes the logged-in user and their permissions available in templates
                'django.contrib.auth.context_processors.auth',
                # Makes flash messages available in templates
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Entry point for the WSGI server (used by Gunicorn in production).
WSGI_APPLICATION = 'myproject.wsgi.application'


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

# SQLite is the default — it stores everything in a single file and requires
# zero configuration. Ideal for development. For production, swap this for
# PostgreSQL by changing ENGINE and providing credentials.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # File lives in the project root
    }
}


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

# These validators run when a user sets or changes their password.
# Django checks the new password against all of them before accepting it.
AUTH_PASSWORD_VALIDATORS = [
    {
        # Rejects passwords that are too similar to the user's username or email.
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Rejects passwords shorter than 8 characters (Django's default minimum).
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Rejects passwords that appear in a list of 20,000 common passwords.
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Rejects passwords that consist entirely of numbers.
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ---------------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'en-us'  # Default language for the site
# All datetimes are stored in UTC. Convert to local time in templates if needed.
TIME_ZONE = 'UTC'
USE_I18N = True  # Enables Django's translation framework
USE_TZ = True    # Store all datetimes as timezone-aware values in the database


# ---------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# ---------------------------------------------------------------------------

# The URL prefix Django uses when linking to static files in templates.
# e.g. {% static 'sticky_notes/css/styles.css' %} resolves to /static/sticky_notes/css/styles.css
STATIC_URL = 'static/'


# ---------------------------------------------------------------------------
# Primary key type
# ---------------------------------------------------------------------------

# Use BigAutoField (64-bit integer) as the default primary key for all models.
# This gives more headroom than the older 32-bit AutoField.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Authentication redirects
# ---------------------------------------------------------------------------

# Where to send unauthenticated users who try to access a @login_required view.
LOGIN_URL = '/accounts/login/'

# Where to redirect users after a successful login.
LOGIN_REDIRECT_URL = '/notes/'

# Where to redirect users after they log out.
LOGOUT_REDIRECT_URL = '/accounts/login/'


# ---------------------------------------------------------------------------
# Email backend
# ---------------------------------------------------------------------------

# In development, we use the console backend — it prints emails to the terminal
# instead of actually sending them. This makes it easy to copy the password
# reset link from the Django App workflow logs without needing an SMTP server.
#
# For production, replace this with a real backend, for example:
#   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# and set EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, etc.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@stickynotes.local'
