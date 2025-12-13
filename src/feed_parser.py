import feedparser
import requests
import yaml
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
import logging
import time
from typing import List, Dict, Optional

class FeedParser:
    def __init__(self, config_path: str = "config/feeds.yaml"):
        """Initialize the RSS feed parser with configuration."""
        self.config_path = config_path
        self.feeds_config = self._load_config()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict:
        """Load RSS feed configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Configuration file {self.config_path} not found")
            return {"sources": {}}
    
    def parse_feed(self, feed_url: str, source_name: str, category: str) -> List[Dict]:
        """Parse a single RSS feed and return articles."""
        articles = []
        
        try:
            self.logger.info(f"Parsing feed: {feed_url}")
            
            # Parse the RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.status != 200:
                self.logger.warning(f"HTTP {feed.status} for feed {feed_url}")
                return articles
            
            # Extract articles from feed entries
            for entry in feed.entries:
                article = self._extract_article_data(entry, source_name, category, feed_url)
                if article:
                    articles.append(article)
                    
        except Exception as e:
            self.logger.error(f"Error parsing feed {feed_url}: {str(e)}")
            
        return articles
    
    def _extract_article_data(self, entry, source_name: str, category: str, feed_url: str) -> Optional[Dict]:
        """Extract article data from a feed entry."""
        try:
            # Extract basic article information
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
            
            # Extract author if available
            author = getattr(entry, 'author', '')
            if hasattr(entry, 'authors') and entry.authors:
                author = ', '.join([a.get('name', '') for a in entry.authors if a.get('name')])
            article['author'] = author
            
            # Extract tags if available
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
            article['tags'] = tags
            
            # Add fetch timestamp
            article['fetched_at'] = datetime.now(timezone.utc)
            
            return article
            
        except Exception as e:
            self.logger.error(f"Error extracting article data: {str(e)}")
            return None
    
    def parse_all_feeds(self) -> List[Dict]:
        """Parse all configured RSS feeds and return all articles."""
        all_articles = []
        
        sources = self.feeds_config.get('sources', {})
        
        for source_key, source_config in sources.items():
            source_name = source_config.get('name', source_key)
            feeds = source_config.get('feeds', [])
            
            self.logger.info(f"Processing {len(feeds)} feeds for {source_name}")
            
            for feed_config in feeds:
                feed_url = feed_config.get('url')
                category = feed_config.get('category', 'general')
                
                if feed_url:
                    articles = self.parse_feed(feed_url, source_name, category)
                    all_articles.extend(articles)
                    
                    # Add a small delay to be respectful to servers
                    time.sleep(1)
        
        self.logger.info(f"Total articles parsed: {len(all_articles)}")
        return all_articles
    
    def get_source_list(self) -> List[str]:
        """Get list of configured news sources."""
        sources = self.feeds_config.get('sources', {})
        return [config.get('name', key) for key, config in sources.items()]
    
    def get_feed_urls_by_source(self, source_name: str) -> List[str]:
        """Get all feed URLs for a specific source."""
        sources = self.feeds_config.get('sources', {})
        
        for source_key, source_config in sources.items():
            if source_config.get('name') == source_name:
                feeds = source_config.get('feeds', [])
                return [feed.get('url') for feed in feeds if feed.get('url')]
        
        return []