import json
from typing import List, Dict, Any, TypedDict

from langchain.tools.render import format_tool_to_openai_function
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from utils.llm_utils import get_llm

from config import MODEL_NAME, TEMPERATURE, AVAILABLE_COOKWARE
from tools.validation import validate_query_relevance, validate_cookware
from tools.search import search_recipes, search_cooking_question
from tools.cooking import extract_required_cookware
from utils.logging_utils import log_step, logger

# Define all available tools
tools = [
    validate_query_relevance,
    validate_cookware,
    search_recipes,
    search_cooking_question,
    extract_required_cookware
]

# Format tools for OpenAI function calling
tool_map = {
    tool.name: tool
    for tool in tools
}

# Set up the LLM with function calling 
llm = get_llm()

# Define the state for our graph
class GraphState(TypedDict):
    query: str
    messages: List[BaseMessage]
    debug_info: Dict[str, Any]
    # relevant is only needed for the initial classification
    relevant: bool

# Define a custom tool executor function
def execute_tool(tool_name: str, tool_input: Dict[str, Any]) -> Any:
    """Execute a tool with the given input."""
    log_step(f"Executing tool: {tool_name}", tool_input)
    if tool_name in tool_map:
        # Use the new .invoke() method instead of calling the tool directly
        return tool_map[tool_name].invoke(tool_input)
    else:
        raise ValueError(f"Tool {tool_name} not found. Available tools: {list(tool_map.keys())}")

# System prompt
system_prompt = f"""You are a helpful cooking assistant that specializes in recipes, cooking techniques, and food preparation.

Available Cookware:
{json.dumps(AVAILABLE_COOKWARE, indent=2)}

Follow these guidelines:
1. ONLY answer queries related to cooking, recipes, or food. Politely refuse any off-topic questions.
2. For recipe requests, consider if research is needed.
3. For recipes, always check if the user has the required cookware.
4. When providing recipes, include ingredients, steps, and cooking times.
5. When answering cooking questions, be detailed and educational.

IMPORTANT: You will have access to various tools. Call these tools ONLY when necessary:
- validate_query_relevance: To check if a query is cooking-related
- search_recipes: When you need to find specific recipes
- search_cooking_question: For general cooking information
- extract_required_cookware: To determine what cookware is needed for a recipe
- validate_cookware: To check if the user has the necessary cookware

Always make tool decisions based on the specific query and what information you need.
"""

# Node functions
def classify(state: GraphState) -> Dict[str, Any]:
    """Determine if the query is relevant and route accordingly."""
    log_step("classify")
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=state["query"]),
        AIMessage(content=(
            "Is this query related to cooking, recipes, or food preparation? "
            "Respond in only one word, with RELEVANT or NOT"
        ))
    ]
    
    # Single LLM call to determine relevance
    response = llm.invoke(messages)
    log_step("LLM classification response", response.content)
    
    # More robust relevance check
    is_relevant = "RELEVANT" in response.content.upper()
    
    return {
        "messages": messages + [response],
        "relevant": is_relevant,
        "debug_info": {"relevance_check": {
            "relevant": is_relevant,
            "explanation": response.content
        }}
    }

def search(state: GraphState) -> Dict[str, Any]:
    """Search for relevant information or identify next step."""
    log_step("search")
    
    messages = state["messages"]
    debug_info = state.get("debug_info", {})
    relevant = state.get("relevant", False)  # Preserve the relevant flag
    
    # Prepare tools for this stage
    available_tools = [
        search_recipes,
        search_cooking_question
    ]
    
    # Ask LLM what tool to use or if we can skip to next step
    response = llm.invoke(
        messages + [
            AIMessage(
                content="I need to determine if I should search for information or can proceed with what I know."
            )
        ]
    )
    
    messages.append(response)
    
    # Format tools for function calling
    response = llm.invoke(
        messages,
        functions=[format_tool_to_openai_function(t) for t in available_tools]
    )
    
    # Check if a function was called
    function_call = response.additional_kwargs.get("function_call", None)
    
    if function_call:
        # Execute tool
        action = json.loads(function_call["arguments"])
        function_name = function_call["name"]
        
        tool_result = execute_tool(function_name, action)
        
        # Add results to messages
        messages.append(response)
        messages.append(
            AIMessage(
                content=f"Tool result: {json.dumps(tool_result, indent=2)}"
            )
        )
        
        # Update debug info
        debug_info = state["debug_info"].copy()
        debug_info["search"] = {
            "tool": function_name,
            "result": tool_result
        }
        
        return {
            "messages": messages,
            "debug_info": debug_info,
            "relevant": relevant  # Return the preserved relevant flag
        }
    else:
        # No tool was called, just update messages
        messages.append(response)
        
        return {
            "messages": messages,
            "debug_info": debug_info,
            "relevant": relevant  # Return the preserved relevant flag
        }

def identify_tools(state: GraphState) -> Dict[str, Any]:
    """Identify what cookware is needed for the recipe."""
    log_step("identify_tools")
    
    messages = state["messages"]
    debug_info = state.get("debug_info", {})
    relevant = state.get("relevant", False)  # Preserve the relevant flag
    
    # Ask LLM if we need to extract required tools
    response = llm.invoke(
        messages + [
            AIMessage(
                content="I need to determine if I should extract required cookware for a recipe."
            )
        ]
    )
    
    messages.append(response)
    
    # Format tool for function calling
    response = llm.invoke(
        messages,
        functions=[format_tool_to_openai_function(extract_required_cookware)]
    )
    
    # Check if a function was called
    function_call = response.additional_kwargs.get("function_call", None)
    
    if function_call:
        # Execute tool
        action = json.loads(function_call["arguments"])
        function_name = function_call["name"]
        
        tool_result = execute_tool(function_name, action)
        
        # Add results to messages
        messages.append(response)
        messages.append(
            AIMessage(
                content=f"Tool result: {json.dumps(tool_result, indent=2)}"
            )
        )
        
        # Update debug info
        debug_info = state["debug_info"].copy()
        debug_info["tools"] = {
            "required_cookware": tool_result.get("required_cookware", [])
        }
        
        return {
            "messages": messages,
            "debug_info": debug_info,
            "relevant": relevant  # Return the preserved relevant flag
        }
    else:
        # No tool was called
        messages.append(response)
        
        return {
            "messages": messages,
            "debug_info": debug_info,
            "relevant": relevant  # Return the preserved relevant flag
        }

def validate_cooking(state: GraphState) -> Dict[str, Any]:
    """Validate if the user has the required cookware."""
    log_step("validate_cooking")
    
    messages = state["messages"]
    debug_info = state.get("debug_info", {})
    relevant = state.get("relevant", False)  # Preserve the relevant flag
    
    required_cookware = state["debug_info"].get("tools", {}).get("required_cookware", [])
    
    # If we have required cookware, validate it
    if required_cookware:
        # Format tool for function calling
        response = llm.invoke(
            messages,
            functions=[format_tool_to_openai_function(validate_cookware)]
        )
        
        # Check if a function was called
        function_call = response.additional_kwargs.get("function_call", None)
        
        if function_call:
            # Execute tool
            function_name = function_call["name"]
            
            tool_result = execute_tool(function_name, {"required_tools": required_cookware})
            
            # Add results to messages
            messages.append(response)
            messages.append(
                AIMessage(
                    content=f"Tool result: {json.dumps(tool_result, indent=2)}"
                )
            )
            
            # Update debug info
            debug_info["cookware_validation"] = tool_result
    
    return {
        "messages": messages,
        "debug_info": debug_info,
        "relevant": relevant  # Return the preserved relevant flag
    }

def respond(state: GraphState) -> Dict[str, Any]:
    """Generate the final response."""
    log_step("respond")
    
    messages = state["messages"]
    debug_info = state.get("debug_info", {})
    relevant = state.get("relevant", False)  # Preserve the relevant flag
    
    # If we reached this node through the non-relevant path, provide a clear cooking-focused refusal
    if relevant is False:
        response = llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state["query"]),
                AIMessage(content="""
                This query is NOT about cooking. I must respond with:
                
                "I am a cooking assistant that specializes in recipes, cooking techniques, and food preparation. 
                I cannot help with questions about cars, technology, or other non-cooking topics. 
                Please feel free to ask me anything about cooking, recipes, or food preparation!"
                """)
            ]
        )
    else:
        # We reached this node through the normal path, generate a detailed response
        response = llm.invoke(
            messages + [
                AIMessage(
                    content="I'll now provide a detailed response to this cooking query based on all the information gathered."
                )
            ]
        )
    
    # Add the final response to messages
    messages.append(response)
    
    return {
        "messages": messages,
        "debug_info": debug_info,
        "relevant": relevant  # Return the preserved relevant flag
    }

# Router function for conditional transitions
def router(state: GraphState) -> str:
    """Determine the next node based on the current state."""
    if not state["relevant"]:
        return "respond"
    
    if "tools" in state["debug_info"] and state["debug_info"]["tools"].get("required_cookware"):
        return "validate_cookware"
    
    return "identify_tools"

# Build the graph
def build_recipe_graph():
    """Build and return the recipe graph."""
    # Create the graph builder
    builder = StateGraph(GraphState)
    
    # Add nodes
    builder.add_node("classify", classify)
    builder.add_node("search", search)
    builder.add_node("identify_tools", identify_tools)
    builder.add_node("validate_cookware", validate_cooking)
    builder.add_node("respond", respond)
    
    # Add edges
    builder.add_edge(START, "classify")
    builder.add_conditional_edges(
        "classify",
        lambda state: "respond" if not state["relevant"] else "search"
    )
    builder.add_edge("search", "identify_tools")
    builder.add_conditional_edges(
        "identify_tools",
        lambda state: "validate_cookware" if "tools" in state["debug_info"] and state["debug_info"]["tools"].get("required_cookware") else "respond"
    )
    builder.add_edge("validate_cookware", "respond")
    builder.add_edge("respond", END)
    
    # Compile the graph
    return builder.compile()

# Create an instance of the graph
recipe_graph = build_recipe_graph()

# Function to process a query
async def process_query(query: str) -> Dict[str, Any]:
    """Process a user query through the recipe graph."""
    log_step("process_query", {"query": query})
    
    initial_state = {
        "query": query,
        "messages": [],
        "debug_info": {},
        "relevant": False
    }
    
    try:
        final_state = None
        for output in recipe_graph.stream(initial_state):
            final_state = output
        
        # Extract the nested state if present
        if final_state and "respond" in final_state:
            final_state = final_state["respond"]
        
        # Determine if query was relevant
        is_relevant = False
        if final_state and "debug_info" in final_state and "relevance_check" in final_state["debug_info"]:
            is_relevant = final_state["debug_info"]["relevance_check"].get("relevant", False)
        elif final_state and "relevant" in final_state:
            is_relevant = final_state["relevant"]
            
        if final_state and "messages" in final_state:
            messages = final_state["messages"]
            last_message = messages[-1] if messages else None
            
            return {
                "response": last_message.content if hasattr(last_message, "content") else "No response generated",
                "relevant": is_relevant,
                "debug_info": final_state.get("debug_info")
            }
        
        return {
            "response": "I am a cooking assistant and can only help with cooking-related questions.",
            "relevant": False,
            "debug_info": None
        }
    except Exception as e:
        logger.exception(f"Error in process_query: {str(e)}")
        return {
            "response": f"An error occurred: {str(e)}",
            "relevant": False,
            "debug_info": {"error": str(e)}
        } 