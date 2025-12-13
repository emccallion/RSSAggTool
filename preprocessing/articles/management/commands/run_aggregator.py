from django.core.management.base import BaseCommand
import subprocess
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Run the news aggregator service to collect new articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run aggregator in dry-run mode (no database writes)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Run aggregator in verbose mode',
        )

    def handle(self, *args, **options):
        self.stdout.write('Running news aggregator service...')

        # Get path to aggregator script
        base_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
        aggregator_script = base_dir / 'src' / 'main.py'
        venv_python = base_dir / 'venv' / 'bin' / 'python'

        if not aggregator_script.exists():
            self.stdout.write(
                self.style.ERROR(f'Aggregator script not found at {aggregator_script}')
            )
            return

        # Build command
        cmd = [str(venv_python), str(aggregator_script)]

        if options['dry_run']:
            cmd.append('--dry-run')
        if options['verbose']:
            cmd.append('--verbose')

        self.stdout.write(f'Executing: {" ".join(cmd)}')

        try:
            # Run the aggregator
            result = subprocess.run(
                cmd,
                cwd=str(base_dir),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # Display output
            if result.stdout:
                self.stdout.write('\n--- Aggregator Output ---')
                self.stdout.write(result.stdout)

            if result.stderr:
                self.stdout.write('\n--- Aggregator Errors ---')
                self.stdout.write(self.style.WARNING(result.stderr))

            if result.returncode == 0:
                self.stdout.write(
                    self.style.SUCCESS('\nAggregator completed successfully!')
                )
                if not options['dry_run']:
                    self.stdout.write(
                        self.style.SUCCESS(
                            'Run "python manage.py sync_from_aggregator" to import new articles'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'\nAggregator failed with exit code {result.returncode}'
                    )
                )

        except subprocess.TimeoutExpired:
            self.stdout.write(
                self.style.ERROR('Aggregator timed out after 5 minutes')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running aggregator: {str(e)}')
            )
            raise
