import logging
import json
from typing import Any, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("recipe_app")

def log_step(step_name: str, data: Any = None) -> None:
    """Log a step in the processing pipeline."""
    if data:
        if isinstance(data, dict):
            logger.info(f"STEP: {step_name} - {json.dumps(data, indent=2)}")
        else:
            logger.info(f"STEP: {step_name} - {data}")
    else:
        logger.info(f"STEP: {step_name}")

def log_tool_call(tool_name: str, inputs: Dict[str, Any], outputs: Any = None) -> None:
    """Log a tool call with inputs and outputs."""
    logger.info(f"TOOL CALL: {tool_name}")
    logger.info(f"INPUTS: {json.dumps(inputs, indent=2)}")
    if outputs:
        logger.info(f"OUTPUTS: {json.dumps(outputs, indent=2) if isinstance(outputs, dict) else outputs}")
