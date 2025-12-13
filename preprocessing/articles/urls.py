from django.urls import path
from . import views

urlpatterns = [
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('article/<int:pk>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('sync/', views.SyncView.as_view(), name='sync_status'),
    path('ajax/quick-edit/<int:pk>/', views.ajax_quick_edit, name='ajax_quick_edit'),
]
