"""Optional LLM-based requirement extraction."""
from app.services.extractor import ExtractedRequirement, PageText
from app.core.config import get_settings

class LLMRequirementExtractor:
    """Fallback extractor using an LLM for complex PDFs."""
    
    def extract(self, pages: list[PageText]) -> list[ExtractedRequirement]:
        if not get_settings().enable_llm_extractor:
            # Fallback to empty if not enabled (caller should use rule-based)
            return []
            
        # For MVP, this simulates an LLM API call
        # In a real implementation, this would call OpenAI/Anthropic/Gemini
        
        # Combine all text
        full_text = "\n".join(p.text for p in pages)
        
        # Simple simulated extraction for demonstration
        results = []
        if "complex requirement" in full_text.lower():
            results.append(
                ExtractedRequirement(
                    requirement_id="LLM-REQ-001",
                    raw_text="Complex requirement extracted via LLM",
                    product="Unknown",
                    mandatory=True,
                    parameters={}
                )
            )
            
        return results
