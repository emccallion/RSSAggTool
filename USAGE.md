# News Aggregation System - Usage Guide

## Overview

This system successfully aggregates RSS feeds from major financial and news outlets, processes and categorizes articles, and stores them in a SQLite database for analysis. The system is generic and extensible, making it suitable for building more complex analysis tools.

## Current Status

✅ **Working Sources:**
- Financial Times (multiple feeds: home, world, economics, companies, markets, climate)
- New York Times (home, business, politics, world)
- Wall Street Journal (top stories)
- Bloomberg (businessweek, politics, economics)

⚠️ **Sources with Issues:**
- The Economist (403 Forbidden - likely requires authentication)
- Australian Financial Review (404 - feed URL needs updating)
- Foreign Affairs (404 - feed URL needs updating)

## Key Features

1. **RSS Feed Parsing**: Automatically fetches and parses RSS feeds from configured sources
2. **Article Classification**: Uses keyword-based classification to identify:
   - Topics (Economics, Politics, Business, Finance, Technology, etc.)
   - Geographies (US, UK, China, EU, etc.)
   - Sentiment analysis
3. **Database Storage**: SQLite database with normalized schema for articles, tags, topics, and geographies
4. **Browsing & Search**: Multiple ways to explore your data:
   - Interactive browser with pagination and filtering
   - Keyword search across titles and descriptions
   - Page-by-page navigation
   - Filter by source, category, or time period
5. **Command Line Tools**: Easy-to-use CLI for running aggregation and querying data

## Quick Start

1. **Activate virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Run news aggregation:**
   ```bash
   python src/main.py  # Fetch and store articles
   python src/main.py --dry-run  # Test without saving
   ```

3. **Query the database:**
   ```bash
   python src/query.py --stats  # Show statistics
   python src/query.py --limit 10  # Show recent articles
   python src/query.py --source "Financial Times"  # Filter by source
   python src/query.py --browse  # Interactive browser mode
   python src/query.py --search "inflation economy"  # Search articles
   python src/query.py --page 2  # View page 2 of results
   ```

## Browsing Your Data

### Interactive Browser Mode
```bash
python src/query.py --browse
```

The interactive browser provides a full-screen interface with:
- **Navigation**: Use `n`/`p` for next/previous page, `g` to jump to page
- **Filtering**: Press `s` to filter by source, `c` for category
- **Details**: Press `f` to toggle full article descriptions
- **Search**: Built-in filtering and navigation
- **Help**: Press `h` for help, `q` to quit

### Command Line Browsing
```bash
# Pagination through all articles
python src/query.py --page 1 --limit 10
python src/query.py --page 2 --limit 10

# Search by keywords
python src/query.py --search "inflation economy"
python src/query.py --search "federal reserve" --page 2

# Filter by source and category  
python src/query.py --source "Bloomberg" --limit 20
python src/query.py --category "economics" --hours 48

# Combine filters
python src/query.py --source "Financial Times" --search "climate" --full
```

## Current Database

- **Total Articles**: 305+ articles
- **Active Sources**: 4 (Financial Times, NYT, WSJ, Bloomberg)
- **Categories**: general, world, economics, business, markets, politics, climate
- **Topics**: Automatic classification into 15+ topic categories
- **Geographies**: 13+ geographic regions tracked

## File Structure

```
project/
├── src/
│   ├── main.py          # Main aggregation script
│   ├── feed_parser.py   # RSS feed parsing
│   ├── database.py      # Database operations
│   ├── classifier.py    # Article classification
│   └── query.py         # Database querying
├── config/
│   └── feeds.yaml       # RSS feed configuration
├── data/
│   └── news.db          # SQLite database
├── logs/                # Application logs
└── requirements.txt     # Python dependencies
```

## Extending the System

### Adding New RSS Sources

Edit `config/feeds.yaml` to add new sources:

```yaml
sources:
  new_source:
    name: "Source Name"
    feeds:
      - url: "https://example.com/rss"
        category: "general"
```

### Customizing Classification

Edit `src/classifier.py` to:
- Add new topic keywords
- Add new geographic regions
- Modify sentiment analysis
- Add custom tagging rules

### Database Schema

The database includes tables for:
- `articles` - Main article data
- `tags` - Article tags
- `topics` - Topic hierarchy
- `geographies` - Geographic regions
- Junction tables for many-to-many relationships

## Future Enhancements

This generic foundation can be extended for:

1. **Bayesian Economic Modeling**: Feed article classifications into probability models
2. **Card Generation**: Create summary cards from related articles
3. **Sankey Diagrams**: Visualize economic scenario probabilities
4. **Advanced NLP**: Use LLMs for better content analysis
5. **Real-time Updates**: Implement continuous feed monitoring
6. **Web Interface**: Build dashboard for visualization
7. **Export Capabilities**: JSON/CSV export for analysis tools

## Running Regularly

To collect news regularly, you can set up a cron job:

```bash
# Edit crontab
crontab -e

# Add line to run every hour
0 * * * * cd /home/eoghan/project && source venv/bin/activate && python src/main.py
```

## System Requirements

- Python 3.8+
- ~50MB storage for SQLite database (grows with articles)
- Internet connection for RSS feeds
- Virtual environment recommended

The system is designed to be lightweight, reliable, and easily extensible for your future economic analysis needs.