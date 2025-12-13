# News Aggregation System

A generic RSS feed aggregator for collecting and organizing news articles from major financial and geopolitical news sources.

## Features

- RSS feed parsing and aggregation
- Article storage with metadata
- Tagging and categorization
- Geographic and topic classification
- Database storage for historical analysis

## Supported Sources

- Financial Times
- Wall Street Journal  
- New York Times
- The Economist
- Foreign Affairs
- Australian Financial Review
- Bloomberg

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Configure RSS feeds in `config/feeds.yaml`
3. Run the aggregator: `python src/main.py`

## Database

SQLite database storing articles with fields for title, content, source, tags, geography, and timestamps.