from django.db import models


class Feed(models.Model):
    """RSS Feed source for news aggregation."""

    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('business', 'Business'),
        ('economics', 'Economics'),
        ('politics', 'Politics'),
        ('world', 'World'),
        ('markets', 'Markets'),
        ('climate', 'Climate'),
        ('geopolitics', 'Geopolitics'),
        ('technology', 'Technology'),
        ('other', 'Other'),
    ]

    source_name = models.CharField(
        max_length=200,
        help_text='Name of the news source (e.g., Financial Times)'
    )
    url = models.URLField(
        max_length=500,
        unique=True,
        help_text='RSS feed URL'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='general',
        help_text='Content category for this feed'
    )
    active = models.BooleanField(
        default=True,
        help_text='Whether to fetch articles from this feed'
    )
    description = models.TextField(
        blank=True,
        help_text='Optional description of this feed'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['source_name', 'category']
        verbose_name = 'RSS Feed'
        verbose_name_plural = 'RSS Feeds'

    def __str__(self):
        status = '✓' if self.active else '✗'
        return f"{status} {self.source_name} - {self.category}"
