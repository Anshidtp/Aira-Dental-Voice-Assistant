"""
Pydantic models for request/response validation
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum


class LanguageEnum(str, Enum):
    """Supported languages"""
    ENGLISH = "en"
    MALAYALAM = "ml"


class AppointmentStatus(str, Enum):
    """Appointment status"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Voice Session Schemas
class VoiceSessionCreate(BaseModel):
    """Schema for creating a voice session"""
    patient_id: Optional[str] = None
    language: Optional[LanguageEnum] = None
    metadata: Optional[Dict[str, Any]] = None


class VoiceSessionResponse(BaseModel):
    """Schema for voice session response"""
    session_id: str
    room_name: str
    token: str
    livekit_url: str
    expires_at: datetime
    language: str
    
    class Config:
        from_attributes = True


class ConversationMessage(BaseModel):
    """Schema for conversation message"""
    role: MessageRole
    content: str
    language: LanguageEnum
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None


# Patient Schemas
class PatientBase(BaseModel):
    """Base patient schema"""
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., pattern=r'^\+?1?\d{9,15}$')
    email: Optional[EmailStr] = None
    preferred_language: LanguageEnum = LanguageEnum.ENGLISH
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None


class PatientCreate(PatientBase):
    """Schema for creating a patient"""
    pass


class PatientUpdate(BaseModel):
    """Schema for updating a patient"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    email: Optional[EmailStr] = None
    preferred_language: Optional[LanguageEnum] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[str] = None


class PatientResponse(PatientBase):
    """Schema for patient response"""
    id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Appointment Schemas
class AppointmentBase(BaseModel):
    """Base appointment schema"""
    patient_id: str
    appointment_date: datetime
    duration_minutes: int = Field(30, ge=15, le=180)
    reason: str = Field(..., min_length=1, max_length=500)
    notes: Optional[str] = None


class AppointmentCreate(AppointmentBase):
    """Schema for creating an appointment"""
    
    @validator('appointment_date')
    def appointment_must_be_future(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Appointment date must be in the future')
        return v


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    appointment_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=15, le=180)
    reason: Optional[str] = Field(None, min_length=1, max_length=500)
    notes: Optional[str] = None
    status: Optional[AppointmentStatus] = None


class AppointmentResponse(AppointmentBase):
    """Schema for appointment response"""
    id: str
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    patient: Optional[PatientResponse] = None
    
    class Config:
        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Schema for appointment list response"""
    total: int
    appointments: List[AppointmentResponse]


# Dental Information Schemas
class DentalQuery(BaseModel):
    """Schema for dental query"""
    question: str = Field(..., min_length=1, max_length=1000)
    language: LanguageEnum = LanguageEnum.ENGLISH
    context: Optional[str] = None


class DentalResponse(BaseModel):
    """Schema for dental response"""
    answer: str
    language: LanguageEnum
    sources: Optional[List[str]] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)


# Health Check Schemas
class HealthCheck(BaseModel):
    """Schema for health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, str]


# Error Schemas
class ErrorResponse(BaseModel):
    """Schema for error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Agent Schemas
class AgentState(BaseModel):
    """Schema for agent state"""
    session_id: str
    language: LanguageEnum
    conversation_history: List[ConversationMessage]
    context: Dict[str, Any]
    current_intent: Optional[str] = None


class IntentRecognition(BaseModel):
    """Schema for intent recognition"""
    intent: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    entities: Dict[str, Any]
    language: LanguageEnum


# Metrics Schemas
class SessionMetrics(BaseModel):
    """Schema for session metrics"""
    session_id: str
    duration_seconds: float
    message_count: int
    language_switches: int
    intents_recognized: List[str]
    avg_response_time_ms: float
    errors_count: int