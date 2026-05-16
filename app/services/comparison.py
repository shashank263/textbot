from typing import List, Dict, Optional
import json


class ComparisonService:
    """Handles comparison requests between assessments."""
    
    def __init__(self, processed_catalog_path: str = "data/processed_catalog.json"):
        self.catalog = self._load_catalog(processed_catalog_path)
    
    def _load_catalog(self, path: str) -> List[Dict]:
        """Load processed catalog."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return []
    
    def extract_comparison_intent(self, message: str) -> Optional[tuple]:
        """
        Detect if user wants to compare assessments.
        
        Returns: (assessment_name_1, assessment_name_2) or None
        """
        message_lower = message.lower()
        
        # Look for comparison patterns
        patterns = [
            r"(?:compare|difference|vs|versus).*?(\w+.*?)\s+(?:and|with|vs|versus)\s+(\w+.*?)(?:\?|$)",
            r"(?:what.*?difference).*?(\w+.*?)\s+and\s+(\w+.*?)(?:\?|$)",
        ]
        
        for pattern in patterns:
            import re
            match = re.search(pattern, message_lower)
            if match:
                return (match.group(1).strip(), match.group(2).strip())
        
        return None
    
    def find_assessment_by_name(self, name: str) -> Optional[Dict]:
        """Find assessment in catalog by name (fuzzy match)."""
        name_lower = name.lower()
        
        for assessment in self.catalog:
            if name_lower in assessment.get("name", "").lower():
                return assessment
        
        return None
    
    def compare(self, name1: str, name2: str) -> str:
        """
        Compare two assessments.
        
        Returns formatted comparison text.
        """
        assessment1 = self.find_assessment_by_name(name1)
        assessment2 = self.find_assessment_by_name(name2)
        
        if not assessment1 or not assessment2:
            missing = []
            if not assessment1:
                missing.append(name1)
            if not assessment2:
                missing.append(name2)
            return f"I couldn't find the following assessment(s): {', '.join(missing)}. Please check the names."
        
        comparison = self._format_comparison(assessment1, assessment2)
        return comparison
    
    def _format_comparison(self, a1: Dict, a2: Dict) -> str:
        """Format comparison as readable text."""
        lines = []
        
        lines.append(f"## Comparison: {a1.get('name')} vs {a2.get('name')}")
        lines.append("")
        
        # Duration
        d1 = a1.get("duration")
        d2 = a2.get("duration")
        lines.append("### Duration")
        lines.append(f"- {a1.get('name')}: {d1} minutes" if d1 else f"- {a1.get('name')}: Not specified")
        lines.append(f"- {a2.get('name')}: {d2} minutes" if d2 else f"- {a2.get('name')}: Not specified")
        lines.append("")
        
        # Test Type
        type_map = {"P": "Personality", "K": "Knowledge", "A": "Ability", "S": "Situational Judgment"}
        t1 = type_map.get(a1.get("test_type"), a1.get("test_type"))
        t2 = type_map.get(a2.get("test_type"), a2.get("test_type"))
        lines.append("### Test Type")
        lines.append(f"- {a1.get('name')}: {t1}")
        lines.append(f"- {a2.get('name')}: {t2}")
        lines.append("")
        
        # Skills
        s1 = a1.get("skills", [])
        s2 = a2.get("skills", [])
        lines.append("### Skills Measured")
        lines.append(f"- {a1.get('name')}: {', '.join(s1) if s1 else 'N/A'}")
        lines.append(f"- {a2.get('name')}: {', '.join(s2) if s2 else 'N/A'}")
        lines.append("")
        
        # Level
        l1 = a1.get("level", "All")
        l2 = a2.get("level", "All")
        lines.append("### Suitability Level")
        lines.append(f"- {a1.get('name')}: {l1}")
        lines.append(f"- {a2.get('name')}: {l2}")
        lines.append("")
        
        # Description
        lines.append("### Description")
        lines.append(f"- **{a1.get('name')}**: {a1.get('description', 'No description')}")
        lines.append(f"- **{a2.get('name')}**: {a2.get('description', 'No description')}")
        
        return "\n".join(lines)
