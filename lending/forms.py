from django import forms
from .models import Borrower, Loan
from resources.models import BookCopy


class IssueBookForm(forms.Form):
    borrower_identifier = forms.CharField(
        max_length=50,
        label='Student / Staff',
        widget=forms.TextInput(attrs={
            'placeholder': 'Type name or ID to search…',
            'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 outline-none',
            'id': 'borrowerSearch',
            'autocomplete': 'off',
        })
    )
    accession_number = forms.CharField(
        max_length=50,
        label='Book',
        widget=forms.TextInput(attrs={
            'placeholder': 'Type book title or accession code…',
            'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 outline-none',
            'id': 'bookSearch',
            'autocomplete': 'off',
        })
    )
    loan_duration_days = forms.IntegerField(
        initial=14,
        min_value=1,
        max_value=90,
        label='Loan period (days)',
        widget=forms.NumberInput(attrs={
            'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-400 outline-none',
        })
    )


class BorrowerForm(forms.ModelForm):
    class Meta:
        model = Borrower
        fields = ['identifier', 'first_name', 'last_name', 'borrower_type', 'class_form', 'department', 'phone', 'email']
        widgets = {
            'identifier':     forms.TextInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2', 'placeholder': 'Admission No / Staff ID'}),
            'first_name':     forms.TextInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2'}),
            'last_name':      forms.TextInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2'}),
            'borrower_type':  forms.Select(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2', 'id': 'id_borrower_type', 'onchange': 'toggleMemberFields()'}),
            'class_form':     forms.TextInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2', 'placeholder': 'e.g. Form 3 East'}),
            'department':     forms.TextInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2', 'placeholder': 'e.g. Sciences, Administration'}),
            'phone':          forms.TextInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2', 'placeholder': 'Optional'}),
            'email':          forms.EmailInput(attrs={'class': 'w-full text-sm border border-slate-300 rounded-lg px-3 py-2', 'placeholder': 'Optional'}),
        }
        labels = {
            'identifier':    'Admission / Staff ID',
            'borrower_type': 'Member Type',
            'class_form':    'Class / Form',
            'department':    'Department',
        }