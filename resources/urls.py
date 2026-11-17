from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('catalogue/', views.catalogue, name='catalogue'),
    path('catalogue/<int:pk>/', views.resource_detail, name='resource_detail'),
    path('catalogue/<int:pk>/upload-cover/', views.upload_cover, name='upload_cover'),
]
