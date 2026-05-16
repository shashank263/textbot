from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="TestBot - SHL Assessment Recommendation Chatbot",
    description="AI-powered conversational assessment recommendation system",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize app on startup."""
    print("Starting TestBot...")
    # Import here to ensure models are ready
    from app.routes import chat
    print("Chat routes loaded")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TestBot",
        "version": "1.0.0"
    }


# Include routers
from app.routes import chat as chat_router

app.include_router(chat_router.router)


if __name__ == "__main__":
    import uvicorn
    
    # Check if Ollama is available (optional warning)
    from app.services.llm_service import LLMService
    llm = LLMService()
    if not llm.is_available():
        print("WARNING: Ollama service not available at http://localhost:11434")
        print("Some features may be limited. Start Ollama with: ollama serve")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
