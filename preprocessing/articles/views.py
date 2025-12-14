from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.core.management import call_command
from django.http import JsonResponse
from io import StringIO
import sys

from .models import PreprocessingArticle
from .forms import ArticleFilterForm, ArticleEditForm, BulkActionForm


class ArticleListView(ListView):
    """List view for preprocessing articles with filtering and sorting."""

    model = PreprocessingArticle
    template_name = 'articles/article_list.html'
    context_object_name = 'articles'
    paginate_by = 20

    def get_queryset(self):
        queryset = PreprocessingArticle.objects.all()

        # Apply filters from query parameters
        outcome = self.request.GET.get('outcome')
        source = self.request.GET.get('source')
        storygroup = self.request.GET.get('storygroup')
        search = self.request.GET.get('search')
        added_by = self.request.GET.get('added_by')

        if outcome:
            queryset = queryset.filter(outcome=outcome)
        if source:
            queryset = queryset.filter(source__icontains=source)
        if storygroup:
            queryset = queryset.filter(storygroup__icontains=storygroup)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        if added_by:
            queryset = queryset.filter(added_by__icontains=added_by)

        # Sorting
        sort_by = self.request.GET.get('sort', '-time_added')
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = ArticleFilterForm(self.request.GET or None)
        context['bulk_form'] = BulkActionForm()

        # Add statistics
        context['stats'] = {
            'total': PreprocessingArticle.objects.count(),
            'new': PreprocessingArticle.objects.filter(outcome='NEW').count(),
            'processed': PreprocessingArticle.objects.filter(outcome='processed').count(),
            'rejected': PreprocessingArticle.objects.filter(outcome='rejected').count(),
        }

        # Get unique sources and storygroups for filtering
        context['sources'] = PreprocessingArticle.objects.values_list(
            'source', flat=True
        ).distinct().order_by('source')

        context['storygroups'] = PreprocessingArticle.objects.exclude(
            storygroup=''
        ).values_list('storygroup', flat=True).distinct().order_by('storygroup')

        return context

    def post(self, request, *args, **kwargs):
        """Handle bulk actions."""
        action = request.POST.get('action')
        article_ids = request.POST.getlist('selected_articles')
        modified_by = request.POST.get('modified_by', '')
        storygroup = request.POST.get('storygroup', '')

        if not article_ids:
            messages.warning(request, 'No articles selected.')
            return redirect('article_list')

        articles = PreprocessingArticle.objects.filter(id__in=article_ids)

        if action == 'mark_processed':
            articles.update(outcome='processed', modified_by=modified_by)
            messages.success(request, f'{len(article_ids)} articles marked as processed.')
        elif action == 'mark_rejected':
            articles.update(outcome='rejected', modified_by=modified_by)
            messages.success(request, f'{len(article_ids)} articles marked as rejected.')
        elif action == 'mark_new':
            articles.update(outcome='NEW', modified_by=modified_by)
            messages.success(request, f'{len(article_ids)} articles marked as new.')

        if storygroup:
            articles.update(storygroup=storygroup)
            messages.success(request, f'Story group updated for {len(article_ids)} articles.')

        return redirect('article_list')


class ArticleDetailView(DetailView):
    """Detail view for a single preprocessing article."""

    model = PreprocessingArticle
    template_name = 'articles/article_detail.html'
    context_object_name = 'article'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit_form'] = ArticleEditForm(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        """Handle article edits."""
        article = self.get_object()
        form = ArticleEditForm(request.POST, instance=article)

        if form.is_valid():
            form.save()
            messages.success(request, 'Article updated successfully.')
            return redirect('article_detail', pk=article.pk)
        else:
            messages.error(request, 'Error updating article.')
            context = self.get_context_data()
            context['edit_form'] = form
            return render(request, self.template_name, context)


class SyncView(View):
    """View for fetching articles from RSS feeds."""

    template_name = 'articles/sync_status.html'

    def get(self, request):
        """Display aggregator status and controls."""
        preprocessing_count = PreprocessingArticle.objects.count()
        new_count = PreprocessingArticle.objects.filter(outcome='NEW').count()
        processed_count = PreprocessingArticle.objects.filter(outcome='processed').count()

        context = {
            'total_articles': preprocessing_count,
            'new_articles': new_count,
            'processed_articles': processed_count,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """Handle fetch articles action."""
        action = request.POST.get('action')

        if action == 'fetch_articles':
            return self.fetch_articles(request)

        messages.error(request, 'Unknown action.')
        return redirect('sync_status')

    def fetch_articles(self, request):
        """Fetch new articles from RSS feeds."""
        try:
            output = StringIO()
            call_command('fetch_articles', stdout=output)

            output_str = output.getvalue()

            # Extract summary from output
            if 'New articles:' in output_str:
                for line in output_str.split('\n'):
                    if 'New articles:' in line or 'Total in database:' in line:
                        messages.info(request, line.strip())

            messages.success(request, 'Articles fetched successfully!')

        except Exception as e:
            messages.error(request, f'Error fetching articles: {str(e)}')

        return redirect('sync_status')


def ajax_quick_edit(request, pk):
    """AJAX endpoint for quick editing of article fields."""
    if request.method == 'POST':
        article = get_object_or_404(PreprocessingArticle, pk=pk)
        field = request.POST.get('field')
        value = request.POST.get('value')

        if field in ['outcome', 'storygroup', 'modified_by']:
            setattr(article, field, value)
            article.save()
            return JsonResponse({'success': True, 'message': 'Updated successfully'})

        return JsonResponse({'success': False, 'message': 'Invalid field'})

    return JsonResponse({'success': False, 'message': 'Invalid request method'})
