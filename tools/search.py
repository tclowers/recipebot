from typing import List, Dict, Any
from langchain_core.tools import tool
from utils.logging_utils import log_tool_call

@tool
def search_recipes(query: str) -> Dict[str, Any]:
    """
    Searches for recipes on the web based on the user's query.
    
    Args:
        query: The search query string
    
    Returns:
        Dict with search results
    """
    log_tool_call("search_recipes", {"query": query})
    
    # Mock response for Chicken Soup
    if "chicken soup" in query.lower():
        return {
            "results": [
                {
                    "title": "Classic Chicken Soup Recipe",
                    "snippet": "This homemade chicken soup recipe features tender chicken, fresh vegetables, and aromatic herbs in a flavorful broth. Perfect comfort food for cold days!",
                    "link": "https://example.com/classic-chicken-soup"
                },
                {
                    "title": "Easy 30-Minute Chicken Soup",
                    "snippet": "Make delicious chicken soup in just 30 minutes with this simple recipe. Uses rotisserie chicken, pre-cut vegetables, and boxed broth for a quick meal.",
                    "link": "https://cooking.example.com/quick-chicken-soup"
                },
                {
                    "title": "Healing Chicken Noodle Soup",
                    "snippet": "This medicinal chicken noodle soup is packed with immune-boosting ingredients like garlic, ginger, and turmeric. Perfect when feeling under the weather.",
                    "link": "https://health.example.com/healing-soup"
                }
            ]
        }
    # For other queries, you would actually call the SERP API
    # But for now, return a generic mock response
    return {
        "results": [
            {
                "title": f"Recipe for {query}",
                "snippet": f"Delicious {query} recipe that can be made in under 30 minutes.",
                "link": "https://example.com/recipe"
            }
        ]
    }

@tool
def search_cooking_question(query: str) -> Dict[str, Any]:
    """
    Searches for general cooking questions and techniques.
    
    Args:
        query: The search query string
    
    Returns:
        Dict with search results
    """
    log_tool_call("search_cooking_question", {"query": query})
    
    # Mock response
    return {
        "results": [
            {
                "title": f"How to {query}",
                "snippet": f"Expert advice on {query} with step-by-step instructions.",
                "link": "https://cooking.example.com/techniques"
            }
        ]
    } 