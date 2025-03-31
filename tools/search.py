from typing import Dict, Any
from langchain.tools import tool
from utils.logging_utils import log_tool_call, logger
import os
from serpapi import GoogleSearch

@tool
def search_recipes(query: str) -> Dict[str, Any]:
    """
    Searches for recipes on the web based on the user's query using SERP API.
    
    Args:
        query: The search query string
    
    Returns:
        Dict with search results
    """
    log_tool_call("search_recipes", {"query": query})
    
    # Get API key from environment variable
    serp_api_key = os.environ.get("SERP_API_KEY")
    
    if not serp_api_key:
        logger.warning("SERP API key not found. Falling back to mock responses.")
        return _get_mock_recipe_response(query)
    
    try:
        # Avoid duplicating "recipe" in the query
        search_query = query.lower().strip()
        if "recipe" not in search_query:
            search_query = f"{search_query} recipe"
        
        logger.info(f"Searching SERP API for: {search_query}")
        
        # Set up the SERP API parameters
        params = {
            "api_key": serp_api_key,
            "engine": "google",
            "q": search_query,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": 3  # Number of results to fetch
        }
        
        # Execute the search using SERP SDK
        search = GoogleSearch(params)
        data = search.get_dict()
        
        # Add debug info for the API response
        if "search_metadata" in data:
            logger.info(f"SERP API metadata: status={data['search_metadata'].get('status')}, "
                        f"id={data['search_metadata'].get('id')}, "
                        f"total_time_taken={data['search_metadata'].get('total_time_taken')}")
        
        # Parse the results
        results = []
        if "organic_results" in data:
            logger.info(f"Found {len(data['organic_results'])} organic results")
            
            for result in data["organic_results"][:3]:  # Take top 3 results
                title = result.get("title", "")
                snippet = result.get("snippet", "")
                link = result.get("link", "")
                
                # Log a condensed version of each result
                logger.info(f"Result: {title[:50]}... | {snippet[:100]}... | {link}")
                
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "link": link
                })
        else:
            logger.warning("No organic_results found in SERP API response. Keys found: " + 
                          ", ".join(list(data.keys())[:5]) + 
                          ("..." if len(data.keys()) > 5 else ""))
        
        # Return results or fall back to mock if no results found
        if results:
            # Log a summary of the results
            logger.info(f"Returning {len(results)} recipe results for query: {search_query}")
            return {"results": results}
        else:
            logger.warning("No results found from SERP API. Falling back to mock responses.")
            return _get_mock_recipe_response(query)
            
    except Exception as e:
        logger.error(f"Error querying SERP API: {str(e)}")
        # Fall back to mock responses on error
        return _get_mock_recipe_response(query)

def _get_mock_recipe_response(query: str) -> Dict[str, Any]:
    """Helper function to get mock recipe responses when API is unavailable."""
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
    # For other queries, return a generic mock response
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
    Searches for answers to cooking-related questions using SERP API.
    
    Args:
        query: The cooking question to search for
    
    Returns:
        Dict with search results
    """
    log_tool_call("search_cooking_question", {"query": query})
    
    # Get API key from environment variable
    serp_api_key = os.environ.get("SERP_API_KEY")
    
    if not serp_api_key:
        logger.warning("SERP API key not found. Falling back to mock responses.")
        return _get_mock_cooking_response(query)
    
    try:
        # Set up the SERP API parameters
        params = {
            "api_key": serp_api_key,
            "engine": "google",
            "q": query,
            "google_domain": "google.com",
            "gl": "us",
            "hl": "en",
            "num": 3  # Number of results to fetch
        }
        
        # Execute the search using SERP SDK
        search = GoogleSearch(params)
        data = search.get_dict()
        
        # Parse the results
        results = []
        if "organic_results" in data:
            for result in data["organic_results"][:3]:
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("snippet", ""),
                    "link": result.get("link", "")
                })
        
        # Return results or fall back to mock if no results found
        if results:
            return {"results": results}
        else:
            logger.warning("No results found from SERP API. Falling back to mock responses.")
            return _get_mock_cooking_response(query)
            
    except Exception as e:
        logger.error(f"Error querying SERP API: {str(e)}")
        # Fall back to mock responses on error
        return _get_mock_cooking_response(query)

def _get_mock_cooking_response(query: str) -> Dict[str, Any]:
    """Helper function to get mock cooking question responses when API is unavailable."""
    return {
        "results": [
            {
                "title": f"How to {query}",
                "snippet": f"Learn the best techniques for {query} with these expert tips.",
                "link": "https://example.com/cooking-tips"
            },
            {
                "title": f"Common mistakes when {query}",
                "snippet": f"Avoid these common errors when {query} to get better results every time.",
                "link": "https://cooking-school.example.com/mistakes"
            }
        ]
    } 