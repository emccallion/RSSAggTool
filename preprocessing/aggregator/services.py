"""
RSS Feed parsing and article classification services.
Integrated Django version - writes directly to PreprocessingArticle model.
"""
import feedparser
import requests
import yaml
import logging
import time
from datetime import datetime, timezone
from typing import List, Dict, Optional
from pathlib import Path
from textblob import TextBlob
from django.conf import settings


logger = logging.getLogger(__name__)


class FeedParser:
    """RSS feed parser integrated with Django."""

    def __init__(self, config_path: str = None):
        """Initialize the RSS feed parser with configuration."""
        if config_path is None:
            # Default to config/feeds.yaml in parent directory
            config_path = Path(settings.BASE_DIR).parent / 'config' / 'feeds.yaml'

        self.config_path = str(config_path)
        self.feeds_config = self._load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _load_config(self) -> Dict:
        """Load RSS feed configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            return {"sources": {}}

    def parse_feed(self, feed_url: str, source_name: str, category: str) -> List[Dict]:
        """Parse a single RSS feed and return articles."""
        articles = []

        try:
            logger.info(f"Parsing feed: {feed_url}")

            feed = feedparser.parse(feed_url)

            if feed.status != 200:
                logger.warning(f"HTTP {feed.status} for feed {feed_url}")
                return articles

            for entry in feed.entries:
                article = self._extract_article_data(entry, source_name, category, feed_url)
                if article:
                    articles.append(article)

        except Exception as e:
            logger.error(f"Error parsing feed {feed_url}: {str(e)}")

        return articles

    def _extract_article_data(self, entry, source_name: str, category: str, feed_url: str) -> Optional[Dict]:
        """Extract article data from a feed entry."""
        try:
            article = {
                'title': getattr(entry, 'title', ''),
                'link': getattr(entry, 'link', ''),
                'description': getattr(entry, 'description', ''),
                'summary': getattr(entry, 'summary', ''),
                'source': source_name,
                'category': category,
                'feed_url': feed_url,
                'guid': getattr(entry, 'id', getattr(entry, 'link', '')),
            }

            # Extract publication date
            published_time = getattr(entry, 'published_parsed', None)
            if published_time:
                article['published'] = datetime(*published_time[:6], tzinfo=timezone.utc)
            else:
                article['published'] = datetime.now(timezone.utc)

            # Extract author
            author = getattr(entry, 'author', '')
            if hasattr(entry, 'authors') and entry.authors:
                author = ', '.join([a.get('name', '') for a in entry.authors if a.get('name')])
            article['author'] = author

            # Extract tags
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
            article['tags'] = tags

            article['fetched_at'] = datetime.now(timezone.utc)

            return article

        except Exception as e:
            logger.error(f"Error extracting article data: {str(e)}")
            return None

    def parse_all_feeds(self) -> List[Dict]:
        """Parse all configured RSS feeds and return all articles."""
        all_articles = []

        sources = self.feeds_config.get('sources', {})

        for source_key, source_config in sources.items():
            source_name = source_config.get('name', source_key)
            feeds = source_config.get('feeds', [])

            logger.info(f"Processing {len(feeds)} feeds for {source_name}")

            for feed_config in feeds:
                feed_url = feed_config.get('url')
                category = feed_config.get('category', 'general')

                if feed_url:
                    articles = self.parse_feed(feed_url, source_name, category)
                    all_articles.extend(articles)
                    time.sleep(1)  # Be respectful to servers

        logger.info(f"Total articles parsed: {len(all_articles)}")
        return all_articles


class NewsClassifier:
    """Article classification using keyword matching and sentiment analysis."""

    def __init__(self):
        self.topic_keywords = {
            'Economics': ['economy', 'economic', 'gdp', 'growth', 'recession', 'inflation',
                         'deflation', 'unemployment', 'jobs', 'fiscal', 'monetary', 'budget'],
            'Central Banking': ['fed', 'federal reserve', 'central bank', 'interest rate',
                               'monetary policy', 'ecb', 'boe'],
            'Politics': ['government', 'political', 'politics', 'election', 'vote',
                        'campaign', 'policy', 'legislation'],
            'Geopolitics': ['international', 'diplomacy', 'foreign policy', 'sanctions',
                           'trade war', 'conflict', 'nato', 'un'],
            'Business': ['company', 'corporate', 'business', 'enterprise', 'ceo',
                        'executive', 'shares', 'stock', 'revenue', 'profit'],
            'Finance': ['market', 'trading', 'investment', 'investor', 'fund', 'bank',
                       'banking', 'financial', 'credit', 'bond', 'equity'],
            'Technology': ['tech', 'technology', 'digital', 'ai', 'blockchain',
                          'cryptocurrency', 'software', 'innovation'],
            'Energy': ['oil', 'gas', 'energy', 'renewable', 'solar', 'wind', 'nuclear',
                      'coal', 'opec'],
            'Climate': ['climate', 'environment', 'green', 'carbon', 'emissions',
                       'sustainability', 'global warming'],
            'Trade': ['trade', 'export', 'import', 'tariff', 'wto', 'free trade'],
        }

    def classify_article(self, article: Dict) -> Dict:
        """Classify an article and return classification data."""
        text = f"{article.get('title', '')} {article.get('description', '')} {article.get('summary', '')}".lower()

        return {
            'topics': self._extract_topics(text),
            'sentiment': self._analyze_sentiment(text),
        }

    def _extract_topics(self, text: str) -> List[str]:
        """Extract topics from text."""
        matched_topics = []

        for topic, keywords in self.topic_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                matched_topics.append((topic, score))

        # Return top 3 topics
        matched_topics.sort(key=lambda x: x[1], reverse=True)
        return [topic for topic, score in matched_topics[:3]]

    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            if polarity > 0.1:
                sentiment_label = 'positive'
            elif polarity < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'

            return {
                'label': sentiment_label,
                'polarity': polarity,
            }
        except:
            return {
                'label': 'neutral',
                'polarity': 0.0,
            }
