from django.contrib import admin
from .models import Feed


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    """Admin interface for RSS Feed management."""

    list_display = [
        'active_status',
        'source_name',
        'category',
        'url_short',
        'created_at',
    ]

    list_filter = [
        'active',
        'source_name',
        'category',
        'created_at',
    ]

    search_fields = [
        'source_name',
        'url',
        'description',
    ]

    fieldsets = (
        ('Feed Information', {
            'fields': ('source_name', 'url', 'category', 'active')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    actions = ['activate_feeds', 'deactivate_feeds']

    def active_status(self, obj):
        """Display active status with icon."""
        return '✓ Active' if obj.active else '✗ Inactive'
    active_status.short_description = 'Status'

    def url_short(self, obj):
        """Display shortened URL."""
        return obj.url[:60] + '...' if len(obj.url) > 60 else obj.url
    url_short.short_description = 'Feed URL'

    def activate_feeds(self, request, queryset):
        """Bulk action to activate feeds."""
        count = queryset.update(active=True)
        self.message_user(request, f'{count} feed(s) activated.')
    activate_feeds.short_description = 'Activate selected feeds'

    def deactivate_feeds(self, request, queryset):
        """Bulk action to deactivate feeds."""
        count = queryset.update(active=False)
        self.message_user(request, f'{count} feed(s) deactivated.')
    deactivate_feeds.short_description = 'Deactivate selected feeds'
