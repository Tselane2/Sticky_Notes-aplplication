# urls.py — URL routing for the sticky_notes app.
# This file maps URL patterns to the view functions defined in views.py.
# These URLs are mounted under /notes/ by the main project urls.py,
# so the full paths become: /notes/, /notes/create/, etc.

from django.urls import path
from . import views  # Import all views from this app

urlpatterns = [
    # /notes/ — show the list of all notes for the logged-in user
    path('', views.note_list, name='note_list'),

    # /notes/create/ — show the form to create a new note
    path('create/', views.note_create, name='note_create'),

    # /notes/update/<pk>/ — edit an existing note by its primary key (ID)
    # <int:pk> captures a positive integer from the URL and passes it to the view as 'pk'
    path('update/<int:pk>/', views.note_update, name='note_update'),

    # /notes/delete/<pk>/ — confirm and delete a note by its primary key
    path('delete/<int:pk>/', views.note_delete, name='note_delete'),
]
