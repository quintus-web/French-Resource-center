from django.urls import path
from . import views

app_name = 'lending'

urlpatterns = [
    path('dashboard/', views.circulation_dashboard, name='dashboard'),
    path('members/', views.members_list, name='members'),
    path('members/register/', views.register_borrower, name='register_borrower'),
    path('issue/', views.issue_copy, name='issue'),
    path('return/<int:loan_id>/', views.return_copy, name='return'),
    path('bulk-import/', views.bulk_import, name='bulk_import'),
    path('search/members/', views.search_members, name='search_members'),
    path('search/books/', views.search_books, name='search_books'),
]