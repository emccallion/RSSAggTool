from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import yaml

from feeds.models import Feed


class Command(BaseCommand):
    help = 'Load default RSS feeds from feeds.yaml into the database'

    def handle(self, *args, **options):
        # Path to feeds.yaml (in parent directory's config folder)
        config_path = Path(settings.BASE_DIR).parent / 'config' / 'feeds.yaml'

        if not config_path.exists():
            self.stdout.write(self.style.ERROR(f'feeds.yaml not found at {config_path}'))
            return

        self.stdout.write(f'Loading feeds from {config_path}...')

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        feeds_loaded = 0
        feeds_skipped = 0

        for source_key, source_data in config.get('sources', {}).items():
            source_name = source_data.get('name', source_key)

            for feed_data in source_data.get('feeds', []):
                url = feed_data['url']
                category = feed_data.get('category', 'general')

                # Check if feed already exists
                if Feed.objects.filter(url=url).exists():
                    self.stdout.write(
                        self.style.WARNING(f'  ⊘ Skipped (exists): {source_name} - {category}')
                    )
                    feeds_skipped += 1
                    continue

                # Create new feed
                Feed.objects.create(
                    source_name=source_name,
                    url=url,
                    category=category,
                    active=True,
                    description=f'{category.capitalize()} feed from {source_name}'
                )

                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Loaded: {source_name} - {category}')
                )
                feeds_loaded += 1

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✓ Successfully loaded {feeds_loaded} feed(s)'))
        if feeds_skipped:
            self.stdout.write(self.style.WARNING(f'⊘ Skipped {feeds_skipped} existing feed(s)'))

        total = Feed.objects.count()
        active = Feed.objects.filter(active=True).count()
        self.stdout.write(f'\nTotal feeds in database: {total} ({active} active)')
