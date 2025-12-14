from django.urls import path
from . import views

urlpatterns = [
    path('', views.FeedListView.as_view(), name='feed_list'),
    path('add/', views.FeedCreateView.as_view(), name='feed_add'),
    path('<int:pk>/edit/', views.FeedUpdateView.as_view(), name='feed_edit'),
    path('<int:pk>/toggle/', views.toggle_feed_status, name='feed_toggle'),
    path('ajax/toggle/<int:pk>/', views.ajax_toggle_feed, name='ajax_feed_toggle'),
]
