from django.contrib import admin
from .models import SankeyDiagram


@admin.register(SankeyDiagram)
class SankeyDiagramAdmin(admin.ModelAdmin):
    """Admin interface for Sankey diagrams."""

    list_display = [
        'name',
        'description_short',
        'created_by',
        'created_at',
        'updated_at',
    ]

    list_filter = [
        'created_by',
        'created_at',
        'updated_at',
    ]

    search_fields = [
        'name',
        'description',
        'config_text',
    ]

    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Diagram Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Configuration', {
            'fields': ('config_text', 'settings_json')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def description_short(self, obj):
        """Return shortened description."""
        if obj.description:
            return obj.description[:50] + ('...' if len(obj.description) > 50 else '')
        return '-'
    description_short.short_description = 'Description'
