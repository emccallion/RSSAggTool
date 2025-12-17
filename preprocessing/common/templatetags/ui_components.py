"""
Template tags for reusable UI components.
"""
from django import template

register = template.Library()


@register.inclusion_tag('components/stat_card.html')
def stat_card(value, label, variant='primary', icon=None):
    """
    Render a statistics card.

    Args:
        value: The numeric value to display
        label: The label text
        variant: Card color variant (primary, info, success, warning, danger)
        icon: Optional Bootstrap icon class

    Example:
        {% load ui_components %}
        {% stat_card stats.total "Total Articles" variant="primary" icon="bi-newspaper" %}
    """
    return {
        'value': value,
        'label': label,
        'variant': variant,
        'icon': icon
    }


@register.inclusion_tag('components/filter_panel.html', takes_context=True)
def filter_panel(context, form, action_url=None, show_sort=True):
    """
    Render a filter panel with form.

    Args:
        form: The filter form instance
        action_url: The form action URL (default: current path)
        show_sort: Whether to show sort field

    Example:
        {% load ui_components %}
        {% filter_panel filter_form action_url=request.path %}
    """
    return {
        'form': form,
        'action_url': action_url,
        'show_sort': show_sort,
        'request': context.get('request')
    }


@register.inclusion_tag('components/pagination.html', takes_context=True)
def pagination_controls(context, page_obj):
    """
    Render pagination controls.

    Args:
        page_obj: Django paginator page object

    Example:
        {% load ui_components %}
        {% pagination_controls page_obj %}
    """
    return {
        'page_obj': page_obj,
        'request': context.get('request')
    }


@register.simple_tag(takes_context=True)
def pagination_url(context, page_number):
    """
    Generate a URL for a pagination page number, preserving query parameters.

    Args:
        page_number: The page number

    Example:
        {% load ui_components %}
        <a href="{% pagination_url 2 %}">Page 2</a>
    """
    request = context.get('request')
    if not request:
        return f"?page={page_number}"

    params = request.GET.copy()
    params['page'] = page_number
    return f"?{params.urlencode()}"


@register.filter
def add_class(field, css_class):
    """
    Add a CSS class to a form field widget.

    Args:
        field: Form field
        css_class: CSS class to add

    Example:
        {{ form.field|add_class:"form-control" }}
    """
    return field.as_widget(attrs={'class': css_class})


@register.filter
def has_error(form, field_name):
    """
    Check if a form field has errors.

    Args:
        form: Form instance
        field_name: Name of the field

    Example:
        {% if form|has_error:"email" %}...{% endif %}
    """
    return field_name in form.errors
