from pydantic import BaseModel
from typing import List, Optional


class Message(BaseModel):
    """Individual message in conversation history."""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request schema for /chat endpoint."""
    messages: List[Message]


class Recommendation(BaseModel):
    """Single assessment recommendation."""
    name: str
    url: str
    test_type: str
    description: Optional[str] = None
    skills: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """Response schema for /chat endpoint."""
    reply: str
    recommendations: List[Recommendation] = []
    end_of_conversation: bool = False


class ParsedIntent(BaseModel):
    """Extracted hiring requirements from conversation."""
    role: Optional[str] = None
    experience: Optional[str] = None
    skills: List[str] = []
    traits: List[str] = []
    personality_required: Optional[bool] = None
    raw_context: Optional[str] = None
