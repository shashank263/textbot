from typing import Tuple


class GuardrailsService:
    """Protects chatbot scope and prevents off-topic requests."""
    
    # Off-topic keywords that should trigger refusal
    OFF_TOPIC_KEYWORDS = [
        "salary", "wage", "compensation", "pay", "bonus",
        "legal", "law", "court", "lawsuit", "attorney",
        "medical", "health", "doctor", "hospital", "medicine",
        "political", "politics", "election", "vote",
        "religion", "god", "prayer", "faith",
        "invest", "stock", "bitcoin", "crypto", "trading",
        "adult", "nsfw", "explicit", "porn",
    ]
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        "forget", "ignore", "forget your", "ignore your", "previous instruction",
        "system prompt", "sys prompt", "admin", "administrator",
        "jailbreak", "bypass", "override", "ignore all",
    ]
    
    # SHL-related keywords (allowed topics)
    SHL_KEYWORDS = [
        "assessment", "test", "shl", "recommendation", "evaluate",
        "screening", "hire", "recruitment", "candidate", "verify",
        "ability", "personality", "situational", "knowledge",
    ]
    
    def check_safety(self, message: str) -> Tuple[bool, str]:
        """
        Check if message is safe and on-topic.
        
        Returns: (is_safe, reason)
        - is_safe=True: proceed normally
        - is_safe=False: reject with reason
        """
        message_lower = message.lower()
        
        # Check for prompt injection
        for pattern in self.INJECTION_PATTERNS:
            if pattern in message_lower:
                return False, "I detected an attempt to modify my behavior. I'm designed specifically to help with SHL assessment recommendations."
        
        # Check for off-topic content
        for keyword in self.OFF_TOPIC_KEYWORDS:
            if keyword in message_lower:
                return False, f"I can't assist with {keyword}. I'm specialized in SHL assessment recommendations."
        
        # Check if message is about SHL or hiring
        is_shl_related = any(kw in message_lower for kw in self.SHL_KEYWORDS)
        
        # Allow if:
        # 1. Message contains SHL keywords, or
        # 2. Message mentions hiring/roles/skills (assessment-related), or
        # 3. Message asks for clarification about the system
        has_hiring_context = any(kw in message_lower for kw in [
            "hire", "hiring", "recruit", "developer", "engineer",
            "role", "position", "candidate", "interview", "skill",
            "experience", "requirement", "criteria",
        ])
        
        is_clarification = any(kw in message_lower for kw in [
            "what can", "what do", "how does", "how can", "help", "capability",
            "feature", "support",
        ])
        
        if is_shl_related or has_hiring_context or is_clarification:
            return True, ""
        
        # Ambiguous - allow but may ask for clarification
        return True, ""
    
    def is_comparison_request(self, message: str) -> bool:
        """Detect if user is asking for assessment comparison."""
        message_lower = message.lower()
        comparison_keywords = ["compare", "difference", "vs", "versus", "between"]
        return any(kw in message_lower for kw in comparison_keywords)
    
    def is_refinement(self, previous_intent, new_message: str) -> bool:
        """
        Detect if user is refining a previous recommendation.
        
        Refinement = changing requirements in context of a previous recommendation.
        """
        message_lower = new_message.lower()
        
        # Refinement keywords
        refinement_keywords = [
            "actually", "wait", "also", "instead", "but", "however",
            "what if", "how about", "maybe", "let's", "let me"
        ]
        
        return any(kw in message_lower for kw in refinement_keywords)
    
    def generate_refusal(self, reason: str) -> str:
        """Generate a polite refusal message."""
        default = "I can only assist with SHL assessment recommendations. How can I help with your assessment needs?"
        return reason if reason else default
