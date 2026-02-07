from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text, Boolean, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


def generate_uuid():
    """Generate UUID for primary keys"""
    return str(uuid.uuid4())


class Patient(Base):
    """Patient model"""
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, index=True)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True, unique=True, index=True)
    preferred_language = Column(String(5), nullable=False, default="en")
    date_of_birth = Column(DateTime, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    # Medical information
    medical_history = Column(JSON, nullable=True)
    allergies = Column(JSON, nullable=True)
    medications = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    appointments = relationship("Appointment", back_populates="patient", cascade="all, delete-orphan")
    sessions = relationship("VoiceSession", back_populates="patient", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, name={self.name}, phone={self.phone})>"


class Appointment(Base):
    """Appointment model"""
    __tablename__ = "appointments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False, index=True)
    appointment_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=False, default=30)
    reason = Column(String(500), nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, default="pending", index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient_id={self.patient_id}, date={self.appointment_date})>"


class VoiceSession(Base):
    """Voice session model"""
    __tablename__ = "voice_sessions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    patient_id = Column(String, ForeignKey("patients.id"), nullable=True, index=True)
    room_name = Column(String(255), nullable=False, unique=True, index=True)
    language = Column(String(5), nullable=False, default="en")
    
    # Session details
    started_at = Column(DateTime, nullable=False, server_default=func.now())
    ended_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Conversation
    message_count = Column(Integer, nullable=False, default=0)
    conversation_summary = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="sessions")
    messages = relationship("ConversationMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<VoiceSession(id={self.id}, room_name={self.room_name}, language={self.language})>"


class ConversationMessage(Base):
    """Conversation message model"""
    __tablename__ = "conversation_messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("voice_sessions.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    language = Column(String(5), nullable=False)
    
    # Audio metadata
    audio_duration_ms = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Additional metadata
    intent = Column(String(100), nullable=True)
    entities = Column(JSON, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now(), index=True)
    
    # Relationships
    session = relationship("VoiceSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, session_id={self.session_id}, role={self.role})>"


class DentalKnowledgeBase(Base):
    """Dental knowledge base model"""
    __tablename__ = "dental_knowledge_base"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    category = Column(String(100), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer_en = Column(Text, nullable=False)
    answer_ml = Column(Text, nullable=False)
    keywords = Column(JSON, nullable=True)
    
    # Metadata
    difficulty_level = Column(String(20), nullable=True)  # basic, intermediate, advanced
    source = Column(String(255), nullable=True)
    verified = Column(Boolean, nullable=False, default=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<DentalKnowledgeBase(id={self.id}, category={self.category})>"


class SessionMetrics(Base):
    """Session metrics model for analytics"""
    __tablename__ = "session_metrics"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("voice_sessions.id"), nullable=False, index=True)
    
    # Performance metrics
    avg_response_time_ms = Column(Float, nullable=True)
    avg_stt_latency_ms = Column(Float, nullable=True)
    avg_llm_latency_ms = Column(Float, nullable=True)
    avg_tts_latency_ms = Column(Float, nullable=True)
    
    # Quality metrics
    language_detection_accuracy = Column(Float, nullable=True)
    intent_recognition_accuracy = Column(Float, nullable=True)
    interruption_count = Column(Integer, nullable=False, default=0)
    error_count = Column(Integer, nullable=False, default=0)
    
    # Usage metrics
    language_switches = Column(Integer, nullable=False, default=0)
    intents_recognized = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<SessionMetrics(id={self.id}, session_id={self.session_id})>"