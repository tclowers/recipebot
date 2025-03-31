from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from config import DEBUG

from models.schemas import QueryRequest, QueryResponse
from graphs.recipe_graph import process_query
from utils.logging_utils import logger

# Initialize FastAPI app
app = FastAPI(
    title="Recipe Chatbot API",
    description="A cooking and recipe Q&A application using LangGraph and LangChain",
    version="0.1.0"
)

# Add CORS middleware - you'll want to tighten this up in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/api/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    Process a cooking or recipe query.
    
    Args:
        request: The query request
        
    Returns:
        Response with cooking/recipe information or a refusal
    """
    try:
        logger.info(f"Received query: {request.query}")
        
        # Process the query through our recipe graph
        result = await process_query(request.query)
        
        # Return the response
        return QueryResponse(
            response=result["response"],
            relevant=result["relevant"],
            debug_info=result["debug_info"] if DEBUG else None
        )
    except Exception as e:
        logger.exception(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

# Health Check endpoint -super useful in deployments
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 