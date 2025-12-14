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
