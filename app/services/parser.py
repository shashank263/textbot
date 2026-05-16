import re
from typing import List, Dict, Optional
from app.models.schemas import ParsedIntent


class RequirementParser:
    """Extracts structured hiring requirements from conversation history."""
    
    # Keywords for experience levels
    SENIORITY_KEYWORDS = {
        "junior": ["junior", "entry", "entry-level", "graduate", "fresh"],
        "mid": ["mid", "mid-level", "intermediate", "experienced", "3-5 years"],
        "senior": ["senior", "lead", "principal", "expert", "10+ years"],
        "manager": ["manager", "lead", "director", "head", "chief"]
    }
    
    # Common role keywords
    ROLE_KEYWORDS = {
        "developer": ["developer", "engineer", "programmer", "dev", "coder"],
        "frontend": ["frontend", "front-end", "ui", "web", "react", "angular"],
        "backend": ["backend", "back-end", "server", "api", "microservice"],
        "fullstack": ["fullstack", "full-stack", "full stack"],
        "devops": ["devops", "dev-ops", "infrastructure", "deployment"],
        "qa": ["qa", "quality", "tester", "test automation"],
        "data": ["data scientist", "data engineer", "ml engineer", "machine learning"],
        "manager": ["manager", "lead", "director", "coordinator"],
    }
    
    # Personality and trait keywords
    TRAIT_KEYWORDS = {
        "communication": ["communication", "interpersonal", "soft skills", "speaking"],
        "leadership": ["leadership", "managing", "team lead", "mentor"],
        "problem_solving": ["problem solving", "analytical", "critical thinking"],
        "creativity": ["creative", "innovation", "design thinking"],
        "stakeholder": ["stakeholder", "client-facing", "presentation"],
    }
    
    def __init__(self):
        pass
    
    def parse(self, messages: List[Dict]) -> ParsedIntent:
        """
        Extract hiring requirements from conversation.
        
        Returns ParsedIntent with structured data.
        """
        context = self._build_context(messages)
        
        parsed = ParsedIntent(
            role=self._extract_role(context),
            experience=self._extract_experience(context),
            skills=self._extract_skills(context),
            traits=self._extract_traits(context),
            personality_required=self._check_personality_required(context),
            raw_context=context
        )
        
        return parsed
    
    def _build_context(self, messages: List[Dict]) -> str:
        """Combine all messages into single text."""
        parts = []
        for msg in messages:
            content = msg.get("content", "")
            if content:
                parts.append(content)
        return " ".join(parts).lower()
    
    def _extract_role(self, context: str) -> Optional[str]:
        """Extract job role from context."""
        # Look for role keywords
        for role, keywords in self.ROLE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context:
                    # Extract the noun/phrase around the keyword
                    return role.title()
        
        # Try to extract custom role (e.g., "hiring for java developer")
        hiring_pattern = r"hiring (?:for |a |an )?([a-z\s]+?)(?:\s(?:developer|engineer|role|position)|$)"
        match = re.search(hiring_pattern, context)
        if match:
            return match.group(1).title()
        
        return None
    
    def _extract_experience(self, context: str) -> Optional[str]:
        """Extract experience level from context."""
        for level, keywords in self.SENIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context:
                    return level.title()
        return None
    
    def _extract_skills(self, context: str) -> List[str]:
        """Extract technical skills from context."""
        skills = []
        
        # Common technical skills
        common_skills = [
            "java", "python", "javascript", "typescript", "go", "rust", "c++",
            "sql", "nosql", "mongodb", "postgres", "mysql",
            "react", "angular", "vue", "node", "express", "spring boot",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform",
            "git", "linux", "rest api", "graphql", "microservices",
            "html", "css", "webpack", "docker", "ci/cd"
        ]
        
        for skill in common_skills:
            if skill in context:
                skills.append(skill.upper())
        
        return list(set(skills))  # Remove duplicates
    
    def _extract_traits(self, context: str) -> List[str]:
        """Extract soft skills and traits."""
        traits = []
        
        for trait, keywords in self.TRAIT_KEYWORDS.items():
            for keyword in keywords:
                if keyword in context:
                    traits.append(trait)
                    break  # Each trait once
        
        return list(set(traits))
    
    def _check_personality_required(self, context: str) -> Optional[bool]:
        """Determine if personality assessment is needed."""
        personality_indicators = [
            "personality", "culture fit", "soft skills", "team fit",
            "interpersonal", "communication", "leadership", "management"
        ]
        
        for indicator in personality_indicators:
            if indicator in context:
                return True
        
        return None
    
    def needs_clarification(self, parsed: ParsedIntent) -> bool:
        """Determine if we need to ask clarification questions."""
        # Need clarification if role or experience is missing
        return parsed.role is None or parsed.experience is None
    
    def suggest_clarification_questions(self, parsed: ParsedIntent) -> List[str]:
        """Suggest follow-up questions based on what's missing."""
        questions = []
        
        if not parsed.role:
            questions.append("What type of role are you hiring for? (e.g., Java Developer, Data Scientist, QA Engineer)")
        
        if not parsed.experience:
            questions.append("What experience level? (Junior, Mid-level, Senior, or Manager)")
        
        if not parsed.skills or len(parsed.skills) < 2:
            questions.append("What specific technical skills are important for this role?")
        
        return questions
