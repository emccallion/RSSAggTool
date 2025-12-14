from django.urls import path
from . import views

urlpatterns = [
    path('', views.DiagramListView.as_view(), name='sankey_list'),
    path('build/', views.DiagramBuilderView.as_view(), name='sankey_builder'),
    path('build/<int:pk>/', views.DiagramBuilderView.as_view(), name='sankey_builder_edit'),
    path('view/<int:pk>/', views.DiagramViewView.as_view(), name='sankey_view'),
    path('delete/<int:pk>/', views.diagram_delete, name='sankey_delete'),

    # AJAX endpoints
    path('ajax/save/', views.diagram_save_ajax, name='sankey_save_ajax'),
    path('ajax/publish/<int:pk>/', views.diagram_publish, name='sankey_publish'),
    path('ajax/nodes/<int:diagram_id>/<str:node_name>/associations/', views.node_associations, name='node_associations'),
    path('ajax/nodes/published/', views.published_nodes_list, name='published_nodes_list'),
    path('ajax/associations/create/', views.create_association, name='create_association'),
    path('ajax/associations/<int:association_id>/delete/', views.delete_association, name='delete_association'),
]
