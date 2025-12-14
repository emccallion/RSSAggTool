from django.db import models
from django.utils import timezone


class SankeyDiagram(models.Model):
    """Model for storing Sankey diagram configurations."""

    name = models.CharField(
        max_length=200,
        help_text='Name/title for this diagram'
    )
    description = models.TextField(
        blank=True,
        help_text='Optional description of what this diagram shows'
    )

    # Diagram configuration (the input text that defines the flows)
    config_text = models.TextField(
        help_text='Sankey diagram configuration in SankeyMatic format'
    )

    # Settings (stored as JSON or individual fields)
    # For now, we'll store the full configuration including settings
    settings_json = models.JSONField(
        default=dict,
        blank=True,
        help_text='Diagram appearance settings (colors, sizes, etc.)'
    )

    # Publishing status
    is_published = models.BooleanField(
        default=False,
        help_text='When published, nodes become database entries linkable to articles'
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when diagram was published'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(
        max_length=100,
        default='user',
        help_text='Username or identifier of creator'
    )

    # Optional: Save the rendered SVG for quick display
    rendered_svg = models.TextField(
        blank=True,
        help_text='Cached SVG output'
    )

    class Meta:
        ordering = ['-updated_at']
        verbose_name = 'Sankey Diagram'
        verbose_name_plural = 'Sankey Diagrams'

    def __str__(self):
        return f"{self.name} ({self.created_at.strftime('%Y-%m-%d')})"

    def get_preview_text(self):
        """Return first 100 chars of config for preview."""
        return self.config_text[:100] + ('...' if len(self.config_text) > 100 else '')


class PublishedNode(models.Model):
    """Represents a node from a published Sankey diagram."""

    name = models.CharField(
        max_length=500,
        help_text='Node name/label'
    )
    sankey_diagram = models.ForeignKey(
        SankeyDiagram,
        on_delete=models.CASCADE,
        related_name='published_nodes',
        help_text='The diagram this node belongs to'
    )

    # Store original config data for reference
    original_config_data = models.JSONField(
        default=dict,
        blank=True,
        help_text='Original node configuration (position, color, etc.)'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [['sankey_diagram', 'name']]
        verbose_name = 'Published Node'
        verbose_name_plural = 'Published Nodes'

    def __str__(self):
        return f"{self.name} ({self.sankey_diagram.name})"

    def get_supporting_count(self):
        """Count of supporting article associations."""
        return self.article_associations.filter(association_type='supporting').count()

    def get_conflicting_count(self):
        """Count of conflicting article associations."""
        return self.article_associations.filter(association_type='conflicting').count()

    def get_total_score(self):
        """Sum of all association scores."""
        from django.db.models import Sum
        result = self.article_associations.aggregate(total=Sum('score'))
        return result['total'] or 0


class NodeArticleAssociation(models.Model):
    """Links published nodes to news articles as supporting or conflicting sources."""

    ASSOCIATION_TYPES = [
        ('supporting', 'Supporting'),
        ('conflicting', 'Conflicting'),
    ]

    node = models.ForeignKey(
        PublishedNode,
        on_delete=models.CASCADE,
        related_name='article_associations',
        help_text='The published node'
    )
    article = models.ForeignKey(
        'articles.PreprocessingArticle',
        on_delete=models.CASCADE,
        related_name='node_associations',
        help_text='The news article'
    )
    association_type = models.CharField(
        max_length=20,
        choices=ASSOCIATION_TYPES,
        help_text='Whether this article supports or conflicts with the node'
    )
    score = models.IntegerField(
        default=0,
        help_text='Strength/confidence score for this association'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(
        max_length=100,
        default='user',
        help_text='Username of person who created this association'
    )

    class Meta:
        ordering = ['-created_at']
        unique_together = [['node', 'article']]
        verbose_name = 'Node-Article Association'
        verbose_name_plural = 'Node-Article Associations'
        indexes = [
            models.Index(fields=['association_type']),
            models.Index(fields=['score']),
        ]

    def __str__(self):
        return f"{self.article.title[:50]} {self.association_type} {self.node.name}"
