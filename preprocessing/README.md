# News Preprocessing Microservice

A Django-based preprocessing service for reviewing and categorizing news articles before they move to production. This microservice connects to the news aggregator database and provides an elegant web interface for article management.

## Features

- **Dual Database Architecture**: Connects to both the news aggregator database (read-only) and a separate preprocessing database
- **Web-Based UI**: Clean, Bootstrap-based interface for reviewing articles
- **Article Management**:
  - View, filter, and search articles
  - Mark articles as NEW, processed, or rejected
  - Assign articles to story groups
  - Track who added/modified each article
- **Sync Functionality**:
  - Pull articles from the news aggregator database
  - Run the aggregator service directly from the UI
  - Automatic duplicate detection based on (title, source, published date)
- **Admin Interface**: Full Django admin for advanced management

## Quick Start

### 1. Installation

The service is already installed and configured. Dependencies are in the parent project's virtual environment.

### 2. Database Migration

```bash
# Migrations already run, but if you need to rerun:
cd preprocessing
source ../venv/bin/activate
python manage.py migrate
```

### 3. Create Admin User

```bash
# Create a superuser for the admin interface
python manage.py createsuperuser
```

### 4. Run the Server

```bash
cd preprocessing
source ../venv/bin/activate
python manage.py runserver 8001
```

Access the service at: http://localhost:8001/

### 5. Sync Articles

Visit http://localhost:8001/sync/ to:
- Run the news aggregator to collect new articles
- Sync articles from news.db to preprocessing.db

Or use the command line:

```bash
# Sync articles from news aggregator database
python manage.py sync_from_aggregator

# Run the news aggregator service
python manage.py run_aggregator
```

## Database Structure

### Preprocessing Database (`data/preprocessing.db`)

**PreprocessingArticle** table includes:
- All original article fields (title, link, description, source, etc.)
- `time_added` - Auto-populated timestamp
- `added_by` - User who added the article (default: 'SYSTEM')
- `modified_by` - User who last modified the article
- `outcome` - Status: NEW (default), processed, or rejected
- `storygroup` - Free-text field for grouping related stories
- `source_article_id` - Reference to original article in news.db

### News Aggregator Database (`../data/news.db`)

Read-only access to the original news aggregator articles table.

## Workflow

1. **Collect News**: Use the Sync page to run the aggregator, which fetches new articles from RSS feeds into `news.db`

2. **Import to Preprocessing**: Click "Sync Articles" to import new articles from `news.db` to `preprocessing.db`
   - Only new articles (not already in preprocessing) are imported
   - Articles are matched on (title, source, published date)
   - All imported articles start with outcome='NEW' and added_by='SYSTEM'

3. **Review & Categorize**: Use the Articles page to:
   - Filter articles by status, source, storygroup
   - Review article details
   - Change outcome status (NEW → processed/rejected)
   - Assign articles to story groups
   - Track who made changes

4. **Bulk Actions**: Select multiple articles and apply actions:
   - Mark as processed/rejected/new
   - Assign to a story group
   - Track modifier name

## URL Structure

- `/` - Article list with filtering and search
- `/article/<id>/` - Article detail and edit page
- `/sync/` - Sync status and controls
- `/admin/` - Django admin interface

## Management Commands

```bash
# Sync articles from news aggregator
python manage.py sync_from_aggregator

# Run the news aggregator service
python manage.py run_aggregator [--dry-run] [--verbose]
```

## Configuration

Settings are in `preprocessing_project/settings.py`:

- `DATABASES`: Configured for dual database access
- `DATABASE_ROUTERS`: Routes queries to the correct database
- `INSTALLED_APPS`: Includes the articles app
- `STATIC_URL`: Configured for Bootstrap and custom CSS

## File Structure

```
preprocessing/
├── manage.py
├── preprocessing_project/      # Django project settings
│   ├── settings.py             # Database config, installed apps
│   └── urls.py                 # Root URL configuration
├── articles/                   # Main Django app
│   ├── models.py               # PreprocessingArticle and NewsArticle
│   ├── views.py                # List, detail, and sync views
│   ├── forms.py                # Filter and edit forms
│   ├── urls.py                 # App URL patterns
│   ├── admin.py                # Admin configuration
│   ├── routers.py              # Database router
│   ├── templates/              # HTML templates
│   └── management/commands/    # Custom management commands
├── static/css/                 # Custom CSS styling
└── data/
    └── preprocessing.db        # SQLite database
```

## Technical Details

- **Framework**: Django 6.0
- **Database**: SQLite (dual database setup)
- **Frontend**: Bootstrap 5.1.3 with custom CSS
- **Matching Logic**: Articles matched on (title, source, published) tuple
- **Deduplication**: Unique constraint on (title, source, published)

## Current Status

- ✅ Database: 305 articles synced from news aggregator
- ✅ Models: PreprocessingArticle and NewsArticle
- ✅ Views: List, Detail, and Sync views
- ✅ Templates: Responsive Bootstrap templates
- ✅ Admin: Full Django admin interface
- ✅ Management Commands: Sync and run aggregator

## Future Enhancements

- Export filtered articles to CSV/JSON
- Advanced filtering (date ranges, multiple sources)
- Article preview in list view
- Keyboard shortcuts for quick actions
- Real-time sync status updates
- Email notifications for new articles
