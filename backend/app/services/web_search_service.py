"""
Web Search Service for compliance research.
Integrates with search APIs to enhance content generation with real-time data.
"""

import os
import logging
from typing import List, Dict, Optional
import requests
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebSearchService:
    """
    Web search service for researching compliance topics.
    Uses Serper API (Google Search) for reliable results.
    """
    
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY", "")
        self.api_url = "https://google.serper.dev/search"
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("SERPER_API_KEY not set. Web search disabled.")
    
    async def research(self, query: str, max_results: int = 3) -> List[Dict[str, str]]:
        """
        Perform web search for the given query.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, snippet, and URL
        """
        if not self.enabled:
            logger.info("Web search disabled - no API key")
            return []
        
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "q": query,
                "num": max_results
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.error(f"Search API error: {response.status_code}")
                return []
            
            data = response.json()
            results = []
            
            # Extract organic results
            for item in data.get("organic", [])[:max_results]:
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "url": item.get("link", "")
                })
            
            logger.info(f"Web search for '{query}': {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    def extract_keywords(self, prompt: str) -> str:
        """
        Extract search keywords from user prompt.
        Simple implementation - can be enhanced with NLP.
        """
        # Remove common words and extract key terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = prompt.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Take first 5 keywords
        return " ".join(keywords[:5])


# Singleton instance
_search_service: Optional[WebSearchService] = None


def get_search_service() -> WebSearchService:
    """Get or create web search service instance."""
    global _search_service
    if _search_service is None:
        _search_service = WebSearchService()
    return _search_service
