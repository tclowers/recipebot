import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
SERP_API_KEY = os.getenv("SERP_API_KEY", "")

# Model Configuration
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
TEMPERATURE = 0.2

# Available cooking tools for validation
AVAILABLE_COOKWARE: List[str] = [
    "Spatula",
    "Frying Pan", 
    "Little Pot", 
    "Stovetop", 
    "Whisk",
    "Knife",
    "Ladle",
    "Spoon"
]

# Logging
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t") 