# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A news aggregation system that collects RSS feeds from financial and geopolitical sources, classifies articles using NLP, and stores them in a SQLite database for analysis. The system is designed as a foundation for building economic modeling and analysis tools.

## Common Commands

### Development Setup
```bash
# Activate virtual environment (required for all commands)
source venv/bin/activate

# Install dependencies
python setup.py
# OR manually:
pip install -r requirements.txt
```

### Running the Aggregator
```bash
# Fetch and store articles from all configured feeds
python src/main.py

# Test feed parsing without saving to database
python src/main.py --dry-run

# Fetch from a specific source only
python src/main.py --source "Financial Times"

# Enable verbose logging
python src/main.py --verbose
```

### Querying the Database
```bash
# Show database statistics
python src/query.py --stats

# Show recent articles (default: last 24 hours, limit 10)
python src/query.py

# Interactive browser mode with pagination and filtering
python src/query.py --browse

# Search articles by keywords
python src/query.py --search "inflation economy"

# Filter by source or category
python src/query.py --source "Bloomberg" --limit 20
python src/query.py --category "economics" --hours 48

# Pagination
python src/query.py --page 2 --limit 10
```

## Architecture

### Core Components

**src/main.py** - Orchestration script that:
1. Initializes FeedParser, NewsDatabase, and NewsClassifier
2. Fetches articles from configured RSS feeds
3. Runs NLP classification on each article
4. Bulk inserts articles with classifications into database
5. Provides dry-run mode for testing

**src/feed_parser.py** - RSS parsing:
- Loads feed configuration from `config/feeds.yaml`
- Uses feedparser library to parse RSS/Atom feeds
- Extracts title, link, description, author, tags, published date
- Includes 1-second delay between feeds for rate limiting
- Handles HTTP errors gracefully

**src/classifier.py** - NLP classification:
- Keyword-based topic classification (Economics, Politics, Finance, etc.)
- Geographic entity extraction (countries and regions)
- Sentiment analysis using TextBlob (positive/negative/neutral)
- Returns confidence scores for topics and geographies
- Generates additional tags (economic indicators, market conditions, urgency)

**src/database.py** - Data persistence:
- SQLite database with normalized schema
- Core tables: articles, tags, topics, geographies
- Junction tables for many-to-many relationships (article_tags, article_topics, article_geographies)
- Indexes on source, published date, category for query performance
- Bulk insert operations with duplicate detection via UNIQUE constraints
- Pre-populated with default topics and geographies

**src/query.py** - Query interface:
- Command-line tool for browsing and searching articles
- Interactive browser mode with pagination
- Filtering by source, category, time period
- Keyword search across title and description
- Statistics and source listing

**config/feeds.yaml** - Feed configuration:
- Structured by news source (Financial Times, WSJ, NYT, Bloomberg, etc.)
- Each feed has URL and category mapping
- Currently 4 working sources; 3 have feed URL issues (Economist, AFR, Foreign Affairs)

### Database Schema

The database uses a normalized structure to support flexible querying and analysis:

- **articles** - Core article data (title, link, description, source, published date, etc.)
- **tags** - Generic tagging system with type field (general, geography, topic, entity)
- **topics** - Hierarchical topic taxonomy with parent-child relationships
- **geographies** - Geographic entities with country codes, regions, continents
- **article_tags**, **article_topics**, **article_geographies** - Junction tables with confidence scores

All classification relationships include confidence scores (0-1.0) to support probabilistic analysis.

### Data Flow

1. **Ingestion**: main.py → FeedParser reads config/feeds.yaml → parses RSS feeds → returns article dictionaries
2. **Classification**: NewsClassifier analyzes article text → extracts topics, geographies, sentiment → adds classification dict to article
3. **Storage**: NewsDatabase.bulk_insert_articles() → inserts articles → creates tag/topic/geography relationships
4. **Retrieval**: query.py → NewsDatabase methods → SQL queries with filters → formatted output

### Classification System

The NewsClassifier uses keyword matching with confidence scoring:

- **Topic keywords**: 10 categories (Economics, Central Banking, Politics, Geopolitics, Business, Finance, Technology, Energy, Climate, Trade)
- **Geography keywords**: 12+ countries/regions (US, UK, EU, China, Japan, etc.)
- **Sentiment analysis**: TextBlob polarity (-1 to 1) and subjectivity (0 to 1)
- **Confidence scoring**: Based on keyword matches normalized by text length

Confidence scores enable filtering low-quality matches and building probabilistic models.

### Extending the System

**Adding new RSS feeds**: Edit `config/feeds.yaml` following the existing structure.

**Adding classification categories**: Edit keyword mappings in `src/classifier.py`:
- `topic_keywords` for new topics
- `geography_keywords` for new regions
- `market_keywords` for market-specific terms

**Database queries**: The NewsDatabase class provides methods for:
- `get_articles()` - with filtering by source, category, date
- `search_articles()` - keyword search
- `get_article_count()` - statistics
- Add new query methods as needed for custom analysis

**Future enhancements** (per USAGE.md):
- Bayesian economic modeling using article classifications
- Card generation from related articles
- Sankey diagrams for scenario probabilities
- LLM-based content analysis
- Real-time feed monitoring
- Web dashboard interface
