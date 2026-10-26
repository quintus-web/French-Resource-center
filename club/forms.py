from django import forms
from .models import ClubEvent, DELFStudyResource


class ClubEventForm(forms.ModelForm):
    class Meta:
        model = ClubEvent
        fields = ['title', 'event_type', 'date', 'start_time', 'location', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full text-sm border rounded-lg px-3 py-2',
                'placeholder': 'e.g. Concours d’Éloquence / French Debate'
            }),
            'event_type': forms.Select(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'location': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
        }


class DELFResourceForm(forms.ModelForm):
    class Meta:
        model = DELFStudyResource
        fields = ['title', 'level', 'skill', 'url', 'description', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2', 'placeholder': 'e.g. RFI Journal en français facile'}),
            'level': forms.Select(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'skill': forms.Select(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2'}),
            'url': forms.URLInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2', 'placeholder': 'https://...'}),
            'description': forms.TextInput(attrs={'class': 'w-full text-sm border rounded-lg px-3 py-2', 'placeholder': 'Recommended 10 min daily audio'}),
        }