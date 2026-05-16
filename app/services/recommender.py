from typing import List, Dict, Tuple
from app.models.schemas import Recommendation


class RecommenderService:
    """Creates final recommendation shortlist."""
    
    def create_recommendations(self,
                             ranked_assessments: List[Tuple[Dict, float]],
                             max_recommendations: int = 5) -> List[Recommendation]:
        """
        Convert ranked assessments to Recommendation objects.
        
        Returns top N recommendations with URLs and test types.
        """
        recommendations = []
        
        for assessment, score in ranked_assessments[:max_recommendations]:
            rec = Recommendation(
                name=assessment.get("name", "Unknown"),
                url=assessment.get("url", ""),
                test_type=assessment.get("test_type", "O"),
                description=assessment.get("description", ""),
                skills=assessment.get("skills", [])
            )
            
            # Only include if URL exists (ensure from catalog)
            if rec.url:
                recommendations.append(rec)
        
        return recommendations
    
    def format_recommendations_text(self, 
                                   recommendations: List[Recommendation]) -> str:
        """Format recommendations as human-readable text."""
        if not recommendations:
            return "No suitable assessments found. Could you provide more details?"
        
        lines = ["Based on your requirements, I recommend:"]
        
        for i, rec in enumerate(recommendations, 1):
            test_type_name = self._get_test_type_name(rec.test_type)
            lines.append(f"\n{i}. **{rec.name}** ({test_type_name})")
            if rec.description:
                lines.append(f"   {rec.description}")
            if rec.skills:
                lines.append(f"   Skills: {', '.join(rec.skills)}")
        
        return "\n".join(lines)
    
    def _get_test_type_name(self, test_type: str) -> str:
        """Convert test type code to readable name."""
        mapping = {
            "P": "Personality",
            "K": "Knowledge",
            "A": "Ability/Reasoning",
            "S": "Situational Judgment",
            "O": "Other"
        }
        return mapping.get(test_type, "Unknown")
    
    def validate_catalog_only(self, recommendations: List[Recommendation]) -> bool:
        """Validate that all recommendations have URLs (from catalog)."""
        return all(rec.url for rec in recommendations)
