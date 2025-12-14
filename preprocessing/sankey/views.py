from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import SankeyDiagram


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
