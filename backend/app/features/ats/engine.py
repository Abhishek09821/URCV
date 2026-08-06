"""
ATS Analysis Engine - Real rule-based scoring.

Architectural Decision:
- NOT fake scores - real ATS compatibility checks
- Rule-based system based on actual ATS requirements
- Returns actionable suggestions
- Cached for 24 hours per resume
"""
from typing import Any

from app.core.logging import get_logger
from app.domain.schemas.resume_schema import ResumeJSON

logger = get_logger(__name__)


class ATSAnalyzer:
    """
    ATS compatibility analyzer.
    
    Scoring breakdown (100 points total):
    - Contact Information: 15 points
    - Section Structure: 20 points
    - Formatting: 25 points
    - Keywords: 20 points
    - Readability: 10 points
    - File Structure: 10 points
    """
    
    def analyze(self, resume_json: ResumeJSON) -> dict[str, Any]:
        """
        Analyze resume for ATS compatibility.
        
        Args:
            resume_json: Resume JSON to analyze
            
        Returns:
            Analysis with score, breakdown, and suggestions
        """
        logger.info("Starting ATS analysis")
        
        # Run all checks
        contact_result = self._check_contact_information(resume_json)
        section_result = self._check_section_structure(resume_json)
        format_result = self._check_formatting(resume_json)
        keyword_result = self._check_keywords(resume_json)
        readability_result = self._check_readability(resume_json)
        file_result = self._check_file_structure(resume_json)
        
        # Calculate total score
        total_score = (
            contact_result["score"] +
            section_result["score"] +
            format_result["score"] +
            keyword_result["score"] +
            readability_result["score"] +
            file_result["score"]
        )
        
        # Collect all suggestions
        all_suggestions = []
        all_suggestions.extend(contact_result["suggestions"])
        all_suggestions.extend(section_result["suggestions"])
        all_suggestions.extend(format_result["suggestions"])
        all_suggestions.extend(keyword_result["suggestions"])
        all_suggestions.extend(readability_result["suggestions"])
        all_suggestions.extend(file_result["suggestions"])
        
        return {
            "overall_score": total_score,
            "breakdown": {
                "contact_information": contact_result["score"],
                "section_structure": section_result["score"],
                "formatting": format_result["score"],
                "keywords": keyword_result["score"],
                "readability": readability_result["score"],
                "file_structure": file_result["score"]
            },
            "suggestions": all_suggestions,
            "passed": total_score >= 70  # 70+ is good ATS score
        }
    
    def _check_contact_information(self, resume: ResumeJSON) -> dict[str, Any]:
        """Check contact information (15 points)."""
        score = 0
        suggestions = []
        
        personal = resume.personal
        
        # Email (5 points)
        if personal.email:
            score += 5
        else:
            suggestions.append({
                "category": "contact",
                "priority": "high",
                "message": "Add email address - required by all ATS"
            })
        
        # Phone (5 points)
        if personal.phone:
            score += 5
        else:
            suggestions.append({
                "category": "contact",
                "priority": "high",
                "message": "Add phone number - highly recommended"
            })
        
        # Name (5 points)
        if personal.fullName and personal.fullName != "Unknown":
            score += 5
        else:
            suggestions.append({
                "category": "contact",
                "priority": "critical",
                "message": "Full name is missing or unclear"
            })
        
        return {"score": score, "suggestions": suggestions}
    
    def _check_section_structure(self, resume: ResumeJSON) -> dict[str, Any]:
        """Check section structure (20 points)."""
        score = 0
        suggestions = []
        
        # Education (5 points)
        if resume.education:
            score += 5
        else:
            suggestions.append({
                "category": "sections",
                "priority": "high",
                "message": "Add education section - critical for ATS"
            })
        
        # Experience OR Projects (10 points)
        if resume.experience or resume.projects:
            score += 10
        else:
            suggestions.append({
                "category": "sections",
                "priority": "critical",
                "message": "Add experience or projects section"
            })
        
        # Skills (5 points)
        if resume.skills and (resume.skills.technical or resume.skills.other):
            score += 5
        else:
            suggestions.append({
                "category": "sections",
                "priority": "high",
                "message": "Add skills section with technical skills"
            })
        
        return {"score": score, "suggestions": suggestions}
    
    def _check_formatting(self, resume: ResumeJSON) -> dict[str, Any]:
        """Check formatting compatibility (25 points)."""
        score = 25  # Start with full points, deduct for issues
        suggestions = []
        
        # Check for images/photos (ATS may struggle)
        if resume.meta.detectedLayout and resume.meta.detectedLayout.hasPhoto:
            score -= 5
            suggestions.append({
                "category": "formatting",
                "priority": "medium",
                "message": "Photos may not parse well in ATS - consider removing"
            })
        
        # Multiple columns can confuse ATS
        if resume.meta.detectedLayout and resume.meta.detectedLayout.columns > 1:
            score -= 5
            suggestions.append({
                "category": "formatting",
                "priority": "high",
                "message": "Multi-column layouts can confuse ATS - use single column"
            })
        
        # Check if pages > 2
        if resume.meta.pageCount > 2:
            score -= 3
            suggestions.append({
                "category": "formatting",
                "priority": "low",
                "message": "Resume longer than 2 pages - consider condensing"
            })
        
        # Standard fonts are better
        # (We'd check this in full implementation)
        
        return {"score": max(0, score), "suggestions": suggestions}
    
    def _check_keywords(self, resume: ResumeJSON) -> dict[str, Any]:
        """Check for important keywords (20 points)."""
        score = 0
        suggestions = []
        
        # Check for technical skills
        has_technical_skills = (
            resume.skills and 
            resume.skills.technical and 
            len(resume.skills.technical) > 0
        )
        
        if has_technical_skills:
            skill_count = sum(len(cat.skills) for cat in resume.skills.technical)
            if skill_count >= 10:
                score += 10
            elif skill_count >= 5:
                score += 7
            else:
                score += 4
                suggestions.append({
                    "category": "keywords",
                    "priority": "medium",
                    "message": "Add more technical skills - ATS looks for specific keywords"
                })
        else:
            suggestions.append({
                "category": "keywords",
                "priority": "high",
                "message": "Add technical skills section with specific technologies"
            })
        
        # Check for action verbs in experience/projects
        action_verbs = [
            'developed', 'built', 'created', 'implemented', 'designed',
            'managed', 'led', 'improved', 'increased', 'reduced'
        ]
        
        has_action_verbs = False
        text_to_check = ""
        
        for exp in resume.experience:
            text_to_check += " ".join(exp.responsibilities or [])
            text_to_check += " ".join(exp.achievements or [])
        
        for proj in resume.projects:
            text_to_check += proj.description
            text_to_check += " ".join(proj.highlights or [])
        
        text_lower = text_to_check.lower()
        found_verbs = [verb for verb in action_verbs if verb in text_lower]
        
        if len(found_verbs) >= 5:
            score += 10
        elif len(found_verbs) >= 3:
            score += 6
        else:
            suggestions.append({
                "category": "keywords",
                "priority": "medium",
                "message": f"Use more action verbs (found: {', '.join(found_verbs[:3])})"
            })
            score += 3
        
        return {"score": score, "suggestions": suggestions}
    
    def _check_readability(self, resume: ResumeJSON) -> dict[str, Any]:
        """Check readability (10 points)."""
        score = 10  # Start with full points
        suggestions = []
        
        # Check if using bullet points (look for lists in data)
        has_bullets = False
        if resume.experience:
            has_bullets = any(exp.responsibilities or exp.achievements for exp in resume.experience)
        if resume.projects:
            has_bullets = has_bullets or any(proj.highlights for proj in resume.projects)
        
        if not has_bullets:
            score -= 3
            suggestions.append({
                "category": "readability",
                "priority": "medium",
                "message": "Use bullet points for better readability"
            })
        
        # Check description lengths (not too long)
        for proj in resume.projects:
            if len(proj.description.split()) > 100:
                score -= 2
                suggestions.append({
                    "category": "readability",
                    "priority": "low",
                    "message": "Project descriptions are too long - keep under 100 words"
                })
                break
        
        return {"score": max(0, score), "suggestions": suggestions}
    
    def _check_file_structure(self, resume: ResumeJSON) -> dict[str, Any]:
        """Check file structure (10 points)."""
        score = 10
        suggestions = []
        
        # PDF format is good (we know it's PDF since we parsed it)
        # Single page is preferred
        if resume.meta.pageCount == 1:
            # Ideal
            pass
        elif resume.meta.pageCount == 2:
            score -= 2
        else:
            score -= 4
            suggestions.append({
                "category": "file",
                "priority": "low",
                "message": "Try to fit resume on 1-2 pages"
            })
        
        return {"score": score, "suggestions": suggestions}
