from django import forms
from .models import Feed


class FeedForm(forms.ModelForm):
    """Form for creating and editing RSS feeds."""

    class Meta:
        model = Feed
        fields = ['source_name', 'url', 'category', 'active', 'description']
        widgets = {
            'source_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Financial Times'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/rss'
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description of this feed'
            }),
        }
