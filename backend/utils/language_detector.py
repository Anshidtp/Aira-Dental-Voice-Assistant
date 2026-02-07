import re
from typing import Tuple


class LanguageDetector:
    """Detect language from text (Malayalam or English)"""
    
    # Unicode ranges for Malayalam script
    MALAYALAM_RANGE = r'[\u0D00-\u0D7F]+'
    
    # Common Malayalam words for additional validation
    MALAYALAM_COMMON_WORDS = [
        'എന്ത്', 'എങ്ങനെ', 'ആണ്', 'എവിടെ', 'എപ്പോൾ', 
        'ആരാണ്', 'എത്ര', 'ഉണ്ട്', 'ഇല്ല', 'കഴിയും'
    ]
    
    # Common English words
    ENGLISH_COMMON_WORDS = [
        'the', 'is', 'are', 'was', 'were', 'have', 'has', 'do', 'does',
        'what', 'when', 'where', 'who', 'how', 'why', 'can', 'could'
    ]
    
    def __init__(self):
        self.malayalam_pattern = re.compile(self.MALAYALAM_RANGE)
    
    def detect(self, text: str, threshold: float = 0.3) -> Tuple[str, float]:
        """
        Detect language from text
        
        Args:
            text: Input text
            threshold: Threshold for Malayalam character ratio (default 0.3)
        
        Returns:
            Tuple of (language_code, confidence)
            language_code: 'ml' for Malayalam, 'en' for English
            confidence: Float between 0 and 1
        """
        if not text or not text.strip():
            return "en", 0.5  # Default to English with low confidence
        
        text = text.strip()
        
        # Count Malayalam characters
        malayalam_chars = self.malayalam_pattern.findall(text)
        malayalam_char_count = sum(len(chars) for chars in malayalam_chars)
        
        # Total characters (excluding spaces and punctuation)
        total_chars = len(re.sub(r'[^\w]', '', text, flags=re.UNICODE))
        
        if total_chars == 0:
            return "en", 0.5
        
        # Calculate Malayalam character ratio
        malayalam_ratio = malayalam_char_count / total_chars
        
        # Check for common words
        text_lower = text.lower()
        malayalam_word_matches = sum(1 for word in self.MALAYALAM_COMMON_WORDS if word in text)
        english_word_matches = sum(1 for word in self.ENGLISH_COMMON_WORDS if word_lower in text_lower for word_lower in [word])
        
        # Determine language
        if malayalam_ratio >= threshold or malayalam_word_matches > 0:
            # Malayalam detected
            confidence = min(1.0, malayalam_ratio + (malayalam_word_matches * 0.1))
            return "ml", confidence
        elif english_word_matches > 0:
            # English with word matches
            confidence = min(1.0, 0.7 + (english_word_matches * 0.05))
            return "en", confidence
        else:
            # Default to English if no clear indicators
            # But with lower confidence
            confidence = 1.0 - malayalam_ratio
            return "en", confidence
    
    def is_malayalam(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is primarily Malayalam
        
        Args:
            text: Input text
            threshold: Threshold for Malayalam character ratio
        
        Returns:
            True if Malayalam, False otherwise
        """
        language, confidence = self.detect(text, threshold)
        return language == "ml" and confidence > 0.5
    
    def is_english(self, text: str, threshold: float = 0.3) -> bool:
        """
        Check if text is primarily English
        
        Args:
            text: Input text
            threshold: Threshold for Malayalam character ratio
        
        Returns:
            True if English, False otherwise
        """
        language, confidence = self.detect(text, threshold)
        return language == "en" and confidence > 0.5
    
    def get_language_stats(self, text: str) -> dict:
        """
        Get detailed language statistics
        
        Args:
            text: Input text
        
        Returns:
            Dictionary with language statistics
        """
        if not text or not text.strip():
            return {
                "language": "en",
                "confidence": 0.5,
                "malayalam_ratio": 0.0,
                "total_chars": 0,
                "malayalam_chars": 0
            }
        
        malayalam_chars = self.malayalam_pattern.findall(text)
        malayalam_char_count = sum(len(chars) for chars in malayalam_chars)
        total_chars = len(re.sub(r'[^\w]', '', text, flags=re.UNICODE))
        
        malayalam_ratio = malayalam_char_count / total_chars if total_chars > 0 else 0
        language, confidence = self.detect(text)
        
        return {
            "language": language,
            "confidence": confidence,
            "malayalam_ratio": malayalam_ratio,
            "total_chars": total_chars,
            "malayalam_chars": malayalam_char_count,
            "english_chars": total_chars - malayalam_char_count
        }


# Global instance
language_detector = LanguageDetector()