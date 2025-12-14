from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json

from .models import SankeyDiagram, PublishedNode, NodeArticleAssociation
from articles.models import PreprocessingArticle


class DiagramListView(ListView):
    """List all Sankey diagrams."""

    model = SankeyDiagram
    template_name = 'sankey/diagram_list.html'
    context_object_name = 'diagrams'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = {
            'total': SankeyDiagram.objects.count(),
        }
        return context


class DiagramBuilderView(View):
    """View for building/editing Sankey diagrams."""

    template_name = 'sankey/diagram_builder.html'

    def get(self, request, pk=None):
        """Display the diagram builder interface."""
        diagram = None
        if pk:
            diagram = get_object_or_404(SankeyDiagram, pk=pk)

        context = {
            'diagram': diagram,
            'is_edit': pk is not None,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk=None):
        """Save or update a diagram."""
        try:
            # Get form data
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            config_text = request.POST.get('config_text', '').strip()
            settings_json_str = request.POST.get('settings_json', '{}')

            # Validate
            if not name:
                messages.error(request, 'Diagram name is required.')
                return redirect('sankey_builder')

            if not config_text:
                messages.error(request, 'Diagram configuration is required.')
                return redirect('sankey_builder')

            # Parse settings JSON
            try:
                settings_json = json.loads(settings_json_str)
            except json.JSONDecodeError:
                settings_json = {}

            # Create or update
            if pk:
                # Update existing
                diagram = get_object_or_404(SankeyDiagram, pk=pk)
                diagram.name = name
                diagram.description = description
                diagram.config_text = config_text
                diagram.settings_json = settings_json
                diagram.save()
                messages.success(request, f'Diagram "{name}" updated successfully!')
            else:
                # Create new
                diagram = SankeyDiagram.objects.create(
                    name=name,
                    description=description,
                    config_text=config_text,
                    settings_json=settings_json,
                    created_by=request.POST.get('created_by', 'user')
                )
                messages.success(request, f'Diagram "{name}" created successfully!')

            return redirect('sankey_builder', pk=diagram.pk)

        except Exception as e:
            messages.error(request, f'Error saving diagram: {str(e)}')
            return redirect('sankey_builder')


class DiagramViewView(View):
    """View a saved diagram in read-only mode."""

    template_name = 'sankey/diagram_view.html'

    def get(self, request, pk):
        diagram = get_object_or_404(SankeyDiagram, pk=pk)
        context = {
            'diagram': diagram,
        }
        return render(request, self.template_name, context)


def diagram_delete(request, pk):
    """Delete a diagram."""
    if request.method == 'POST':
        diagram = get_object_or_404(SankeyDiagram, pk=pk)
        name = diagram.name
        diagram.delete()
        messages.success(request, f'Diagram "{name}" deleted successfully.')
        return redirect('sankey_list')

    return redirect('sankey_list')


@require_http_methods(["POST"])
def diagram_save_ajax(request):
    """AJAX endpoint for saving diagrams."""
    try:
        data = json.loads(request.body)

        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        config_text = data.get('config_text', '').strip()
        settings_json = data.get('settings_json', {})
        diagram_id = data.get('diagram_id')

        if not name or not config_text:
            return JsonResponse({
                'success': False,
                'message': 'Name and configuration are required'
            }, status=400)

        if diagram_id:
            # Update existing
            diagram = get_object_or_404(SankeyDiagram, pk=diagram_id)
            diagram.name = name
            diagram.description = description
            diagram.config_text = config_text
            diagram.settings_json = settings_json
            diagram.save()
            message = 'Diagram updated successfully'
        else:
            # Create new
            diagram = SankeyDiagram.objects.create(
                name=name,
                description=description,
                config_text=config_text,
                settings_json=settings_json,
                created_by=data.get('created_by', 'user')
            )
            message = 'Diagram created successfully'

        return JsonResponse({
            'success': True,
            'message': message,
            'diagram_id': diagram.pk
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["POST"])
def diagram_publish(request, pk):
    """Publish a diagram - creates PublishedNode entries for all nodes."""
    try:
        data = json.loads(request.body)
        diagram = get_object_or_404(SankeyDiagram, pk=pk)

        if diagram.is_published:
            return JsonResponse({
                'success': False,
                'message': 'Diagram is already published'
            }, status=400)

        # Parse nodes from the data
        nodes = data.get('nodes', [])
        if not nodes:
            return JsonResponse({
                'success': False,
                'message': 'No nodes provided'
            }, status=400)

        # Create PublishedNode entries
        created_count = 0
        for node_data in nodes:
            node_name = node_data.get('name')
            if node_name:
                PublishedNode.objects.get_or_create(
                    sankey_diagram=diagram,
                    name=node_name,
                    defaults={
                        'original_config_data': node_data
                    }
                )
                created_count += 1

        # Mark diagram as published
        diagram.is_published = True
        diagram.published_at = timezone.now()
        diagram.save()

        return JsonResponse({
            'success': True,
            'message': f'Diagram published successfully with {created_count} nodes',
            'published_at': diagram.published_at.isoformat()
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def node_associations(request, diagram_id, node_name):
    """Get all article associations for a specific node."""
    try:
        diagram = get_object_or_404(SankeyDiagram, pk=diagram_id)

        if not diagram.is_published:
            return JsonResponse({
                'success': False,
                'message': 'Diagram is not published'
            }, status=400)

        # Get the published node
        try:
            node = PublishedNode.objects.get(
                sankey_diagram=diagram,
                name=node_name
            )
        except PublishedNode.DoesNotExist:
            return JsonResponse({
                'success': True,
                'supporting': [],
                'conflicting': [],
                'supporting_score': 0,
                'conflicting_score': 0
            })

        # Get associations
        associations = NodeArticleAssociation.objects.filter(node=node).select_related('article')

        supporting = []
        conflicting = []
        supporting_score = 0
        conflicting_score = 0

        for assoc in associations:
            assoc_data = {
                'id': assoc.id,
                'article_id': assoc.article.id,
                'article_title': assoc.article.title,
                'article_source': assoc.article.source,
                'score': assoc.score,
                'created_at': assoc.created_at.isoformat(),
                'created_by': assoc.created_by
            }

            if assoc.association_type == 'supporting':
                supporting.append(assoc_data)
                supporting_score += assoc.score
            else:
                conflicting.append(assoc_data)
                conflicting_score += assoc.score

        return JsonResponse({
            'success': True,
            'supporting': supporting,
            'conflicting': conflicting,
            'supporting_score': supporting_score,
            'conflicting_score': conflicting_score,
            'supporting_count': len(supporting),
            'conflicting_count': len(conflicting)
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["GET"])
def published_nodes_list(request):
    """Get list of all published nodes for article association."""
    try:
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

        return JsonResponse({
            'success': True,
            'nodes': nodes_data
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["POST"])
def create_association(request):
    """Create or update an article-node association."""
    try:
        data = json.loads(request.body)

        article_id = data.get('article_id')
        node_id = data.get('node_id')
        association_type = data.get('association_type')
        score = data.get('score', 0)
        created_by = data.get('created_by', 'user')

        if not all([article_id, node_id, association_type]):
            return JsonResponse({
                'success': False,
                'message': 'article_id, node_id, and association_type are required'
            }, status=400)

        if association_type not in ['supporting', 'conflicting']:
            return JsonResponse({
                'success': False,
                'message': 'association_type must be "supporting" or "conflicting"'
            }, status=400)

        article = get_object_or_404(PreprocessingArticle, pk=article_id)
        node = get_object_or_404(PublishedNode, pk=node_id)

        # Create or update association
        association, created = NodeArticleAssociation.objects.update_or_create(
            node=node,
            article=article,
            defaults={
                'association_type': association_type,
                'score': score,
                'created_by': created_by
            }
        )

        return JsonResponse({
            'success': True,
            'message': 'Association created successfully' if created else 'Association updated successfully',
            'association_id': association.id,
            'created': created
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["POST"])
def delete_association(request, association_id):
    """Delete an article-node association."""
    try:
        association = get_object_or_404(NodeArticleAssociation, pk=association_id)
        association.delete()

        return JsonResponse({
            'success': True,
            'message': 'Association deleted successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
