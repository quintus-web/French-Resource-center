from django.urls import path
from . import views

app_name = 'lending'

urlpatterns = [
    path('dashboard/', views.circulation_dashboard, name='dashboard'),
    path('issue/', views.issue_copy, name='issue'),
    path('return/<int:loan_id>/', views.return_copy, name='return'),
]