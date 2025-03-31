from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    """Schema for the query request."""
    query: str = Field(..., description="The user's cooking or recipe query")
    
class QueryResponse(BaseModel):
    """Schema for the query response."""
    response: str = Field(..., description="The response to the user's query")
    relevant: bool = Field(..., description="Whether the query was relevant to cooking")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information about processing")
    
class SearchResult(BaseModel):
    """Schema for search results."""
    title: str
    snippet: str
    link: str
    
class CookingVerification(BaseModel):
    """Schema for cooking verification results."""
    can_cook: bool
    missing_tools: Optional[List[str]] = None
    explanation: str 