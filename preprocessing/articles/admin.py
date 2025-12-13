from django.contrib import admin
from .models import PreprocessingArticle, NewsArticle


@admin.register(PreprocessingArticle)
class PreprocessingArticleAdmin(admin.ModelAdmin):
    """Admin interface for PreprocessingArticle."""

    list_display = [
        'title_short',
        'source',
        'outcome',
        'storygroup',
        'added_by',
        'published',
        'time_added',
    ]

    list_filter = [
        'outcome',
        'source',
        'added_by',
        'time_added',
    ]

    search_fields = [
        'title',
        'description',
        'source',
        'storygroup',
    ]

    readonly_fields = [
        'time_added',
        'last_synced',
        'source_article_id',
        'fetched_at',
    ]

    fieldsets = (
        ('Article Information', {
            'fields': ('title', 'link', 'description', 'summary', 'source', 'category', 'author', 'published')
        }),
        ('Preprocessing Info', {
            'fields': ('outcome', 'storygroup', 'added_by', 'modified_by')
        }),
        ('Metadata', {
            'fields': ('time_added', 'last_synced', 'source_article_id', 'fetched_at'),
            'classes': ('collapse',)
        }),
    )

    date_hierarchy = 'time_added'

    actions = ['mark_as_processed', 'mark_as_rejected', 'mark_as_new']

    def title_short(self, obj):
        """Return shortened title for list display."""
        return obj.title[:75] + '...' if len(obj.title) > 75 else obj.title
    title_short.short_description = 'Title'

    def mark_as_processed(self, request, queryset):
        """Bulk action to mark articles as processed."""
        count = queryset.update(outcome='processed')
        self.message_user(request, f'{count} article(s) marked as processed.')
    mark_as_processed.short_description = 'Mark selected as Processed'

    def mark_as_rejected(self, request, queryset):
        """Bulk action to mark articles as rejected."""
        count = queryset.update(outcome='rejected')
        self.message_user(request, f'{count} article(s) marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected as Rejected'

    def mark_as_new(self, request, queryset):
        """Bulk action to mark articles as new."""
        count = queryset.update(outcome='NEW')
        self.message_user(request, f'{count} article(s) marked as new.')
    mark_as_new.short_description = 'Mark selected as New'


@admin.register(NewsArticle)
class NewsArticleAdmin(admin.ModelAdmin):
    """Read-only admin interface for NewsArticle (from news.db)."""

    list_display = [
        'title_short',
        'source',
        'category',
        'published',
        'fetched_at',
    ]

    list_filter = [
        'source',
        'category',
        'published',
    ]

    search_fields = [
        'title',
        'description',
        'source',
    ]

    readonly_fields = [
        'title', 'link', 'description', 'summary', 'content',
        'source', 'category', 'feed_url', 'guid', 'author',
        'published', 'fetched_at', 'processed_at', 'created_at'
    ]

    date_hierarchy = 'published'

    def title_short(self, obj):
        """Return shortened title for list display."""
        return obj.title[:75] + '...' if len(obj.title) > 75 else obj.title
    title_short.short_description = 'Title'

    def has_add_permission(self, request):
        """No adding articles directly (read-only from news.db)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """No deleting articles (read-only from news.db)."""
        return False

    def has_change_permission(self, request, obj=None):
        """No changing articles (read-only from news.db)."""
        return False
