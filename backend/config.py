from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application
    app_name: str = "Dental Voice AI"
    app_version: str = "1.0.0"
    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # LiveKit
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    
    # GROQ CONFIGURATION (UNIFIED LLM)
    # ========================================================================
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"
    groq_temperature: float = 0.7
    groq_max_tokens: int = 1024
    groq_top_p: float = 0.9
    
    # Speech-to-Text
    stt_provider: str = "deepgram"  # deepgram or whisper
    deepgram_api_key: Optional[str] = None
    whisper_model: str = "medium"
    whisper_device: str = "cpu"
    
    # Text-to-Speech
    tts_provider: str = "elevenlabs"  # elevenlabs or cartesia
    elevenlabs_api_key: Optional[str] = None
    elevenlabs_voice_id_en: str = "21m00Tcm4TlvDq8ikWAM"
    elevenlabs_voice_id_ml: str = "custom_malayalam_voice"
    cartesia_api_key: Optional[str] = None
    cartesia_voice_id: str = "794f9389-aac1-45b6-b726-9d9369183238"
    
    # Database
    database_url: str
    db_echo: bool = False
    db_pool_size: int = 20
    db_max_overflow: int = 0
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    
    # Voice Agent
    agent_language_detection: str = "auto"
    agent_default_language: str = "en"
    agent_interrupt_enabled: bool = True
    agent_vad_sensitivity: float = 0.5
    agent_response_timeout: int = 30
    
    # Dental Clinic
    clinic_name: str = "Smile Dental Clinic"
    clinic_timezone: str = "Asia/Kolkata"
    clinic_working_hours_start: str = "09:00"
    clinic_working_hours_end: str = "18:00"
    clinic_working_days: str = "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def working_days_list(self) -> List[str]:
        """Get working days as a list"""
        return [day.strip() for day in self.clinic_working_days.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.env.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.env.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()