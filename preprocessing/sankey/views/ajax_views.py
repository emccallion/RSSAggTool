"""
AJAX endpoints for Sankey diagram operations.
"""
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import json

from common.utils.decorators import ajax_response
from common.utils.api import APIResponse
from ..models import SankeyDiagram, PublishedNode
from ..services import DiagramService, NodeService, AssociationService


@require_http_methods(["POST"])
@ajax_response
def diagram_save_ajax(request):
    """AJAX endpoint for saving diagrams."""
    data = json.loads(request.body)

    name = data.get('name', '').strip()
    description = data.get('description', '').strip()
    config_text = data.get('config_text', '').strip()
    settings_json = data.get('settings_json', {})
    diagram_id = data.get('diagram_id')

    if diagram_id:
        # Update existing
        diagram = get_object_or_404(SankeyDiagram, pk=diagram_id)
        diagram = DiagramService.update(
            diagram,
            name=name,
            description=description,
            config_text=config_text,
            settings_json=settings_json
        )
        message = 'Diagram updated successfully'
    else:
        # Create new
        diagram = DiagramService.create(
            name=name,
            description=description,
            config_text=config_text,
            settings_json=settings_json,
            created_by=data.get('created_by', 'user')
        )
        message = 'Diagram created successfully'

    return {
        'message': message,
        'diagram_id': diagram.pk
    }


@require_http_methods(["POST"])
@ajax_response
def diagram_publish(request, pk):
    """Publish a diagram - creates PublishedNode entries for all nodes."""
    data = json.loads(request.body)
    diagram = get_object_or_404(SankeyDiagram, pk=pk)

    # Parse nodes from the data
    nodes = data.get('nodes', [])

    # Publish using service
    diagram, created_count = DiagramService.publish_diagram(diagram, nodes)

    return {
        'message': f'Diagram published successfully with {created_count} nodes',
        'published_at': diagram.published_at.isoformat()
    }


@require_http_methods(["GET"])
def node_associations(request, diagram_id, node_name):
    """Get all article associations for a specific node."""
    diagram = get_object_or_404(SankeyDiagram, pk=diagram_id)

    if not diagram.is_published:
        return APIResponse.bad_request("Diagram is not published")

    # Get the published node
    try:
        node = PublishedNode.objects.get(
            sankey_diagram=diagram,
            name=node_name
        )
    except PublishedNode.DoesNotExist:
        return APIResponse.success(data={
            'supporting': [],
            'conflicting': [],
            'supporting_score': 0,
            'conflicting_score': 0
        })

    # Get associations using service
    associations = NodeService.get_node_associations(node)
    stats = NodeService.get_node_statistics(node)

    return APIResponse.success(data={
        **associations,
        'supporting_score': stats['supporting_score'],
        'conflicting_score': stats['conflicting_score'],
        'supporting_count': stats['supporting_count'],
        'conflicting_count': stats['conflicting_count']
    })


@require_http_methods(["GET"])
def published_nodes_list(request):
    """Get list of all published nodes for article association."""
    nodes = PublishedNode.objects.select_related('sankey_diagram').all()

    nodes_data = []
    for node in nodes:
        nodes_data.append({
            'id': node.id,
            'name': node.name,
            'diagram_name': node.sankey_diagram.name,
            'diagram_id': node.sankey_diagram.id,
            'supporting_count': node.get_supporting_count(),
            'conflicting_count': node.get_conflicting_count()
        })

    return APIResponse.success(data={'nodes': nodes_data})


@require_http_methods(["POST"])
@ajax_response
def create_association(request):
    """Create or update an article-node association."""
    data = json.loads(request.body)

    article_id = data.get('article_id')
    node_id = data.get('node_id')
    association_type = data.get('association_type')
    score = data.get('score', 0)
    created_by = data.get('created_by', 'user')

    # Validate inputs
    if not all([article_id, node_id, association_type]):
        raise ValidationError('article_id, node_id, and association_type are required')

    # Get objects
    from articles.models import PreprocessingArticle
    article = get_object_or_404(PreprocessingArticle, pk=article_id)
    node = get_object_or_404(PublishedNode, pk=node_id)

    # Create using service
    association, created = AssociationService.create_or_update_association(
        node=node,
        article=article,
        association_type=association_type,
        score=score,
        created_by=created_by
    )

    return {
        'message': 'Association created successfully' if created else 'Association updated successfully',
        'association_id': association.id,
        'created': created
    }


@require_http_methods(["POST"])
@ajax_response
def delete_association(request, association_id):
    """Delete an article-node association."""
    association = AssociationService.get_by_id(association_id)
    AssociationService.delete(association)

    return {'message': 'Association deleted successfully'}
