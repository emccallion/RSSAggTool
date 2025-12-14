from django.contrib import admin
from .models import SankeyDiagram, PublishedNode, NodeArticleAssociation


@admin.register(SankeyDiagram)
class SankeyDiagramAdmin(admin.ModelAdmin):
    """Admin interface for Sankey diagrams."""

    list_display = [
        'name',
        'description_short',
        'is_published',
        'created_by',
        'created_at',
        'updated_at',
    ]

    list_filter = [
        'is_published',
        'created_by',
        'created_at',
        'updated_at',
    ]

    search_fields = [
        'name',
        'description',
        'config_text',
    ]

    readonly_fields = ['created_at', 'updated_at', 'published_at']

    fieldsets = (
        ('Diagram Information', {
            'fields': ('name', 'description', 'created_by')
        }),
        ('Configuration', {
            'fields': ('config_text', 'settings_json')
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at')
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


@admin.register(PublishedNode)
class PublishedNodeAdmin(admin.ModelAdmin):
    """Admin interface for published nodes."""

    list_display = [
        'name',
        'sankey_diagram',
        'supporting_count',
        'conflicting_count',
        'created_at',
    ]

    list_filter = [
        'sankey_diagram',
        'created_at',
    ]

    search_fields = [
        'name',
        'sankey_diagram__name',
    ]

    readonly_fields = ['created_at']

    def supporting_count(self, obj):
        return obj.get_supporting_count()
    supporting_count.short_description = 'Supporting'

    def conflicting_count(self, obj):
        return obj.get_conflicting_count()
    conflicting_count.short_description = 'Conflicting'


@admin.register(NodeArticleAssociation)
class NodeArticleAssociationAdmin(admin.ModelAdmin):
    """Admin interface for node-article associations."""

    list_display = [
        'node',
        'article_title_short',
        'association_type',
        'score',
        'created_by',
        'created_at',
    ]

    list_filter = [
        'association_type',
        'created_at',
        'node__sankey_diagram',
    ]

    search_fields = [
        'node__name',
        'article__title',
        'created_by',
    ]

    readonly_fields = ['created_at']

    def article_title_short(self, obj):
        """Return shortened article title."""
        return obj.article.title[:50] + ('...' if len(obj.article.title) > 50 else '')
    article_title_short.short_description = 'Article'
