from langchain_openai import ChatOpenAI
from config import MODEL_NAME, TEMPERATURE

def get_llm(temperature: float = TEMPERATURE, model: str = MODEL_NAME) -> ChatOpenAI:
    """
    Returns a configured ChatOpenAI instance.
    
    Args:
        temperature: The sampling temperature to use. Defaults to 0.0 for deterministic results.
        model: The model to use. Defaults to the model specified in config.py.
    
    Returns:
        ChatOpenAI: A configured instance of the ChatOpenAI class.
    """
    return ChatOpenAI(
        model=model,
        temperature=temperature
    ) 