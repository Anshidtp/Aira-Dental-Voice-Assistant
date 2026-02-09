from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Dental Voice AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # MongoDB
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "dental_ai_db"
    MONGODB_MIN_POOL_SIZE: int = 10
    MONGODB_MAX_POOL_SIZE: int = 100
    
    # Groq Cloud
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 1024
    
    # LiveKit
    LIVEKIT_API_KEY: str
    LIVEKIT_API_SECRET: str
    LIVEKIT_URL: str = "wss://your-livekit-server.livekit.cloud"
    LIVEKIT_ROOM_PREFIX: str = "dental_clinic_"
    
    # Deepgram (STT)
    DEEPGRAM_API_KEY: str
    DEEPGRAM_MODEL: str = "nova-2"
    DEEPGRAM_LANGUAGE: str = "multi"
    
    # ElevenLabs (TTS)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID_ENGLISH: str = "21m00Tcm4TlvDq8ikWAM"
    ELEVENLABS_VOICE_ID_MALAYALAM: str = "pNInz6obpgDQGcFmaJgB"
    
    # Google Cloud TTS
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GOOGLE_TTS_ENABLED: bool = False
    
    # Language Settings
    DEFAULT_LANGUAGE: str = "en"
    KERALA_LANGUAGE: str = "ml"
    SUPPORTED_LANGUAGES: str = "en,ml,hi,ta"
    AUTO_DETECT_LANGUAGE: bool = True
    
    # Clinic Information
    CLINIC_NAME: str = "Smile Dental Clinic"
    CLINIC_ADDRESS: str = "123 Main Street, Perintalmanna, Kerala 679322"
    CLINIC_PHONE: str = "+919876543210"
    CLINIC_EMAIL: str = "info@smiledentalclinic.com"
    CLINIC_WORKING_HOURS: str = "9:00 AM - 8:00 PM"
    CLINIC_WORKING_DAYS: str = "Monday to Saturday"
    
    # Appointment Settings
    APPOINTMENT_SLOT_DURATION: int = 30
    APPOINTMENT_BUFFER_MINUTES: int = 15
    MAX_DAILY_APPOINTMENTS: int = 20
    APPOINTMENT_REMINDER_HOURS: int = 24
    
    # AI Agent
    AI_ASSISTANT_NAME: str = "Dr. AI Assistant"
    AI_GREETING_TIMEOUT: int = 5
    AI_MAX_CONVERSATION_TURNS: int = 20
    AI_CONVERSATION_TIMEOUT: int = 300
    
    # Phone Integration
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/dental_ai.log"
    LOG_ROTATION: str = "500 MB"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_CALLS_PER_MINUTE: int = 10
    RATE_LIMIT_ENABLED: bool = True
    
    # Webhooks
    WEBHOOK_SECRET: str = "your-webhook-secret"
    WEBHOOK_TIMEOUT: int = 30
    
    # Feature Flags
    ENABLE_VOICE_RECORDING: bool = True
    ENABLE_CONVERSATION_LOGGING: bool = True
    ENABLE_ANALYTICS: bool = True
    ENABLE_SMS_NOTIFICATIONS: bool = False
    
    @property
    def supported_languages_list(self) -> List[str]:
        """Get supported languages as a list"""
        return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()