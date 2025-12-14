"""
Management command to fetch articles from RSS feeds.
Integrated Django version - writes directly to PreprocessingArticle.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from articles.models import PreprocessingArticle
from aggregator.services import FeedParser, NewsClassifier
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch articles from RSS feeds and store in preprocessing database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse feeds but do not save to database',
        )
        parser.add_argument(
            '--source',
            type=str,
            help='Fetch from specific source only',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting RSS feed aggregation...'))

        try:
            # Initialize services
            feed_parser = FeedParser()
            classifier = NewsClassifier()

            # Parse feeds
            self.stdout.write('Parsing RSS feeds...')
            articles = feed_parser.parse_all_feeds()

            if not articles:
                self.stdout.write(self.style.WARNING('No articles found'))
                return

            self.stdout.write(f'Parsed {len(articles)} articles')

            # Classify articles
            self.stdout.write('Classifying articles...')
            classified_count = 0

            for article in articles:
                classification = classifier.classify_article(article)
                article['classification'] = classification
                classified_count += 1

                if classified_count % 50 == 0:
                    self.stdout.write(f'Classified {classified_count}/{len(articles)}')

            if options['dry_run']:
                self.stdout.write(self.style.WARNING('DRY RUN - No articles saved'))
                self.stdout.write(f'\nSample articles:')
                for i, article in enumerate(articles[:3], 1):
                    self.stdout.write(f"{i}. {article.get('title')}")
                    self.stdout.write(f"   Source: {article.get('source')}")
                    self.stdout.write(f"   Topics: {article['classification']['topics']}")
                return

            # Save to database
            self.stdout.write('Saving articles to database...')
            new_count = 0
            duplicate_count = 0

            with transaction.atomic():
                for article in articles:
                    # Check for duplicates
                    exists = PreprocessingArticle.objects.filter(
                        title=article['title'],
                        source=article['source'],
                        published=article['published']
                    ).exists()

                    if exists:
                        duplicate_count += 1
                        continue

                    # Create new article
                    PreprocessingArticle.objects.create(
                        title=article['title'],
                        link=article['link'],
                        description=article.get('description', ''),
                        summary=article.get('summary', ''),
                        source=article['source'],
                        category=article.get('category', ''),
                        feed_url=article.get('feed_url', ''),
                        guid=article.get('guid', ''),
                        author=article.get('author', ''),
                        published=article['published'],
                        fetched_at=article['fetched_at'],
                        added_by='SYSTEM',
                        outcome='NEW',
                    )
                    new_count += 1

            # Summary
            total = PreprocessingArticle.objects.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Aggregation complete!\n'
                    f'  New articles: {new_count}\n'
                    f'  Duplicates skipped: {duplicate_count}\n'
                    f'  Total in database: {total}'
                )
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            raise
