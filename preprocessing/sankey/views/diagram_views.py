"""
Regular views for Sankey diagram pages.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from django.contrib import messages
from django.core.exceptions import ValidationError
import json

from ..models import SankeyDiagram
from ..services import DiagramService


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

            # Parse settings JSON
            try:
                settings_json = json.loads(settings_json_str)
            except json.JSONDecodeError:
                settings_json = {}

            # Create or update using service
            if pk:
                # Update existing
                diagram = get_object_or_404(SankeyDiagram, pk=pk)
                diagram = DiagramService.update(
                    diagram,
                    name=name,
                    description=description,
                    config_text=config_text,
                    settings_json=settings_json
                )
                messages.success(request, f'Diagram "{name}" updated successfully!')
            else:
                # Create new
                diagram = DiagramService.create(
                    name=name,
                    description=description,
                    config_text=config_text,
                    settings_json=settings_json,
                    created_by=request.POST.get('created_by', 'user')
                )
                messages.success(request, f'Diagram "{name}" created successfully!')

            return redirect('sankey_builder_edit', pk=diagram.pk)

        except ValidationError as e:
            messages.error(request, str(e))
            if pk:
                return redirect('sankey_builder_edit', pk=pk)
            return redirect('sankey_builder')
        except Exception as e:
            messages.error(request, f'Error saving diagram: {str(e)}')
            if pk:
                return redirect('sankey_builder_edit', pk=pk)
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
        DiagramService.delete(diagram)
        messages.success(request, f'Diagram "{name}" deleted successfully.')
        return redirect('sankey_list')

    return redirect('sankey_list')
