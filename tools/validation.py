from typing import Dict, Any, List, ClassVar
from langchain_core.tools import BaseTool
from utils.logging_utils import log_tool_call
from utils.llm_utils import get_llm
from config import AVAILABLE_COOKWARE
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field

class QueryInput(BaseModel):
    query: str

class ValidateQueryRelevance(BaseTool):
    name: ClassVar[str] = "validate_query_relevance"
    description: ClassVar[str] = "Determines if the query is related to cooking, recipes, or food preparation."
    args_schema: ClassVar[type] = QueryInput

    def _run(self, query: str) -> Dict[str, Any]:
        """Run the tool."""
        log_tool_call("validate_query_relevance", {"query": query})
        
        # Get LLM instance
        llm = get_llm()
        
        # Create messages for the LLM
        messages = [
            SystemMessage(content="""
            You are a query classifier for a cooking and recipe application. 
            Your task is to determine if a user's query is related to cooking, recipes, food preparation, or ingredients.
            
            ONLY respond with "true" if the query is cooking-related, or "false" if it is not.
            
            Examples of cooking-related queries:
            - How do I make pasta?
            - What's a good recipe for chicken soup?
            - Can I substitute butter with oil?
            - How long should I cook salmon?
            - What tools do I need to make pizza?
            
            Examples of non-cooking-related queries:
            - What's the weather today?
            - How do I fix my car?
            - Who won the Super Bowl?
            - What's the capital of France?
            - Can you help me with my homework?
            """),
            HumanMessage(content=f"Is this query cooking-related? Query: {query}")
        ]
        
        # Get classification from LLM
        classification_response = llm.invoke(messages)
        
        # Parse the response to get a boolean
        is_relevant = "true" in classification_response.content.lower()
        
        # If relevant, get a more detailed explanation
        explanation = ""
        if is_relevant:
            explanation_messages = [
                SystemMessage(content="""
                You are a helpful cooking assistant. Briefly explain why a query is cooking-related.
                Keep your explanation to one sentence.
                """),
                HumanMessage(content=f"Briefly explain why this query is cooking-related: {query}")
            ]
            explanation_response = llm.invoke(explanation_messages)
            explanation = explanation_response.content.strip()
        else:
            explanation = "This query is not related to cooking, recipes, or food preparation."
        
        return {
            "relevant": is_relevant,
            "explanation": explanation
        }

    async def _arun(self, query: str) -> Dict[str, Any]:
        """Run the tool asynchronously."""
        # For now, just call the sync version
        return self._run(query)

class CookwareInput(BaseModel):
    required_tools: List[str]

class ValidateCookware(BaseTool):
    name: ClassVar[str] = "validate_cookware"
    description: ClassVar[str] = "Validates whether the user has the necessary cookware to make a recipe."
    args_schema: ClassVar[type] = CookwareInput

    def _run(self, required_tools: List[str]) -> Dict[str, Any]:
        """Run the tool."""
        log_tool_call("validate_cookware", {"required_tools": required_tools})
        
        missing_tools = [tool for tool in required_tools if tool not in AVAILABLE_COOKWARE]
        can_cook = len(missing_tools) == 0
        
        return {
            "can_cook": can_cook,
            "missing_tools": missing_tools,
            "explanation": f"User {'has' if can_cook else 'is missing'} all required tools."
        }

    async def _arun(self, required_tools: List[str]) -> Dict[str, Any]:
        """Run the tool asynchronously."""
        # For now, just call the sync version
        return self._run(required_tools)

# Create instances of the tools
validate_query_relevance = ValidateQueryRelevance()
validate_cookware = ValidateCookware() 