from django import forms
from .models import PreprocessingArticle


class ArticleFilterForm(forms.Form):
    """Form for filtering articles in the list view."""

    outcome = forms.ChoiceField(
        choices=[('', 'All')] + list(PreprocessingArticle.OUTCOME_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    source = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Source name...'
        })
    )

    storygroup = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Story group...'
        })
    )

    search = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search title...'
        })
    )

    added_by = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Added by...'
        })
    )


class ArticleEditForm(forms.ModelForm):
    """Form for editing preprocessing article fields."""

    class Meta:
        model = PreprocessingArticle
        fields = ['outcome', 'storygroup', 'modified_by']
        widgets = {
            'outcome': forms.Select(attrs={'class': 'form-control'}),
            'storygroup': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter story group name...'
            }),
            'modified_by': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your name...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make modified_by field more user-friendly
        self.fields['modified_by'].required = False
        self.fields['storygroup'].required = False


class BulkActionForm(forms.Form):
    """Form for bulk actions on multiple articles."""

    action = forms.ChoiceField(
        choices=[
            ('', 'Select action...'),
            ('mark_processed', 'Mark as Processed'),
            ('mark_rejected', 'Mark as Rejected'),
            ('mark_new', 'Mark as New'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    selected_articles = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    storygroup = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Story group (optional)...'
        })
    )

    modified_by = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Your name (optional)...'
        })
    )
