"""
Claude AI client for resume improvements.
"""
from typing import Any

from anthropic import Anthropic

from app.core.config import settings
from app.core.exceptions import AIServiceError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ClaudeClient:
    """
    Claude AI client.
    
    Architectural Decision:
    - Uses Claude 3.5 Sonnet for high-quality text improvement
    - Structured prompts ensure factual accuracy
    - Temperature 0.7 for balanced creativity/accuracy
    - Max 1000 tokens for concise improvements
    """
    
    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set - AI features disabled")
            self.client = None
        else:
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    def improve_text(
        self,
        text: str,
        improvement_type: str,
        context: dict[str, Any] | None = None
    ) -> str:
        """
        Improve text using Claude API.
        
        Args:
            text: Original text to improve
            improvement_type: Type of improvement (grammar, action_verbs, etc.)
            context: Additional context
            
        Returns:
            Improved text
            
        Raises:
            AIServiceError: If API call fails
        """
        if not self.client:
            raise AIServiceError("AI service not configured")
        
        try:
            # Build prompt based on improvement type
            system_prompt = self._get_system_prompt(improvement_type)
            user_prompt = self._build_user_prompt(text, improvement_type, context)
            
            # Call Claude API
            response = self.client.messages.create(
                model=settings.AI_MODEL_CLAUDE,
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Extract improved text
            improved = response.content[0].text.strip()
            
            logger.info(
                "Text improved with Claude",
                extra={
                    "improvement_type": improvement_type,
                    "original_length": len(text),
                    "improved_length": len(improved)
                }
            )
            
            return improved
        
        except Exception as e:
            logger.error("Claude API call failed", extra={"error": str(e)})
            raise AIServiceError(f"Failed to improve text: {str(e)}")
    
    def _get_system_prompt(self, improvement_type: str) -> str:
        """Get system prompt based on improvement type."""
        base = """You are a professional resume writer helping improve resume content.
Your improvements must:
1. Preserve all factual information
2. Keep the same overall meaning
3. Be concise and professional
4. Use active voice and strong action verbs
5. Be ATS-friendly"""
        
        type_specific = {
            "grammar": "\nFocus on correcting grammar, spelling, and punctuation errors.",
            "action_verbs": "\nReplace weak verbs with strong action verbs (developed, implemented, achieved, etc.).",
            "professional_tone": "\nImprove professional tone while keeping content truthful.",
            "clarity": "\nMake the text clearer and more concise without losing information.",
            "quantify": "\nHelp quantify achievements where possible (add metrics if the context suggests them)."
        }
        
        return base + type_specific.get(improvement_type, "")
    
    def _build_user_prompt(
        self,
        text: str,
        improvement_type: str,
        context: dict[str, Any] | None
    ) -> str:
        """Build user prompt with text and context."""
        prompt = f"Improve this resume text:\n\n{text}\n\n"
        
        if context:
            if "role" in context:
                prompt += f"Role: {context['role']}\n"
            if "company" in context:
                prompt += f"Company: {context['company']}\n"
        
        prompt += "\nProvide only the improved text, no explanations."
        
        return prompt


# Global Claude client instance
claude_client = ClaudeClient()
