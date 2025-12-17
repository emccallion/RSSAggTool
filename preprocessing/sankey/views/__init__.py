"""
Sankey diagram views.
"""
# Import from diagram_views
from .diagram_views import (
    DiagramListView,
    DiagramBuilderView,
    DiagramViewView,
    diagram_delete
)

# Import from ajax_views
from .ajax_views import (
    diagram_save_ajax,
    diagram_publish,
    node_associations,
    published_nodes_list,
    create_association,
    delete_association
)

__all__ = [
    # Regular views
    'DiagramListView',
    'DiagramBuilderView',
    'DiagramViewView',
    'diagram_delete',

    # AJAX views
    'diagram_save_ajax',
    'diagram_publish',
    'node_associations',
    'published_nodes_list',
    'create_association',
    'delete_association',
]
