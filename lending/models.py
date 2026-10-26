from django.db import models

# Create your models here.
from datetime import timedelta
from django.db import models
from django.utils import timezone
from resources.models import BookCopy


class Borrower(models.Model):
    BORROWER_TYPES = [
        ('STUDENT', 'Student'),
        ('TEACHER', 'Teacher / Staff'),
    ]

    identifier = models.CharField(
        max_length=50,
        unique=True,
        db_index=True,
        help_text="Student Admission Number or Teacher Staff ID"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    borrower_type = models.CharField(max_length=10, choices=BORROWER_TYPES, default='STUDENT')
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    class_form = models.CharField(
        max_length=50,
        blank=True,
        help_text="E.g., Form 3 East, Grade 10, or French Department"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to freeze borrowing privileges"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.identifier})"

    @property
    def active_loans_count(self):
        return self.loans.filter(returned_at__isnull=True).count()


class Loan(models.Model):
    copy = models.ForeignKey(
        BookCopy,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    borrower = models.ForeignKey(
        Borrower,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    issued_at = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_at = models.DateTimeField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"{self.copy.accession_number} -> {self.borrower.identifier} (Due: {self.due_date})"

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now().date() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.returned_at is None:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0