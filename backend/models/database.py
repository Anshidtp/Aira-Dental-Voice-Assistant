from beanie import Document, Indexed
from pydantic import Field, EmailStr
from datetime import datetime, date 
from typing import Optional, List
from enum import Enum
from uuid import uuid4


class AppointmentStatus(str, Enum):
    """Appointment status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class LanguageEnum(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    MALAYALAM = "ml"
    HINDI = "hi"
    TAMIL = "ta"


class Appointment(Document):
    """Appointment model"""
    id: str = Field(default_factory=lambda: str(uuid4()))  # Use UUID for id
    patient_name: str = Field(..., min_length=2, max_length=255)
    patient_phone: Indexed(str) = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    patient_email: Optional[EmailStr] = None
    
    appointment_date: Indexed(date)  # Change to date
    appointment_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    duration_minutes: int = Field(default=30)
    
    reason: Optional[str] = None
    notes: Optional[str] = None
    
    status: AppointmentStatus = Field(default=AppointmentStatus.PENDING)
    preferred_language: LanguageEnum = Field(default=LanguageEnum.ENGLISH)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Call tracking
    call_sid: Optional[Indexed(str)] = None
    call_duration_seconds: Optional[int] = None
    
    class Settings:
        name = "appointments"
        indexes = [
            "patient_phone",
            "appointment_date",
            "status",
            "call_sid",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "patient_name": "Rajesh Kumar",
                "patient_phone": "+919876543210",
                "patient_email": "rajesh@example.com",
                "appointment_date": "2024-03-15",
                "appointment_time": "10:00",
                "reason": "Dental checkup",
                "preferred_language": "ml"
            }
        }


class Conversation(Document):
    """Conversation history model"""
    session_id: Indexed(str, unique=True)
    
    caller_phone: Indexed(str)
    language: LanguageEnum = Field(default=LanguageEnum.ENGLISH)
    
    transcript: Optional[str] = None
    conversation_summary: Optional[str] = None
    
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # LiveKit room info
    room_name: Optional[str] = None
    
    # Associated appointment
    appointment_id: Optional[str] = None
    
    # Flags
    appointment_created: bool = Field(default=False)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "conversations"
        indexes = [
            "session_id",
            "caller_phone",
            "started_at",
        ]


class ConversationMessage(Document):
    """Individual messages in a conversation"""
    conversation_id: Indexed(str)
    
    role: str = Field(..., pattern=r'^(user|assistant|system)$')
    content: str
    language: Optional[str] = None
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Audio metadata
    audio_duration_ms: Optional[int] = None
    
    class Settings:
        name = "conversation_messages"
        indexes = [
            "conversation_id",
            "timestamp",
        ]


class PatientRecord(Document):
    """Patient records for repeat callers"""
    phone: Indexed(str, unique=True)
    name: str = Field(..., min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    
    preferred_language: LanguageEnum = Field(default=LanguageEnum.ENGLISH)
    
    total_appointments: int = Field(default=0)
    total_calls: int = Field(default=0)
    
    notes: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_contact: Optional[datetime] = None
    
    class Settings:
        name = "patient_records"
        indexes = [
            "phone",
            "last_contact",
        ]


class AnalyticsEvent(Document):
    """Analytics and metrics tracking"""
    event_type: Indexed(str)  # call_started, call_ended, appointment_created, etc.
    event_data: dict = Field(default_factory=dict)
    
    session_id: Optional[str] = None
    user_phone: Optional[str] = None
    
    timestamp: Indexed(datetime) = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "analytics_events"
        indexes = [
            "event_type",
            "timestamp",
            "session_id",
        ]


# List of all document models for initialization
DOCUMENT_MODELS = [
    Appointment,
    Conversation,
    ConversationMessage,
    PatientRecord,
    AnalyticsEvent,
]