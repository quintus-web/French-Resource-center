from django import forms
from .models import Borrower, Loan


class IssueBookForm(forms.Form):
    accession_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Scan or enter accession code',
            'class': 'w-full text-sm border rounded-lg px-3 py-2 uppercase font-mono'
        })
    )
    borrower_identifier = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Admission No / Staff ID',
            'class': 'w-full text-sm border rounded-lg px-3 py-2'
        })
    )
    loan_duration_days = forms.IntegerField(
        initial=14,
        min_value=1,
        max_value=90,
        widget=forms.NumberInput(attrs={
            'class': 'w-full text-sm border rounded-lg px-3 py-2'
        })
    )


class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = ['identifier', 'first_name', 'last_name', 'borrower_type', 'class_form', 'phone']
        widgets = {
            'identifier': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2', 'placeholder': 'Admission No / Staff ID'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'borrower_type': forms.Select(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'class_form': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2', 'placeholder': 'e.g. Form 3 East'}),
            'phone': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2', 'placeholder': 'Optional'}),
        }