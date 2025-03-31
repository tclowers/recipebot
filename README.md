# RecipeBot

A cooking assistant chatbot built with LangChain and LangGraph that helps users find recipes, identifies required cookware, and answers cooking-related questions.

## Local Setup

### Prerequisites
- Python 3.10+
- OpenAI API key
- SERP API key

### Environment Setup
1. Clone the repository:
   ```
   git clone https://github.com/tclowers/recipebot.git
   cd recipebot
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   export OPENAI_API_KEY=your_openai_api_key
   export SERP_API_KEY=your_serp_api_key  # Optional
   ```

## Running the Application

### Without Docker
uvicorn main:app --reload --host 0.0.0.0 --port 8000

### With Docker
docker build -t recipebot .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_openai_api_key -e SERP_API_KEY=your_serp_api_key recipebot

## Usage Examples

### Example Queries
Test the API with the following curl commands:

1. Recipe search:
```
curl -X 'POST' \
  'http://localhost:8000/api/query' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "How do I make chicken soup with the cookware I have?"
  }'
```

2. Cooking technique question:
```
curl -X 'POST' \
  'http://localhost:8000/api/query' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What is the best way to cook rice?"
  }'
```

3. Recipe using too many peices of cookware that are not available:
```
curl -X 'POST' \
  'http://localhost:8000/api/query' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "How do I bake a traditional chocolate cake with the cookware I have?"
  }'
```

4. Non-cooking query (should be refused):
```
curl -X 'POST' \
  'http://localhost:8000/api/query' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "How do I fix my car?"
  }'
```

## AWS Deployment Plan

### Architecture
- **Container Orchestration**: Amazon ECS with Fargate for serverless container management
- **API Exposure Options**:
  - **API Gateway**: For advanced features like rate limiting, authentication, and caching
  - **Application Load Balancer (ALB)**: For simpler deployments with basic traffic routing
- **Secret Management**: AWS Secrets Manager for API keys and credentials (best for Prod, most
  smaller apps use environment variables on the container)
- **Monitoring**: CloudWatch for logs and metrics (once again, best for Prod and large teams)

### Deployment Steps
1. Create an ECR repository and push the Docker image
2. Set up ECS cluster with Fargate
3. Configure API Gateway/ALB with proper routes
4. Store secrets in AWS Secrets Manager
5. Set up CloudWatch Logs and Metrics

## Authentication & Security

### User Authentication
- Implement JWT-based authentication using an IDP such as Amazon Cognito, Clerk, or Auth0

## Trade-offs & Next Steps

### Current Limitations
- Limited error handling for edge cases
- No persistence for chat history
- SERP API has query limits and could be expensive at scale
- Mock responses for when API integration fails

### Future Improvements
- A front-end would greatly enhance user experience
- Add database integration for user preferences and history
- Add support for dietary restrictions and allergies

### Edge Cases
- The bot is pretty creative in trying to create a recipie that employs the limited
  cookware specified, but it will reject more specific requests ("Bake a traditional cake")

