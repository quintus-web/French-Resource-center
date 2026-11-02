from django.shortcuts import render

# Create your views here.
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from resources.models import BookCopy
from .forms import BorrowerForm, IssueBookForm
from .models import Borrower, Loan


@login_required
def circulation_dashboard(request):
    active_loans = Loan.objects.filter(returned_at__isnull=True).select_related('copy__resource', 'borrower')
    recent_returns = Loan.objects.filter(returned_at__isnull=False).select_related('copy__resource', 'borrower')[:10]
    
    overdue_count = sum(1 for loan in active_loans if loan.is_overdue)
    
    issue_form = IssueBookForm()
    borrower_form = BorrowerForm()

    context = {
        'active_loans': active_loans,
        'recent_returns': recent_returns,
        'total_active': active_loans.count(),
        'total_overdue': overdue_count,
        'issue_form': issue_form,
        'borrower_form': borrower_form,
    }
    return render(request, 'lending/dashboard.html', context)


@login_required
@transaction.atomic
def issue_copy(request):
    if request.method == 'POST':
        form = IssueBookForm(request.POST)
        if form.is_valid():
            accession_number = form.cleaned_data['accession_number'].strip().upper()
            identifier = form.cleaned_data['borrower_identifier'].strip()
            duration_days = form.cleaned_data['loan_duration_days']

            # Acquire pessimistic row lock
            try:
                copy = BookCopy.objects.select_for_update().get(accession_number=accession_number)
            except BookCopy.DoesNotExist:
                messages.error(request, f"Accession code '{accession_number}' does not exist.")
                return redirect('lending:dashboard')

            if copy.status != 'AVAILABLE':
                messages.error(request, f"Copy {accession_number} is not available (Current status: {copy.get_status_display()}).")
                return redirect('lending:dashboard')

            try:
                borrower = Borrower.objects.get(identifier=identifier, is_active=True)
            except Borrower.DoesNotExist:
                messages.error(request, f"Borrower '{identifier}' not registered or card is inactive.")
                return redirect('lending:dashboard')

            # Create loan and update copy state
            due_date = timezone.now().date() + timedelta(days=duration_days)
            Loan.objects.create(copy=copy, borrower=borrower, due_date=due_date)

            copy.status = 'ISSUED'
            copy.save(update_fields=['status'])

            messages.success(request, f"Successfully issued '{copy.resource.title}' to {borrower.first_name} {borrower.last_name}.")
    return redirect('lending:dashboard')


@login_required
@transaction.atomic
def return_copy(request, loan_id):
    if request.method == 'POST':
        loan = get_object_or_404(
            Loan.objects.select_for_update().select_related('copy'), 
            id=loan_id, 
            returned_at__isnull=True
        )
        
        loan.returned_at = timezone.now()
        loan.save(update_fields=['returned_at'])

        copy = loan.copy
        copy.status = 'AVAILABLE'
        copy.save(update_fields=['status'])

        messages.success(request, f"Copy '{copy.accession_number}' returned and restored to available inventory.")
    return redirect('lending:dashboard')

import csv
import io
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from lending.models import Borrower
from resources.models import Resource, BookCopy  # adjust model names if titled BookCopy


@login_required
def bulk_import(request):
    if request.method == 'POST':
        import_type = request.POST.get('import_type')
        csv_file = request.FILES.get('csv_file')

        if not csv_file or not csv_file.name.endswith('.csv'):
            messages.error(request, "Please upload a valid .csv file.")
            return redirect('lending:bulk_import')

        try:
            decoded_file = io.TextIOWrapper(csv_file.file, encoding='utf-8-sig')
            reader = csv.DictReader(decoded_file)
            created_count = 0
            skipped_count = 0

            with transaction.atomic():
                if import_type == 'members':
                    for row in reader:
                        identifier = row.get('identifier', '').strip()
                        first_name = row.get('first_name', '').strip()
                        last_name = row.get('last_name', '').strip()
                        class_form = row.get('class_form', '').strip()
                        borrower_type = row.get('borrower_type', 'Student').strip()

                        if not identifier or not first_name or not last_name:
                            skipped_count += 1
                            continue

                        _, created = Borrower.objects.get_or_create(
                            identifier=identifier,
                            defaults={
                                'first_name': first_name,
                                'last_name': last_name,
                                'class_form': class_form,
                                'borrower_type': borrower_type,
                                'is_active': True,
                            }
                        )
                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1

                    messages.success(request, f"Imported {created_count} members ({skipped_count} skipped or already existed).")

                elif import_type == 'books':
                    for row in reader:
                        title = row.get('title', '').strip()
                        author = row.get('author', '').strip()
                        level = row.get('level', 'A1').strip().upper()
                        category = row.get('category', 'Roman / Fiction').strip()
                        accession_number = row.get('accession_number', '').strip()
                        shelf_location = row.get('shelf_location', 'General Shelf').strip()

                        if not title or not accession_number:
                            skipped_count += 1
                            continue

                        # Ensure parent resource exists
                        resource, _ = Resource.objects.get_or_create(
                            title=title,
                            author=author,
                            defaults={
                                'level': level,
                                'category': category,
                            }
                        )

                        # Create copy if accession number does not exist
                        _, copy_created = BookCopy.objects.get_or_create(
                            accession_number=accession_number,
                            defaults={
                                'resource': resource,
                                'shelf_location': shelf_location,
                                'status': 'AVAILABLE',
                            }
                        )
                        if copy_created:
                            created_count += 1
                        else:
                            skipped_count += 1

                    messages.success(request, f"Imported {created_count} book copies ({skipped_count} skipped or duplicate accession numbers).")

        except Exception as e:
            messages.error(request, f"Import error: {str(e)}")

        return redirect('lending:bulk_import')

    return render(request, 'lending/bulk_import.html')