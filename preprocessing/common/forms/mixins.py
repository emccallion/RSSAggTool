"""
Form mixins for common patterns.
"""
from django import forms


class BootstrapFormMixin:
    """
    Mixin that automatically adds Bootstrap classes to form fields.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            # Add form-control class to most field types
            if isinstance(field.widget, (
                forms.TextInput,
                forms.EmailInput,
                forms.URLInput,
                forms.PasswordInput,
                forms.NumberInput,
                forms.Textarea,
                forms.Select,
            )):
                field.widget.attrs.setdefault('class', 'form-control')

            # Add form-check-input to checkboxes
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')

            # Add form-check-input to radio buttons
            elif isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.setdefault('class', 'form-check-input')


class FilterFormMixin:
    """
    Mixin that provides helper methods for filtering querysets.
    """

    def apply_filters(self, queryset):
        """
        Apply filters from cleaned_data to a queryset.

        Override filter_methods dictionary to customize field filtering:

        filter_methods = {
            'field_name': lambda qs, value: qs.filter(custom_lookup=value)
        }
        """
        if not hasattr(self, 'cleaned_data'):
            raise ValueError("Form must be validated before applying filters")

        filter_methods = getattr(self, 'filter_methods', {})

        for field_name, value in self.cleaned_data.items():
            if value:
                # Check for custom filter method
                if field_name in filter_methods:
                    queryset = filter_methods[field_name](queryset, value)
                # Default filtering
                elif field_name != 'sort':  # Skip sort field
                    queryset = queryset.filter(**{field_name: value})

        return queryset

    def apply_ordering(self, queryset):
        """Apply ordering based on sort field."""
        if not hasattr(self, 'cleaned_data'):
            raise ValueError("Form must be validated before applying ordering")

        sort = self.cleaned_data.get('sort')
        if sort:
            queryset = queryset.order_by(sort)

        return queryset


class PlaceholderMixin:
    """
    Mixin that adds placeholder text to form fields based on labels.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('placeholder'):
                placeholder = field.label or field_name.replace('_', ' ').title()
                field.widget.attrs['placeholder'] = f"Enter {placeholder.lower()}"
