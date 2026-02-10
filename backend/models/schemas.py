from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, date, time
from typing import Optional, List
from enum import Enum
import re


class LanguageEnum(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    MALAYALAM = "ml"
    HINDI = "hi"
    TAMIL = "ta"


class AppointmentStatus(str, Enum):
    """Appointment status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


# Appointment Schemas
class AppointmentBase(BaseModel):
    """Base appointment schema"""
    patient_name: str = Field(..., min_length=2, max_length=255)
    patient_phone: str = Field(..., pattern=r'^\+?[1-9]\d{9,14}$')
    patient_email: Optional[EmailStr] = None
    appointment_date: date
    appointment_time: str = Field(..., pattern=r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$')
    reason: Optional[str] = None
    notes: Optional[str] = None
    preferred_language: LanguageEnum = LanguageEnum.ENGLISH


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    pass


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[EmailStr] = None
    appointment_date: Optional[date] = None
    appointment_time: Optional[str] = None
    reason: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None
    preferred_language: Optional[LanguageEnum] = None

    @validator("patient_phone")
    def validate_patient_phone(cls, value):
        if value and not re.match(r'^\+?[1-9]\d{9,14}$', value):
            raise ValueError("Invalid phone number format. Must match pattern: ^\\+?[1-9]\\d{9,14}$")
        return value


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response"""
    id: str  # Changed from int to str to match UUID
    status: AppointmentStatus
    duration_minutes: int
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AppointmentList(BaseModel):
    """Schema for list of appointments"""
    appointments: List[AppointmentResponse]
    total: int
    page: int
    page_size: int


# Conversation Schemas
class ConversationMessage(BaseModel):
    """Individual conversation message"""
    role: str
    content: str
    language: Optional[str] = None
    timestamp: datetime


class ConversationCreate(BaseModel):
    """Create a new conversation"""
    caller_phone: str
    language: LanguageEnum = LanguageEnum.ENGLISH


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: int
    session_id: str
    caller_phone: str
    language: LanguageEnum
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    appointment_created: bool
    
    class Config:
        from_attributes = True


# Voice/LiveKit Schemas
class LiveKitTokenRequest(BaseModel):
    """Request for LiveKit access token"""
    room_name: str
    participant_name: str
    metadata: Optional[dict] = None


class LiveKitTokenResponse(BaseModel):
    """LiveKit token response"""
    token: str
    room_name: str
    url: str


class IncomingCallRequest(BaseModel):
    """Incoming call webhook"""
    call_sid: str
    caller_phone: str
    caller_name: Optional[str] = None


class VoiceResponse(BaseModel):
    """Voice API response"""
    success: bool
    message: str
    session_id: Optional[str] = None
    room_name: Optional[str] = None
    token: Optional[str] = None


# Patient Record Schemas
class PatientRecordCreate(BaseModel):
    """Create patient record"""
    phone: str
    name: str
    email: Optional[EmailStr] = None
    preferred_language: LanguageEnum = LanguageEnum.ENGLISH
    notes: Optional[str] = None


class PatientRecordResponse(BaseModel):
    """Patient record response"""
    id: int
    phone: str
    name: str
    email: Optional[str] = None
    preferred_language: LanguageEnum
    total_appointments: int
    total_calls: int
    created_at: datetime
    last_contact: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# AI Agent Schemas
class ChatMessage(BaseModel):
    """Chat message for AI agent"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request to AI agent"""
    message: str
    language: LanguageEnum = LanguageEnum.ENGLISH
    conversation_history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    """AI agent chat response"""
    response: str
    language: LanguageEnum
    intent: Optional[str] = None
    entities: Optional[dict] = None


# Webhook Schemas
class LiveKitWebhook(BaseModel):
    """LiveKit webhook payload"""
    event: str
    room: dict
    participant: Optional[dict] = None
    track: Optional[dict] = None
    created_at: int


# Health Check
class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    database: str
    livekit: str
    groq: str