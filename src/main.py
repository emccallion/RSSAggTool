#!/usr/bin/env python3
"""
Main news aggregation script.
Fetches RSS feeds, classifies articles, and stores them in the database.
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from feed_parser import FeedParser
from database import NewsDatabase
from classifier import NewsClassifier

def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    Path('logs').mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/news_aggregator_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to run the news aggregator."""
    parser = argparse.ArgumentParser(description='News RSS Aggregator')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--source', '-s', type=str, help='Specific source to fetch (optional)')
    parser.add_argument('--dry-run', action='store_true', help='Parse feeds but don\'t save to database')
    parser.add_argument('--config', '-c', type=str, default='config/feeds.yaml', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting news aggregation process...")
    
    try:
        # Initialize components
        logger.info("Initializing components...")
        feed_parser = FeedParser(args.config)
        db = NewsDatabase()
        classifier = NewsClassifier()
        
        # Parse RSS feeds
        logger.info("Parsing RSS feeds...")
        if args.source:
            # Parse specific source only
            source_feeds = feed_parser.get_feed_urls_by_source(args.source)
            if not source_feeds:
                logger.error(f"Source '{args.source}' not found in configuration")
                return 1
            
            articles = []
            for feed_url in source_feeds:
                feed_articles = feed_parser.parse_feed(feed_url, args.source, 'general')
                articles.extend(feed_articles)
        else:
            # Parse all configured feeds
            articles = feed_parser.parse_all_feeds()
        
        if not articles:
            logger.warning("No articles found to process")
            return 0
        
        logger.info(f"Parsed {len(articles)} articles")
        
        # Classify articles
        logger.info("Classifying articles...")
        classified_articles = []
        
        for i, article in enumerate(articles):
            try:
                # Classify the article
                classification = classifier.classify_article(article)
                
                # Add classification data to article
                article['classification'] = classification
                classified_articles.append(article)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Classified {i + 1}/{len(articles)} articles")
                    
            except Exception as e:
                logger.error(f"Error classifying article '{article.get('title', 'Unknown')}': {e}")
                # Still add the article without classification
                classified_articles.append(article)
        
        # Save to database (unless dry run)
        if not args.dry_run:
            logger.info("Saving articles to database...")
            inserted_count = db.bulk_insert_articles(classified_articles)
            logger.info(f"Successfully inserted {inserted_count} new articles")
            
            # Print summary statistics
            total_articles = db.get_article_count()
            sources = db.get_sources()
            
            logger.info(f"Database now contains {total_articles} total articles from {len(sources)} sources")
            
            # Print recent article counts by source
            logger.info("Articles by source:")
            for source in sources:
                count = db.get_article_count(source)
                logger.info(f"  {source}: {count} articles")
                
        else:
            logger.info("Dry run complete - no articles saved to database")
            
            # Print sample classifications for dry run
            logger.info("Sample article classifications:")
            for i, article in enumerate(classified_articles[:3]):
                classification = article.get('classification', {})
                logger.info(f"  Article {i+1}: {article.get('title', 'No title')[:50]}...")
                logger.info(f"    Topics: {classification.get('topics', [])}")
                logger.info(f"    Geographies: {classification.get('geographies', [])}")
                logger.info(f"    Sentiment: {classification.get('sentiment', {}).get('label', 'unknown')}")
        
        logger.info("News aggregation completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)