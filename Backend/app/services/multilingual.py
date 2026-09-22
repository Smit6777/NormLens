"""Multilingual support (Hindi)."""
from app.core.config import get_settings

HINDI_DICTIONARY = {
    "सीमेंट": "cement",
    "इस्पात": "steel",
    "कंक्रीट": "concrete",
    "पानी": "water",
    "सुरक्षा": "safety",
    "हेलमेट": "helmet",
    "बिजली": "electrical",
    "केबल": "cable",
    "परीक्षण": "test"
}

def translate_to_english(text: str) -> str:
    """Simple dictionary-based translation for Hindi terms."""
    if not get_settings().enable_hindi:
        return text
        
    translated = text
    # Very rudimentary translation for MVP
    for hi, en in HINDI_DICTIONARY.items():
        translated = translated.replace(hi, en)
        
    return translated
