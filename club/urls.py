from django.urls import path
from . import views

app_name = 'club'

urlpatterns = [
    path('dashboard/', views.club_dashboard, name='dashboard'),
    path('event/create/', views.create_event, name='create_event'),
    path('event/<int:event_id>/attendance/', views.event_attendance, name='event_attendance'),
    path('delf/', views.delf_resources, name='delf_resources'),
    path('delf/add/', views.add_delf_resource, name='add_delf'),
    path('media/', views.media_hub, name='media_hub'),
]