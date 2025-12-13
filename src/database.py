import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
from pathlib import Path

class NewsDatabase:
    def __init__(self, db_path: str = "data/news.db"):
        """Initialize the news database."""
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        
        # Ensure data directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Articles table
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    link TEXT UNIQUE NOT NULL,
                    description TEXT,
                    summary TEXT,
                    content TEXT,
                    source TEXT NOT NULL,
                    category TEXT,
                    feed_url TEXT,
                    guid TEXT,
                    author TEXT,
                    published DATETIME,
                    fetched_at DATETIME NOT NULL,
                    processed_at DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Tags table
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT DEFAULT 'general', -- general, geography, topic, entity
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Article tags junction table
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER,
                    tag_id INTEGER,
                    confidence REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (article_id, tag_id),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );
                
                -- Geographies table for geographic tagging
                CREATE TABLE IF NOT EXISTS geographies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    country_code TEXT,
                    region TEXT,
                    continent TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Article geographies junction table
                CREATE TABLE IF NOT EXISTS article_geographies (
                    article_id INTEGER,
                    geography_id INTEGER,
                    confidence REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (article_id, geography_id),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (geography_id) REFERENCES geographies(id) ON DELETE CASCADE
                );
                
                -- Topics table for topic classification
                CREATE TABLE IF NOT EXISTS topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    parent_topic_id INTEGER,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_topic_id) REFERENCES topics(id)
                );
                
                -- Article topics junction table
                CREATE TABLE IF NOT EXISTS article_topics (
                    article_id INTEGER,
                    topic_id INTEGER,
                    confidence REAL DEFAULT 1.0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (article_id, topic_id),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (topic_id) REFERENCES topics(id) ON DELETE CASCADE
                );
                
                -- Feed sources table
                CREATE TABLE IF NOT EXISTS feed_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    feed_url TEXT UNIQUE NOT NULL,
                    category TEXT,
                    last_fetched DATETIME,
                    active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Create indexes for better performance
                CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
                CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published);
                CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
                CREATE INDEX IF NOT EXISTS idx_articles_fetched_at ON articles(fetched_at);
                CREATE INDEX IF NOT EXISTS idx_article_tags_article_id ON article_tags(article_id);
                CREATE INDEX IF NOT EXISTS idx_article_tags_tag_id ON article_tags(tag_id);
                CREATE INDEX IF NOT EXISTS idx_article_geographies_article_id ON article_geographies(article_id);
                CREATE INDEX IF NOT EXISTS idx_article_topics_article_id ON article_topics(article_id);
            """)
            
            # Insert default topics
            self._insert_default_topics(conn)
            
            # Insert default geographies
            self._insert_default_geographies(conn)
    
    def _insert_default_topics(self, conn):
        """Insert default topic categories."""
        default_topics = [
            ('Economics', None, 'Economic news and analysis'),
            ('Politics', None, 'Political news and developments'),
            ('Business', None, 'Corporate and business news'),
            ('Finance', None, 'Financial markets and banking'),
            ('Technology', None, 'Technology and innovation'),
            ('Energy', None, 'Energy sector and resources'),
            ('Climate', None, 'Climate and environmental issues'),
            ('Trade', None, 'International trade and commerce'),
            ('Central Banking', 'Economics', 'Monetary policy and central banks'),
            ('Inflation', 'Economics', 'Inflation and price movements'),
            ('GDP', 'Economics', 'Economic growth and GDP'),
            ('Elections', 'Politics', 'Elections and voting'),
            ('Policy', 'Politics', 'Government policy and regulation'),
            ('Geopolitics', 'Politics', 'International relations and conflicts'),
            ('Stock Markets', 'Finance', 'Equity markets and trading'),
            ('Bonds', 'Finance', 'Bond markets and fixed income'),
            ('Currencies', 'Finance', 'Foreign exchange and currencies'),
            ('Mergers & Acquisitions', 'Business', 'M&A activity'),
            ('Earnings', 'Business', 'Corporate earnings and results'),
        ]
        
        # Get existing topics to avoid duplicates
        existing_topics = conn.execute("SELECT name FROM topics").fetchall()
        existing_names = {row[0] for row in existing_topics}
        
        # Insert parent topics first
        for name, parent, description in default_topics:
            if name not in existing_names and parent is None:
                conn.execute(
                    "INSERT OR IGNORE INTO topics (name, description) VALUES (?, ?)",
                    (name, description)
                )
        
        # Insert child topics
        for name, parent, description in default_topics:
            if name not in existing_names and parent is not None:
                parent_id = conn.execute(
                    "SELECT id FROM topics WHERE name = ?", (parent,)
                ).fetchone()
                
                if parent_id:
                    conn.execute(
                        "INSERT OR IGNORE INTO topics (name, parent_topic_id, description) VALUES (?, ?, ?)",
                        (name, parent_id[0], description)
                    )
    
    def _insert_default_geographies(self, conn):
        """Insert default geographic regions."""
        default_geographies = [
            ('United States', 'US', 'North America', 'North America'),
            ('United Kingdom', 'GB', 'Europe', 'Europe'),
            ('European Union', 'EU', 'Europe', 'Europe'),
            ('China', 'CN', 'East Asia', 'Asia'),
            ('Japan', 'JP', 'East Asia', 'Asia'),
            ('Australia', 'AU', 'Oceania', 'Oceania'),
            ('Canada', 'CA', 'North America', 'North America'),
            ('Germany', 'DE', 'Europe', 'Europe'),
            ('France', 'FR', 'Europe', 'Europe'),
            ('India', 'IN', 'South Asia', 'Asia'),
            ('Brazil', 'BR', 'South America', 'South America'),
            ('Russia', 'RU', 'Eastern Europe', 'Europe'),
            ('Global', None, 'Global', 'Global'),
        ]
        
        conn.executemany(
            "INSERT OR IGNORE INTO geographies (name, country_code, region, continent) VALUES (?, ?, ?, ?)",
            default_geographies
        )
    
    def insert_article(self, article_data: Dict) -> Optional[int]:
        """Insert a new article into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    INSERT OR REPLACE INTO articles 
                    (title, link, description, summary, source, category, feed_url, 
                     guid, author, published, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_data.get('title'),
                    article_data.get('link'),
                    article_data.get('description'),
                    article_data.get('summary'),
                    article_data.get('source'),
                    article_data.get('category'),
                    article_data.get('feed_url'),
                    article_data.get('guid'),
                    article_data.get('author'),
                    article_data.get('published'),
                    article_data.get('fetched_at')
                ))
                
                article_id = cursor.lastrowid
                
                # Insert tags if provided
                if 'tags' in article_data and article_data['tags']:
                    self._insert_article_tags(conn, article_id, article_data['tags'])
                
                return article_id
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                self.logger.debug(f"Article already exists: {article_data.get('link')}")
                # Return existing article ID
                return self.get_article_id_by_link(article_data.get('link'))
            else:
                self.logger.error(f"Error inserting article: {e}")
                return None
        except Exception as e:
            self.logger.error(f"Error inserting article: {e}")
            return None
    
    def _insert_article_tags(self, conn, article_id: int, tags: List[str]):
        """Insert tags for an article."""
        for tag_name in tags:
            if tag_name.strip():
                # Insert or get tag
                conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name.strip(),))
                tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name.strip(),)).fetchone()[0]
                
                # Link article to tag
                conn.execute(
                    "INSERT OR IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)",
                    (article_id, tag_id)
                )
    
    def get_article_id_by_link(self, link: str) -> Optional[int]:
        """Get article ID by its link."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT id FROM articles WHERE link = ?", (link,)).fetchone()
            return result[0] if result else None
    
    def get_articles(self, limit: int = 100, offset: int = 0, source: str = None, 
                    category: str = None, since: datetime = None) -> List[Dict]:
        """Get articles with optional filtering."""
        query = "SELECT * FROM articles"
        params = []
        conditions = []
        
        if source:
            conditions.append("source = ?")
            params.append(source)
        
        if category:
            conditions.append("category = ?")
            params.append(category)
        
        if since:
            conditions.append("published >= ?")
            params.append(since)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY published DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def get_article_count(self, source: str = None) -> int:
        """Get total number of articles."""
        query = "SELECT COUNT(*) FROM articles"
        params = []
        
        if source:
            query += " WHERE source = ?"
            params.append(source)
        
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(query, params).fetchone()[0]
    
    def get_sources(self) -> List[str]:
        """Get list of all sources in database."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
            return [row[0] for row in rows]
    
    def get_recent_articles(self, hours: int = 24) -> List[Dict]:
        """Get articles from the last N hours."""
        from datetime import timedelta
        since = datetime.now() - timedelta(hours=hours)
        return self.get_articles(since=since)
    
    def search_articles(self, keywords: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Search articles by keywords in title and description."""
        # Create search terms
        search_terms = keywords.lower().split()
        
        # Build query with LIKE conditions for each search term
        conditions = []
        params = []
        
        for term in search_terms:
            conditions.append("(LOWER(title) LIKE ? OR LOWER(description) LIKE ?)")
            params.extend([f"%{term}%", f"%{term}%"])
        
        query = f"""
            SELECT * FROM articles 
            WHERE {' AND '.join(conditions)}
            ORDER BY published DESC 
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def bulk_insert_articles(self, articles: List[Dict]) -> int:
        """Insert multiple articles in a single transaction."""
        inserted_count = 0
        
        for article in articles:
            article_id = self.insert_article(article)
            if article_id:
                inserted_count += 1
        
        self.logger.info(f"Inserted {inserted_count} new articles out of {len(articles)} total")
        return inserted_count