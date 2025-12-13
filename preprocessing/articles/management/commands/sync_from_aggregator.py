from django.core.management.base import BaseCommand
from django.db import transaction
from articles.models import NewsArticle, PreprocessingArticle
from datetime import datetime


class Command(BaseCommand):
    help = 'Sync articles from news aggregator database to preprocessing database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update existing articles',
        )

    def handle(self, *args, **options):
        self.stdout.write('Starting sync from news aggregator...')

        try:
            # Get all articles from news aggregator database
            news_articles = NewsArticle.objects.using('news_aggregator').all()
            total_news = news_articles.count()
            self.stdout.write(f'Found {total_news} articles in news aggregator database')

            # Get existing articles in preprocessing database (as a set of tuples)
            existing_keys = set(
                PreprocessingArticle.objects.values_list('title', 'source', 'published')
            )
            self.stdout.write(f'Found {len(existing_keys)} articles already in preprocessing database')

            # Find new articles
            new_articles = []
            updated_count = 0

            for article in news_articles:
                key = (article.title, article.source, article.published)

                if key not in existing_keys:
                    # Create new preprocessing article
                    new_articles.append(PreprocessingArticle(
                        title=article.title,
                        link=article.link,
                        description=article.description or '',
                        summary=article.summary or '',
                        content=article.content or '',
                        source=article.source,
                        category=article.category or '',
                        feed_url=article.feed_url or '',
                        guid=article.guid or '',
                        author=article.author or '',
                        published=article.published,
                        fetched_at=article.fetched_at,
                        added_by='SYSTEM',
                        outcome='NEW',
                        source_article_id=article.id,
                    ))

            # Bulk create new articles
            if new_articles:
                with transaction.atomic():
                    PreprocessingArticle.objects.bulk_create(
                        new_articles,
                        ignore_conflicts=True
                    )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully added {len(new_articles)} new articles'
                    )
                )
            else:
                self.stdout.write(self.style.WARNING('No new articles to add'))

            # Summary
            total_preprocessing = PreprocessingArticle.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSync complete!\n'
                    f'News aggregator: {total_news} articles\n'
                    f'Preprocessing database: {total_preprocessing} articles\n'
                    f'New articles added: {len(new_articles)}'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error during sync: {str(e)}')
            )
            raise
