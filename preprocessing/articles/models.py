from django.db import models
from django.utils import timezone


class PreprocessingArticle(models.Model):
    """
    Preprocessing database model for article review and categorization.
    """
    OUTCOME_CHOICES = [
        ('NEW', 'New'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected'),
    ]

    # Original article fields
    title = models.TextField()
    link = models.TextField()
    description = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    source = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True)
    feed_url = models.TextField(blank=True)
    guid = models.TextField(blank=True)
    author = models.CharField(max_length=500, blank=True)
    published = models.DateTimeField(null=True, blank=True)
    fetched_at = models.DateTimeField(null=True, blank=True)

    # Preprocessing-specific fields
    time_added = models.DateTimeField(auto_now_add=True)
    added_by = models.CharField(max_length=100, default='SYSTEM')
    modified_by = models.CharField(max_length=100, blank=True)
    outcome = models.CharField(
        max_length=20,
        choices=OUTCOME_CHOICES,
        default='NEW'
    )
    storygroup = models.CharField(max_length=200, blank=True)
    source_article_id = models.IntegerField(null=True, blank=True, help_text='ID from news.db')
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-time_added']
        unique_together = [['title', 'source', 'published']]
        indexes = [
            models.Index(fields=['outcome']),
            models.Index(fields=['source']),
            models.Index(fields=['storygroup']),
            models.Index(fields=['time_added']),
        ]

    def __str__(self):
        return f"{self.source}: {self.title[:50]}"

    @property
    def outcome_badge_class(self):
        """Return CSS class for outcome badge."""
        badges = {
            'NEW': 'badge-primary',
            'processed': 'badge-success',
            'rejected': 'badge-danger',
        }
        return badges.get(self.outcome, 'badge-secondary')
