from langdetect import detect, LangDetectException
from typing import Optional, Dict
from loguru import logger

from ..config.settings import settings


class LanguageService:
    """Service for language detection and translation"""
    
    LANGUAGE_NAMES = {
        "en": "English",
        "ml": "Malayalam",
        "hi": "Hindi",
        "ta": "Tamil",
    }
    
    GREETINGS = {
        "en": "Hello! Welcome to {clinic_name}. How can I help you today?",
        "ml": "നമസ്കാരം! {clinic_name}യിലേക്ക് സ്വാഗതം. ഞാൻ നിങ്ങളെ എങ്ങനെ സഹായിക്കും?",
        "hi": "नमस्ते! {clinic_name} में आपका स्वागत है। मैं आपकी कैसे मदद कर सकता हूं?",
        "ta": "வணக்கம்! {clinic_name}க்கு வரவேற்கிறோம். நான் உங்களுக்கு எப்படி உதவ முடியும்?",
    }
    
    APPOINTMENT_CONFIRMATIONS = {
        "en": "I've scheduled your appointment for {date} at {time}. Your appointment ID is {id}. Is there anything else I can help you with?",
        "ml": "നിങ്ങളുടെ അപ്പോയിന്റ്മെന്റ് {date} {time}-ന് ഷെഡ്യൂൾ ചെയ്തിട്ടുണ്ട്. നിങ്ങളുടെ അപ്പോയിന്റ്മെന്റ് ഐഡി {id} ആണ്. മറ്റെന്തെങ്കിലും സഹായം വേണോ?",
        "hi": "मैंने आपकी अपॉइंटमेंट {date} को {time} बजे शेड्यूल कर दी है। आपकी अपॉइंटमेंट आईडी {id} है। क्या मैं आपकी कोई और मदद कर सकता हूं?",
        "ta": "உங்கள் சந்திப்பை {date} அன்று {time} மணிக்கு திட்டமிட்டுள்ளேன். உங்கள் சந்திப்பு ஐடி {id}. வேறு ஏதாவது உதவி தேவையா?",
    }
    
    ASK_NAME = {
        "en": "May I have your name, please?",
        "ml": "നിങ്ങളുടെ പേര് പറയാമോ?",
        "hi": "कृपया अपना नाम बताएं?",
        "ta": "தயவுசெய்து உங்கள் பெயரைச் சொல்ல முடியுமா?",
    }
    
    ASK_PHONE = {
        "en": "What's your phone number?",
        "ml": "നിങ്ങളുടെ ഫോൺ നമ്പർ എന്താണ്?",
        "hi": "आपका फोन नंबर क्या है?",
        "ta": "உங்கள் தொலைபேசி எண் என்ன?",
    }
    
    ASK_DATE = {
        "en": "Which date would you prefer for your appointment?",
        "ml": "നിങ്ങൾക്ക് ഏത് തീയതിയാണ് അപ്പോയിന്റ്മെന്റിന് ഇഷ്ടം?",
        "hi": "आप किस तारीख को अपॉइंटमेंट लेना चाहेंगे?",
        "ta": "உங்கள் சந்திப்புக்கு எந்த தேதியை விரும்புகிறீர்கள்?",
    }
    
    ASK_TIME = {
        "en": "What time works best for you?",
        "ml": "നിങ്ങൾക്ക് ഏത് സമയം സൗകര്യമാണ്?",
        "hi": "आपके लिए कौन सा समय सबसे अच्छा है?",
        "ta": "உங்களுக்கு எந்த நேரம் சிறந்தது?",
    }
    
    CLOSING = {
        "en": "Thank you for calling {clinic_name}. Have a great day!",
        "ml": "{clinic_name}യിലേക്ക് വിളിച്ചതിന് നന്ദി. നല്ല ദിവസം!",
        "hi": "{clinic_name} को कॉल करने के लिए धन्यवाद। आपका दिन शुभ हो!",
        "ta": "{clinic_name}க்கு அழைத்ததற்கு நன்றி. நல்ல நாள்!",
    }
    
    def __init__(self):
        """Initialize language service"""
        self.supported_languages = settings.supported_languages_list
        logger.info(f"Language service initialized with languages: {self.supported_languages}")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text
        
        Args:
            text: Input text
            
        Returns:
            Language code (en, ml, hi, ta)
        """
        try:
            detected = detect(text)
            
            # Map detected language to supported languages
            if detected in self.supported_languages:
                logger.debug(f"Detected language: {detected}")
                return detected
            
            # Default to English
            logger.debug(f"Detected {detected}, defaulting to English")
            return settings.DEFAULT_LANGUAGE
            
        except LangDetectException as e:
            logger.warning(f"Language detection failed: {e}, defaulting to English")
            return settings.DEFAULT_LANGUAGE
    
    def get_greeting(self, language: str = "en") -> str:
        """Get greeting message in specified language"""
        greeting = self.GREETINGS.get(language, self.GREETINGS["en"])
        return greeting.format(clinic_name=settings.CLINIC_NAME)
    
    def get_appointment_confirmation(
        self,
        language: str,
        date: str,
        time: str,
        appointment_id: int
    ) -> str:
        """Get appointment confirmation message"""
        msg = self.APPOINTMENT_CONFIRMATIONS.get(
            language,
            self.APPOINTMENT_CONFIRMATIONS["en"]
        )
        return msg.format(date=date, time=time, id=appointment_id)
    
    def get_template(self, template_name: str, language: str = "en") -> str:
        """
        Get a template message in specified language
        
        Args:
            template_name: Template name (ask_name, ask_phone, etc.)
            language: Language code
            
        Returns:
            Template message
        """
        templates = {
            "ask_name": self.ASK_NAME,
            "ask_phone": self.ASK_PHONE,
            "ask_date": self.ASK_DATE,
            "ask_time": self.ASK_TIME,
            "closing": self.CLOSING,
        }
        
        template_dict = templates.get(template_name, {})
        message = template_dict.get(language, template_dict.get("en", ""))
        
        # Format with clinic name if needed
        if "{clinic_name}" in message:
            message = message.format(clinic_name=settings.CLINIC_NAME)
        
        return message
    
    def is_kerala_region(self, phone: Optional[str] = None) -> bool:
        """
        Determine if caller is from Kerala region
        
        Args:
            phone: Phone number (can check area code)
            
        Returns:
            True if Kerala region
        """
        # Kerala STD codes: 0471-0499, 0480-0489
        # This is a simple heuristic
        if phone and phone.startswith("+91"):
            # Check for Kerala area codes (simplified)
            kerala_codes = ["471", "472", "473", "474", "475", "476", "477", 
                          "478", "479", "480", "481", "482", "483", "484",
                          "485", "486", "487", "488", "489", "490", "491"]
            
            for code in kerala_codes:
                if code in phone:
                    return True
        
        return False
    
    def get_initial_language(self, phone: Optional[str] = None) -> str:
        """
        Get initial language based on phone number or region
        
        Args:
            phone: Caller's phone number
            
        Returns:
            Language code
        """
        if settings.AUTO_DETECT_LANGUAGE and self.is_kerala_region(phone):
            logger.info(f"Kerala region detected for {phone}, using Malayalam")
            return settings.KERALA_LANGUAGE
        
        return settings.DEFAULT_LANGUAGE


# Global instance
language_service = LanguageService()