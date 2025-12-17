"""
Business logic for Sankey diagram operations.
"""
from django.core.exceptions import ValidationError
from django.utils import timezone
from common.services.base import BaseCRUDService
from .models import SankeyDiagram, PublishedNode, NodeArticleAssociation


class DiagramService(BaseCRUDService):
    """Service for Sankey diagram operations."""

    model = SankeyDiagram

    @classmethod
    def validate_create(cls, data):
        """Validate diagram creation data."""
        if not data.get('name'):
            raise ValidationError("Diagram name is required")

        if not data.get('config_text'):
            raise ValidationError("Diagram configuration is required")

    @classmethod
    def validate_update(cls, instance, data):
        """Validate diagram update data."""
        if 'name' in data and not data['name']:
            raise ValidationError("Diagram name cannot be empty")

        if 'config_text' in data and not data['config_text']:
            raise ValidationError("Diagram configuration cannot be empty")

    @classmethod
    def publish_diagram(cls, diagram, nodes_data):
        """
        Publish a diagram by creating PublishedNode entries for all nodes.

        Args:
            diagram: SankeyDiagram instance
            nodes_data: List of dicts with node information [{'name': '...', 'color': '...'}, ...]

        Returns:
            tuple: (diagram, created_nodes_count)

        Raises:
            ValidationError: If diagram is already published or no nodes provided
        """
        if diagram.is_published:
            raise ValidationError("Diagram is already published")

        if not nodes_data:
            raise ValidationError("No nodes provided")

        # Create PublishedNode entries
        created_count = 0
        for node_data in nodes_data:
            node_name = node_data.get('name')
            if node_name:
                _, created = PublishedNode.objects.get_or_create(
                    sankey_diagram=diagram,
                    name=node_name,
                    defaults={
                        'original_config_data': node_data
                    }
                )
                if created:
                    created_count += 1

        # Mark diagram as published
        diagram.is_published = True
        diagram.published_at = timezone.now()
        diagram.save()

        return diagram, created_count

    @classmethod
    def get_diagram_statistics(cls, diagram):
        """Get statistics for a diagram."""
        stats = {
            'published': diagram.is_published,
            'published_at': diagram.published_at,
        }

        if diagram.is_published:
            stats['total_nodes'] = diagram.published_nodes.count()
            stats['total_associations'] = NodeArticleAssociation.objects.filter(
                node__sankey_diagram=diagram
            ).count()

        return stats


class NodeService(BaseCRUDService):
    """Service for published node operations."""

    model = PublishedNode

    @classmethod
    def get_node_statistics(cls, node):
        """Get detailed statistics for a node."""
        from django.db.models import Sum

        supporting = node.article_associations.filter(association_type='supporting')
        conflicting = node.article_associations.filter(association_type='conflicting')

        supporting_score = supporting.aggregate(total=Sum('score'))['total'] or 0
        conflicting_score = conflicting.aggregate(total=Sum('score'))['total'] or 0

        return {
            'supporting_count': supporting.count(),
            'conflicting_count': conflicting.count(),
            'supporting_score': supporting_score,
            'conflicting_score': conflicting_score,
            'total_score': supporting_score - conflicting_score,
            'total_associations': node.article_associations.count()
        }

    @classmethod
    def get_node_associations(cls, node):
        """Get all associations for a node, grouped by type."""
        associations = node.article_associations.select_related('article').all()

        supporting = []
        conflicting = []

        for assoc in associations:
            assoc_data = {
                'id': assoc.id,
                'article_id': assoc.article.id,
                'article_title': assoc.article.title,
                'article_source': assoc.article.source,
                'score': assoc.score,
                'created_at': assoc.created_at,
                'created_by': assoc.created_by
            }

            if assoc.association_type == 'supporting':
                supporting.append(assoc_data)
            else:
                conflicting.append(assoc_data)

        return {
            'supporting': supporting,
            'conflicting': conflicting
        }


class AssociationService(BaseCRUDService):
    """Service for node-article association operations."""

    model = NodeArticleAssociation

    @classmethod
    def validate_create(cls, data):
        """Validate association creation data."""
        if not data.get('node'):
            raise ValidationError("Node is required")

        if not data.get('article'):
            raise ValidationError("Article is required")

        if not data.get('association_type'):
            raise ValidationError("Association type is required")

        if data.get('association_type') not in ['supporting', 'conflicting']:
            raise ValidationError("Association type must be 'supporting' or 'conflicting'")

    @classmethod
    def create_or_update_association(cls, node, article, association_type, score=0, created_by='user'):
        """
        Create or update an association between a node and article.

        Args:
            node: PublishedNode instance
            article: PreprocessingArticle instance
            association_type: 'supporting' or 'conflicting'
            score: Confidence score (0-100)
            created_by: Username

        Returns:
            tuple: (association, created)
        """
        if association_type not in ['supporting', 'conflicting']:
            raise ValidationError("Association type must be 'supporting' or 'conflicting'")

        association, created = NodeArticleAssociation.objects.update_or_create(
            node=node,
            article=article,
            defaults={
                'association_type': association_type,
                'score': score,
                'created_by': created_by
            }
        )

        return association, created

    @classmethod
    def get_article_associations(cls, article):
        """Get all node associations for an article."""
        return article.node_associations.select_related('node__sankey_diagram').all()
