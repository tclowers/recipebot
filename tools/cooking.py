from typing import Dict, Any
from langchain_core.tools import tool
from utils.logging_utils import log_tool_call
from utils.llm_utils import get_llm
from config import AVAILABLE_COOKWARE
from langchain_core.messages import HumanMessage, SystemMessage

@tool
def extract_required_cookware(recipe: str) -> Dict[str, Any]:
    """
    Extracts the required cookware needed to prepare a given recipe.
    
    Args:
        recipe: The recipe text
    
    Returns:
        Dict with required cookware
    """
    log_tool_call("extract_required_cookware", {"recipe": recipe})
    
    # Get LLM instance
    llm = get_llm()
    
    # Create messages for the LLM
    messages = [
        SystemMessage(content="""
        You are a helpful cooking assistant that specializes in analyzing recipes.
        Given a recipe text, identify all the cookware/tools needed to prepare it.
        Return ONLY cookware items (pots, pans, utensils, etc.), not ingredients or appliances.
        Be specific but concise in your identification.
        """),
        HumanMessage(content=f"""
        Based on this recipe, what cookware is required to prepare it?
        
        RECIPE:
        {recipe}
        
        List only the cookware items, one per line. Do not include ingredients or explanations.
        """)
    ]
    
    # Call the LLM
    response = llm.invoke(messages)
    
    # Parse the response to extract cookware items
    cookware_text = response.content.strip()
    cookware_list = [item.strip() for item in cookware_text.split('\n') if item.strip()]
    
    # Check if any of the required cookware matches our available cookware list
    # This is for normalization, as the LLM might use slightly different terminology
    normalized_cookware = []
    for item in cookware_list:
        # Simple normalization - you might want to enhance this with more sophisticated matching
        normalized_item = item.lower()
        for available in AVAILABLE_COOKWARE:
            if available.lower() in normalized_item or normalized_item in available.lower():
                normalized_cookware.append(available)
                break
        else:
            # If no match found, keep the original
            normalized_cookware.append(item)
    
    return {
        "required_cookware": normalized_cookware,
        "raw_identified_items": cookware_list,
        "explanation": f"Based on the recipe, these {len(normalized_cookware)} tools are needed."
    } 