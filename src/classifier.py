import re
from typing import List, Dict, Set, Tuple
import logging
from textblob import TextBlob

class NewsClassifier:
    def __init__(self):
        """Initialize the news classifier."""
        self.logger = logging.getLogger(__name__)
        
        # Define keyword mappings for topics
        self.topic_keywords = {
            'Economics': [
                'economy', 'economic', 'gdp', 'growth', 'recession', 'inflation', 
                'deflation', 'unemployment', 'jobs', 'employment', 'fiscal', 
                'monetary', 'budget', 'debt', 'deficit', 'stimulus'
            ],
            'Central Banking': [
                'fed', 'federal reserve', 'central bank', 'interest rate', 
                'monetary policy', 'quantitative easing', 'ecb', 'boe', 
                'bank of japan', 'rba', 'pboc'
            ],
            'Politics': [
                'government', 'political', 'politics', 'election', 'vote', 
                'campaign', 'policy', 'legislation', 'congress', 'parliament', 
                'senate', 'house', 'president', 'prime minister'
            ],
            'Geopolitics': [
                'international', 'diplomacy', 'foreign policy', 'alliance', 
                'sanctions', 'trade war', 'conflict', 'peace', 'nato', 'un', 
                'united nations', 'summit', 'bilateral', 'multilateral'
            ],
            'Business': [
                'company', 'corporate', 'business', 'enterprise', 'corporation', 
                'startup', 'ceo', 'executive', 'management', 'board', 'shares', 
                'stock', 'revenue', 'profit', 'earnings'
            ],
            'Finance': [
                'market', 'trading', 'investment', 'investor', 'fund', 'bank', 
                'banking', 'financial', 'credit', 'loan', 'mortgage', 'bond', 
                'equity', 'currency', 'forex', 'commodity'
            ],
            'Technology': [
                'tech', 'technology', 'digital', 'ai', 'artificial intelligence', 
                'blockchain', 'cryptocurrency', 'bitcoin', 'software', 'hardware', 
                'innovation', 'startup', 'silicon valley'
            ],
            'Energy': [
                'oil', 'gas', 'energy', 'renewable', 'solar', 'wind', 'nuclear', 
                'coal', 'petroleum', 'lng', 'pipeline', 'opec', 'electricity', 
                'power', 'grid'
            ],
            'Climate': [
                'climate', 'environment', 'green', 'carbon', 'emissions', 
                'sustainability', 'renewable', 'clean energy', 'global warming', 
                'paris agreement', 'esg'
            ],
            'Trade': [
                'trade', 'export', 'import', 'tariff', 'customs', 'wto', 
                'free trade', 'trade agreement', 'supply chain', 'logistics'
            ]
        }
        
        # Define geographic keywords
        self.geography_keywords = {
            'United States': [
                'us', 'usa', 'america', 'american', 'united states', 'washington', 
                'new york', 'california', 'texas', 'wall street', 'silicon valley'
            ],
            'United Kingdom': [
                'uk', 'britain', 'british', 'england', 'london', 'scotland', 
                'wales', 'northern ireland'
            ],
            'European Union': [
                'eu', 'europe', 'european', 'brussels', 'eurozone', 'euro area'
            ],
            'China': [
                'china', 'chinese', 'beijing', 'shanghai', 'hong kong', 'mainland china'
            ],
            'Japan': [
                'japan', 'japanese', 'tokyo', 'osaka', 'yen'
            ],
            'Australia': [
                'australia', 'australian', 'sydney', 'melbourne', 'canberra'
            ],
            'Canada': [
                'canada', 'canadian', 'toronto', 'ottawa', 'vancouver'
            ],
            'Germany': [
                'germany', 'german', 'berlin', 'frankfurt', 'munich'
            ],
            'France': [
                'france', 'french', 'paris', 'lyon'
            ],
            'India': [
                'india', 'indian', 'mumbai', 'delhi', 'bangalore'
            ],
            'Russia': [
                'russia', 'russian', 'moscow', 'kremlin'
            ],
            'Brazil': [
                'brazil', 'brazilian', 'sao paulo', 'rio de janeiro'
            ]
        }
        
        # Market-specific terms
        self.market_keywords = {
            'Stock Markets': [
                'stock market', 'equity', 'shares', 'dow jones', 'nasdaq', 
                's&p 500', 'ftse', 'dax', 'nikkei', 'asx', 'tsx'
            ],
            'Bonds': [
                'bond', 'treasury', 'government bond', 'corporate bond', 
                'yield', 'fixed income'
            ],
            'Currencies': [
                'currency', 'forex', 'exchange rate', 'dollar', 'euro', 
                'pound', 'yen', 'yuan', 'rmb'
            ]
        }
        
        # Combine all keyword mappings
        self.all_keywords = {**self.topic_keywords, **self.geography_keywords, **self.market_keywords}
    
    def classify_article(self, article: Dict) -> Dict:
        """Classify an article and return topics, geographies, and other tags."""
        # Combine title and description for analysis
        text = f"{article.get('title', '')} {article.get('description', '')} {article.get('summary', '')}"
        text = text.lower()
        
        # Extract topics
        topics = self._extract_topics(text)
        
        # Extract geographies
        geographies = self._extract_geographies(text)
        
        # Extract sentiment
        sentiment = self._analyze_sentiment(text)
        
        # Generate additional tags
        additional_tags = self._generate_additional_tags(text)
        
        return {
            'topics': topics,
            'geographies': geographies,
            'sentiment': sentiment,
            'additional_tags': additional_tags
        }
    
    def _extract_topics(self, text: str) -> List[Tuple[str, float]]:
        """Extract topics from text with confidence scores."""
        topics = []
        
        for topic, keywords in self.topic_keywords.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                # Count exact matches
                if keyword in text:
                    matches += 1
                    # Give higher score for exact phrase matches
                    if len(keyword.split()) > 1:
                        score += 2
                    else:
                        score += 1
            
            if matches > 0:
                # Normalize score based on text length and number of keywords
                confidence = min(score / len(keywords) * 2, 1.0)
                topics.append((topic, confidence))
        
        # Sort by confidence and return top topics
        topics.sort(key=lambda x: x[1], reverse=True)
        return topics[:5]  # Return top 5 topics
    
    def _extract_geographies(self, text: str) -> List[Tuple[str, float]]:
        """Extract geographic mentions from text."""
        geographies = []
        
        for geography, keywords in self.geography_keywords.items():
            score = 0
            matches = 0
            
            for keyword in keywords:
                if keyword in text:
                    matches += 1
                    score += 1
            
            if matches > 0:
                confidence = min(score / len(keywords) * 3, 1.0)
                geographies.append((geography, confidence))
        
        # Sort by confidence
        geographies.sort(key=lambda x: x[1], reverse=True)
        return geographies[:3]  # Return top 3 geographies
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of the text."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment_label = 'positive'
            elif polarity < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            return {
                'label': sentiment_label,
                'polarity': polarity,
                'subjectivity': subjectivity
            }
        except:
            return {
                'label': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.5
            }
    
    def _generate_additional_tags(self, text: str) -> List[str]:
        """Generate additional tags based on text content."""
        tags = []
        
        # Economic indicators
        economic_indicators = [
            'inflation', 'gdp', 'unemployment', 'interest rate', 'cpi', 'ppi'
        ]
        for indicator in economic_indicators:
            if indicator in text:
                tags.append(f'indicator_{indicator.replace(" ", "_")}')
        
        # Company types
        company_types = ['bank', 'tech', 'energy', 'pharmaceutical', 'automotive']
        for comp_type in company_types:
            if comp_type in text:
                tags.append(f'sector_{comp_type}')
        
        # Market conditions
        market_conditions = ['bull market', 'bear market', 'volatility', 'crash', 'rally']
        for condition in market_conditions:
            if condition in text:
                tags.append(f'market_{condition.replace(" ", "_")}')
        
        # News urgency
        urgent_keywords = ['breaking', 'urgent', 'alert', 'developing']
        for keyword in urgent_keywords:
            if keyword in text:
                tags.append('urgent')
                break
        
        return tags
    
    def get_topic_hierarchy(self) -> Dict:
        """Return the topic hierarchy for reference."""
        return {
            'Economics': ['Central Banking', 'Inflation', 'GDP'],
            'Politics': ['Elections', 'Policy', 'Geopolitics'],
            'Finance': ['Stock Markets', 'Bonds', 'Currencies'],
            'Business': ['Mergers & Acquisitions', 'Earnings'],
        }
    
    def suggest_new_topics(self, recent_articles: List[Dict], min_frequency: int = 5) -> List[str]:
        """Suggest new topics based on frequently occurring terms."""
        # This would analyze recent articles to find new trending topics
        # For now, return empty list - can be enhanced with NLP
        return []