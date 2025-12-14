from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import Feed
from .forms import FeedForm


class FeedListView(ListView):
    """List view for RSS feeds with management options."""

    model = Feed
    template_name = 'feeds/feed_list.html'
    context_object_name = 'feeds'
    paginate_by = 50

    def get_queryset(self):
        queryset = Feed.objects.all()

        # Filter by active status
        active_filter = self.request.GET.get('active')
        if active_filter == 'true':
            queryset = queryset.filter(active=True)
        elif active_filter == 'false':
            queryset = queryset.filter(active=False)

        # Filter by source
        source = self.request.GET.get('source')
        if source:
            queryset = queryset.filter(source_name=source)

        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('source_name', 'category')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Statistics
        context['stats'] = {
            'total': Feed.objects.count(),
            'active': Feed.objects.filter(active=True).count(),
            'inactive': Feed.objects.filter(active=False).count(),
        }

        # Get unique sources and categories for filtering
        context['sources'] = Feed.objects.values_list(
            'source_name', flat=True
        ).distinct().order_by('source_name')

        context['categories'] = Feed.objects.values_list(
            'category', flat=True
        ).distinct().order_by('category')

        return context


class FeedCreateView(CreateView):
    """View for creating a new RSS feed."""

    model = Feed
    form_class = FeedForm
    template_name = 'feeds/feed_form.html'
    success_url = reverse_lazy('feed_list')

    def form_valid(self, form):
        messages.success(self.request, 'RSS feed added successfully!')
        return super().form_valid(form)


class FeedUpdateView(UpdateView):
    """View for updating an existing RSS feed."""

    model = Feed
    form_class = FeedForm
    template_name = 'feeds/feed_form.html'
    success_url = reverse_lazy('feed_list')

    def form_valid(self, form):
        messages.success(self.request, 'RSS feed updated successfully!')
        return super().form_valid(form)


def toggle_feed_status(request, pk):
    """Toggle the active status of a feed."""
    feed = get_object_or_404(Feed, pk=pk)
    feed.active = not feed.active
    feed.save()

    status = 'activated' if feed.active else 'deactivated'
    messages.success(request, f'Feed {status}: {feed.source_name} - {feed.category}')

    return redirect('feed_list')


def ajax_toggle_feed(request, pk):
    """AJAX endpoint to toggle feed active status."""
    if request.method == 'POST':
        feed = get_object_or_404(Feed, pk=pk)
        feed.active = not feed.active
        feed.save()

        return JsonResponse({
            'success': True,
            'active': feed.active,
            'message': f'Feed {"activated" if feed.active else "deactivated"}'
        })

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
