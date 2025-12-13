#!/usr/bin/env python3
"""
Query tool for the news database.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent))

from database import NewsDatabase

def print_articles(articles, show_full=False, start_index=1):
    """Print articles in a formatted way."""
    if not articles:
        print("No articles found.")
        return
    
    for i, article in enumerate(articles):
        print(f"\n--- Article {start_index + i} ---")
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Category: {article.get('category', 'N/A')}")
        print(f"Published: {article.get('published', 'N/A')}")
        print(f"Link: {article['link']}")
        
        if show_full and article.get('description'):
            print(f"Description: {article['description'][:200]}...")
    
    print(f"\nShowing {len(articles)} articles")

def interactive_browse(db, args):
    """Interactive browsing mode with pagination."""
    page_size = args.limit
    current_page = args.page
    source_filter = args.source
    category_filter = args.category
    
    while True:
        # Calculate offset
        offset = (current_page - 1) * page_size
        
        # Get articles for current page
        since = datetime.now() - timedelta(hours=args.hours) if args.hours and args.hours > 0 else None
        articles = db.get_articles(
            limit=page_size,
            offset=offset,
            source=source_filter,
            category=category_filter,
            since=since
        )
        
        # Get total count for pagination info
        total_articles = db.get_article_count(source_filter)
        total_pages = (total_articles + page_size - 1) // page_size
        
        # Clear screen (works on most terminals)
        print("\033[2J\033[H")
        
        # Print header
        print("=" * 60)
        print("📰 NEWS DATABASE BROWSER")
        print("=" * 60)
        
        filters = []
        if source_filter:
            filters.append(f"Source: {source_filter}")
        if category_filter:
            filters.append(f"Category: {category_filter}")
        if args.hours:
            filters.append(f"Last {args.hours} hours")
            
        if filters:
            print(f"Filters: {' | '.join(filters)}")
        
        print(f"Page {current_page} of {total_pages} ({total_articles} total articles)")
        print("-" * 60)
        
        # Print articles
        if articles:
            start_index = offset + 1
            print_articles(articles, args.full, start_index)
        else:
            print("No articles found on this page.")
        
        # Print navigation options
        print("\n" + "=" * 60)
        print("Navigation:")
        if current_page > 1:
            print("  [p] Previous page")
        if current_page < total_pages:
            print("  [n] Next page")
        print("  [g] Go to page number")
        print("  [f] Toggle full details")
        print("  [s] Filter by source")
        print("  [c] Filter by category") 
        print("  [r] Reset filters")
        print("  [h] Show help")
        print("  [q] Quit")
        
        # Get user input
        try:
            choice = input("\nEnter command: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'n' and current_page < total_pages:
                current_page += 1
            elif choice == 'p' and current_page > 1:
                current_page -= 1
            elif choice == 'g':
                try:
                    page_num = int(input(f"Go to page (1-{total_pages}): "))
                    if 1 <= page_num <= total_pages:
                        current_page = page_num
                    else:
                        print(f"Invalid page number. Please enter 1-{total_pages}")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid page number.")
                    input("Press Enter to continue...")
            elif choice == 'f':
                args.full = not args.full
            elif choice == 's':
                sources = db.get_sources()
                print("Available sources:")
                for i, source in enumerate(sources, 1):
                    print(f"  {i}. {source}")
                print(f"  {len(sources)+1}. Clear filter")
                
                try:
                    source_choice = int(input("Select source number: ")) - 1
                    if 0 <= source_choice < len(sources):
                        source_filter = sources[source_choice]
                        current_page = 1  # Reset to first page
                    elif source_choice == len(sources):
                        source_filter = None
                        current_page = 1
                    else:
                        print("Invalid choice")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid choice")
                    input("Press Enter to continue...")
            elif choice == 'c':
                categories = ['general', 'world', 'economics', 'business', 'markets', 'politics', 'climate']
                print("Available categories:")
                for i, category in enumerate(categories, 1):
                    print(f"  {i}. {category}")
                print(f"  {len(categories)+1}. Clear filter")
                
                try:
                    cat_choice = int(input("Select category number: ")) - 1
                    if 0 <= cat_choice < len(categories):
                        category_filter = categories[cat_choice]
                        current_page = 1
                    elif cat_choice == len(categories):
                        category_filter = None
                        current_page = 1
                    else:
                        print("Invalid choice")
                        input("Press Enter to continue...")
                except ValueError:
                    print("Invalid choice")
                    input("Press Enter to continue...")
            elif choice == 'r':
                source_filter = None
                category_filter = None
                current_page = 1
            elif choice == 'h':
                print("\nHelp:")
                print("  Use 'n' and 'p' to navigate between pages")
                print("  Use 'g' to jump to a specific page")
                print("  Use 'f' to toggle between summary and full article details")
                print("  Use 's' and 'c' to filter by source or category")
                print("  Use 'r' to reset all filters")
                print("  Use 'q' to quit the browser")
                input("\nPress Enter to continue...")
            else:
                print("Invalid command. Type 'h' for help.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nGoodbye!")
    return 0

def main():
    """Main query function."""
    parser = argparse.ArgumentParser(description='Query News Database')
    parser.add_argument('--source', '-s', type=str, help='Filter by source')
    parser.add_argument('--category', '-c', type=str, help='Filter by category')
    parser.add_argument('--hours', type=int, default=24, help='Articles from last N hours (default: 24)')
    parser.add_argument('--limit', '-l', type=int, default=10, help='Number of articles to show (default: 10)')
    parser.add_argument('--full', '-f', action='store_true', help='Show full article details')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    parser.add_argument('--sources', action='store_true', help='List all sources')
    parser.add_argument('--browse', '-b', action='store_true', help='Interactive browse mode')
    parser.add_argument('--page', '-p', type=int, default=1, help='Page number (for browsing)')
    parser.add_argument('--search', type=str, help='Search articles by keywords in title/description')
    
    args = parser.parse_args()
    
    try:
        db = NewsDatabase()
        
        if args.stats:
            # Show database statistics
            total_articles = db.get_article_count()
            sources = db.get_sources()
            recent_articles = db.get_recent_articles(24)
            
            print(f"=== Database Statistics ===")
            print(f"Total articles: {total_articles}")
            print(f"Total sources: {len(sources)}")
            print(f"Articles in last 24h: {len(recent_articles)}")
            
            print(f"\nArticles by source:")
            for source in sources:
                count = db.get_article_count(source)
                print(f"  {source}: {count}")
            
            return 0
        
        if args.sources:
            # List all sources
            sources = db.get_sources()
            print("Available sources:")
            for source in sources:
                print(f"  - {source}")
            return 0
        
        if args.browse:
            # Interactive browse mode
            return interactive_browse(db, args)
        
        if args.search:
            # Search articles
            print(f"=== Search Results for: '{args.search}' ===")
            offset = (args.page - 1) * args.limit
            articles = db.search_articles(args.search, args.limit, offset)
            
            if articles:
                print_articles(articles, args.full, offset + 1)
                
                # Show pagination for search results
                if len(articles) == args.limit:
                    print(f"\nPage {args.page} - Next page: python src/query.py --search \"{args.search}\" --page {args.page + 1}")
            else:
                print("No articles found matching your search.")
            
            return 0
        
        # Query articles
        since = datetime.now() - timedelta(hours=args.hours) if args.hours and args.hours > 0 else None
        
        articles = db.get_articles(
            limit=args.limit,
            source=args.source,
            category=args.category,
            since=since
        )
        
        print(f"=== Recent Articles ===")
        if args.source:
            print(f"Source: {args.source}")
        if args.category:
            print(f"Category: {args.category}")
        if args.hours:
            print(f"Last {args.hours} hours")
        
        # Show pagination info if using pagination
        if args.page > 1 or len(articles) == args.limit:
            total_articles = db.get_article_count(args.source)
            total_pages = (total_articles + args.limit - 1) // args.limit
            print(f"\nPage {args.page} of {total_pages} (Total: {total_articles} articles)")
            if args.page < total_pages:
                print(f"Next page: python src/query.py --page {args.page + 1}")
        
        print_articles(articles, args.full, (args.page - 1) * args.limit + 1)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)