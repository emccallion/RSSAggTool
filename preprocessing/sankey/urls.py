from django.urls import path
from . import views

urlpatterns = [
    path('', views.DiagramListView.as_view(), name='sankey_list'),
    path('build/', views.DiagramBuilderView.as_view(), name='sankey_builder'),
    path('build/<int:pk>/', views.DiagramBuilderView.as_view(), name='sankey_builder_edit'),
    path('view/<int:pk>/', views.DiagramViewView.as_view(), name='sankey_view'),
    path('delete/<int:pk>/', views.diagram_delete, name='sankey_delete'),
    path('ajax/save/', views.diagram_save_ajax, name='sankey_save_ajax'),
]
