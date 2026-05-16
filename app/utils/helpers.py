import json
import os
from typing import Any, List, Dict


def load_json(file_path: str) -> Any:
    """Load JSON file safely."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: Any, file_path: str) -> None:
    """Save data to JSON file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def extract_latest_user_message(messages: List[Dict]) -> str:
    """Extract the latest user message from conversation history."""
    for msg in reversed(messages):
        if msg.get("role") == "user":
            return msg.get("content", "")
    return ""


def extract_conversation_context(messages: List[Dict]) -> str:
    """Build context string from conversation history."""
    context_parts = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        context_parts.append(f"{role}: {content}")
    return "\n".join(context_parts)


def normalize_text(text: str) -> str:
    """Normalize text for comparison."""
    return text.lower().strip()
