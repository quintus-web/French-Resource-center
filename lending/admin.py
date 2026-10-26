from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Borrower, Loan


@admin.register(Borrower)
class BorrowerAdmin(admin.ModelAdmin):
    list_display = ('identifier', 'first_name', 'last_name', 'borrower_type', 'class_form', 'is_active', 'active_loans_count')
    list_filter = ('borrower_type', 'is_active')
    search_fields = ('identifier', 'first_name', 'last_name', 'class_form')


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('copy', 'borrower', 'issued_at', 'due_date', 'returned_at', 'overdue_status')
    list_filter = ('returned_at', 'due_date')
    search_fields = ('copy__accession_number', 'copy__resource__title', 'borrower__identifier', 'borrower__last_name')

    @admin.display(description='Overdue?', boolean=True)
    def overdue_status(self, obj):
        return obj.is_overdue
    