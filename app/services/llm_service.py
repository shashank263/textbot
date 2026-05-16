import requests
import json
from typing import Optional, List


class LLMService:
    """
    Handles Ollama + llama3 interaction.
    
    Used for:
    - Clarification question generation
    - Conversational replies
    - Extraction assistance
    
    NOT used for final recommendations (those come from retrieval system).
    """
    
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
    
    def is_available(self) -> bool:
        """Check if Ollama service is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate response from llama3.
        
        Args:
            prompt: The prompt to send to the model
            temperature: Creativity level (0.0-1.0)
        
        Returns:
            Generated text response
        """
        if not self.is_available():
            return self._get_fallback_response(prompt)
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "stream": False,
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return self._get_fallback_response(prompt)
                
        except Exception as e:
            print(f"LLM error: {e}")
            return self._get_fallback_response(prompt)
    
    def generate_clarification_questions(self, 
                                        parsed_intent,
                                        conversation_context: str) -> List[str]:
        """
        Generate clarification questions based on parsed intent.
        """
        missing_fields = []
        
        if not parsed_intent.role:
            missing_fields.append("role")
        if not parsed_intent.experience:
            missing_fields.append("experience level")
        if not parsed_intent.skills or len(parsed_intent.skills) < 2:
            missing_fields.append("technical skills")
        
        if not missing_fields:
            return []
        
        # Use LLM to generate natural questions, or fallback to templates
        if self.is_available():
            prompt = f"""Generate 2-3 clarification questions for a hiring manager. 
Context: {conversation_context}
Missing information: {', '.join(missing_fields)}

Questions should be specific and concise. Return only the questions, one per line."""
            
            response = self.generate_response(prompt, temperature=0.5)
            questions = [q.strip() for q in response.split('\n') if q.strip()]
            return questions[:3]  # Limit to 3
        else:
            # Fallback templates
            templates = {
                "role": "What type of role are you hiring for? (e.g., Java Developer, Data Scientist)",
                "experience level": "What experience level? (Junior, Mid-level, Senior, or Manager)",
                "technical skills": "What specific technical skills are important? (e.g., Java, Python, SQL)",
            }
            
            questions = [templates.get(field, "") for field in missing_fields]
            return [q for q in questions if q]
    
    def generate_comparison_analysis(self, assessment1: dict, assessment2: dict) -> str:
        """
        Generate natural language comparison between two assessments.
        Uses LLM for conversational tone.
        """
        if not self.is_available():
            return self._format_simple_comparison(assessment1, assessment2)
        
        prompt = f"""Compare these two assessments concisely:

Assessment 1: {assessment1.get('name')}
- Type: {assessment1.get('test_type')}
- Duration: {assessment1.get('duration')} min
- Skills: {', '.join(assessment1.get('skills', []))}
- Description: {assessment1.get('description')}

Assessment 2: {assessment2.get('name')}
- Type: {assessment2.get('test_type')}
- Duration: {assessment2.get('duration')} min
- Skills: {', '.join(assessment2.get('skills', []))}
- Description: {assessment2.get('description')}

Provide a 2-3 sentence comparison highlighting key differences."""
        
        return self.generate_response(prompt, temperature=0.6)
    
    def generate_conversational_reply(self, context: str, recommendations_count: int) -> str:
        """
        Generate a friendly conversational reply to accompany recommendations.
        """
        if not self.is_available():
            return self._get_fallback_intro(recommendations_count)
        
        prompt = f"""You are a helpful hiring assessment assistant. Generate a 1-2 sentence 
introduction to present {recommendations_count} assessment recommendations based on this context:
{context}

Be friendly and specific to their needs."""
        
        return self.generate_response(prompt, temperature=0.7)
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when LLM is unavailable."""
        return "I need more information to provide the best recommendations."
    
    def _get_fallback_intro(self, count: int) -> str:
        """Fallback introduction text."""
        if count == 0:
            return "I couldn't find suitable assessments for your requirements. Could you provide more details?"
        elif count == 1:
            return "Based on your needs, I recommend this assessment:"
        else:
            return f"Based on your requirements, here are {count} suitable assessments:"
    
    def _format_simple_comparison(self, a1: dict, a2: dict) -> str:
        """Simple comparison without LLM."""
        return f"{a1.get('name')} is a {a1.get('test_type')}-type test, " \
               f"while {a2.get('name')} is a {a2.get('test_type')}-type test. " \
               f"They measure different skill sets and durations."
