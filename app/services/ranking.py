from typing import List, Dict, Tuple
from app.models.schemas import ParsedIntent, Recommendation
import re


class RankingService:
    """Ranks retrieved assessments based on relevance."""
    
    def rank_assessments(self,
                        assessments: List[Dict],
                        parsed_intent: ParsedIntent,
                        similarity_scores: List[float]) -> List[Tuple[Dict, float]]:
        """
        Rank assessments using multi-factor scoring.
        
        Score = 0.5 * similarity + 0.3 * skill_overlap + 0.2 * role_match
        
        Returns: List of (assessment, score) tuples, sorted by score descending.
        """
        ranked = []
        
        for i, assessment in enumerate(assessments):
            similarity_score = similarity_scores[i] if i < len(similarity_scores) else 0.0
            
            # Normalize similarity to 0-1 range (assuming L2 distance, invert for similarity)
            # FAISS returns distances, closer = better, so invert
            similarity = 1.0 / (1.0 + similarity_score)
            
            skill_overlap = self._calculate_skill_overlap(assessment, parsed_intent)
            role_match = self._calculate_role_match(assessment, parsed_intent)
            
            # Weighted score
            score = (0.5 * similarity + 
                    0.3 * skill_overlap + 
                    0.2 * role_match)
            
            ranked.append((assessment, score))
        
        # Sort by score descending
        ranked.sort(key=lambda x: x[1], reverse=True)
        
        return ranked
    
    def _calculate_skill_overlap(self, assessment: Dict, intent: ParsedIntent) -> float:
        """
        Calculate overlap between assessment skills and user's required skills.
        
        Returns value between 0 and 1.
        """
        if not intent.skills:
            return 0.5  # Neutral if no skills specified
        
        assessment_skills = set(s.lower() for s in assessment.get("skills", []))
        required_skills = set(s.lower() for s in intent.skills)
        
        if not assessment_skills or not required_skills:
            return 0.5
        
        intersection = len(assessment_skills & required_skills)
        union = len(assessment_skills | required_skills)
        
        if union == 0:
            return 0.5
        
        return intersection / union
    
    def _calculate_role_match(self, assessment: Dict, intent: ParsedIntent) -> float:
        """
        Calculate role match based on name, description, and test type.
        
        Returns value between 0 and 1.
        """
        if not intent.role:
            return 0.5
        
        role_lower = intent.role.lower()
        name_lower = assessment.get("name", "").lower()
        desc_lower = assessment.get("description", "").lower()
        
        # Check for direct role mention
        if role_lower in name_lower or role_lower in desc_lower:
            return 1.0
        
        # Check for partial matches
        role_parts = role_lower.split()
        matches = 0
        for part in role_parts:
            if part in name_lower or part in desc_lower:
                matches += 1
        
        if matches > 0:
            return matches / len(role_parts) if role_parts else 0.5
        
        # Check test type alignment with personality requirement
        if intent.personality_required and assessment.get("test_type") == "P":
            return 0.8
        
        return 0.5
    
    def remove_duplicates(self, ranked: List[Tuple[Dict, float]]) -> List[Tuple[Dict, float]]:
        """Remove duplicate assessments, keeping highest score."""
        seen = set()
        unique = []
        
        for assessment, score in ranked:
            name = assessment.get("name", "")
            if name not in seen:
                seen.add(name)
                unique.append((assessment, score))
        
        return unique
    
    def filter_low_scoring(self, 
                          ranked: List[Tuple[Dict, float]], 
                          min_score: float = 0.3) -> List[Tuple[Dict, float]]:
        """Remove assessments below minimum score threshold."""
        return [item for item in ranked if item[1] >= min_score]
