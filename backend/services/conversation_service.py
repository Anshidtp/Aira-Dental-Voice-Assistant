from beanie import PydanticObjectId
from datetime import datetime
from typing import List, Optional
from loguru import logger

from ..models.database import Conversation, ConversationMessage, PatientRecord, LanguageEnum


class ConversationService:
    """Service for managing conversations with MongoDB"""
    
    @staticmethod
    async def create_conversation(
        session_id: str,
        caller_phone: str,
        language: LanguageEnum,
        room_name: Optional[str] = None
    ) -> Conversation:
        """
        Create a new conversation
        
        Args:
            session_id: Unique session identifier
            caller_phone: Caller's phone number
            language: Conversation language
            room_name: LiveKit room name
            
        Returns:
            Created conversation
        """
        try:
            conversation = Conversation(
                session_id=session_id,
                caller_phone=caller_phone,
                language=language,
                room_name=room_name,
            )
            
            await conversation.insert()
            
            logger.info(f"Created conversation {conversation.id} for session {session_id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise
    
    @staticmethod
    async def get_conversation_by_session(
        session_id: str
    ) -> Optional[Conversation]:
        """Get conversation by session ID"""
        try:
            conversation = await Conversation.find_one({"session_id": session_id})
            return conversation
            
        except Exception as e:
            logger.error(f"Error getting conversation: {e}")
            return None
    
    @staticmethod
    async def add_message(
        conversation_id: str,
        role: str,
        content: str,
        language: Optional[str] = None,
        audio_duration_ms: Optional[int] = None
    ) -> ConversationMessage:
        """
        Add a message to a conversation
        
        Args:
            conversation_id: Conversation ID
            role: Message role (user/assistant/system)
            content: Message content
            language: Message language
            audio_duration_ms: Audio duration in milliseconds
            
        Returns:
            Created message
        """
        try:
            message = ConversationMessage(
                conversation_id=conversation_id,
                role=role,
                content=content,
                language=language,
                audio_duration_ms=audio_duration_ms,
            )
            
            await message.insert()
            
            logger.debug(f"Added {role} message to conversation {conversation_id}")
            return message
            
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise
    
    @staticmethod
    async def get_conversation_messages(
        conversation_id: str,
        limit: int = 100
    ) -> List[ConversationMessage]:
        """Get all messages for a conversation"""
        try:
            messages = await ConversationMessage.find(
                {"conversation_id": conversation_id}
            ).sort("timestamp").limit(limit).to_list()
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting conversation messages: {e}")
            return []
    
    @staticmethod
    async def end_conversation(
        session_id: str,
        appointment_id: Optional[str] = None
    ) -> Optional[Conversation]:
        """
        End a conversation
        
        Args:
            session_id: Session ID
            appointment_id: Optional appointment ID if created
            
        Returns:
            Updated conversation
        """
        try:
            conversation = await ConversationService.get_conversation_by_session(session_id)
            if not conversation:
                return None
            
            conversation.ended_at = datetime.utcnow()
            conversation.duration_seconds = int(
                (conversation.ended_at - conversation.started_at).total_seconds()
            )
            
            if appointment_id:
                conversation.appointment_id = appointment_id
                conversation.appointment_created = True
            
            await conversation.save()
            
            logger.info(f"Ended conversation {conversation.id}")
            return conversation
            
        except Exception as e:
            logger.error(f"Error ending conversation: {e}")
            raise
    
    @staticmethod
    async def update_transcript(
        session_id: str,
        transcript: str
    ) -> Optional[Conversation]:
        """Update conversation transcript"""
        try:
            conversation = await ConversationService.get_conversation_by_session(session_id)
            if not conversation:
                return None
            
            conversation.transcript = transcript
            await conversation.save()
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error updating transcript: {e}")
            raise


class PatientService:
    """Service for managing patient records"""
    
    @staticmethod
    async def get_or_create_patient(
        phone: str,
        name: Optional[str] = None,
        language: LanguageEnum = LanguageEnum.ENGLISH
    ) -> PatientRecord:
        """
        Get existing patient or create new one
        
        Args:
            phone: Patient phone number
            name: Patient name
            language: Preferred language
            
        Returns:
            Patient record
        """
        try:
            patient = await PatientRecord.find_one({"phone": phone})
            
            if patient:
                # Update last contact
                patient.last_contact = datetime.utcnow()
                patient.total_calls += 1
                await patient.save()
                
                logger.info(f"Found existing patient: {patient.name}")
            else:
                # Create new patient
                patient = PatientRecord(
                    phone=phone,
                    name=name or "Unknown",
                    preferred_language=language,
                    last_contact=datetime.utcnow(),
                    total_calls=1,
                )
                await patient.insert()
                
                logger.info(f"Created new patient record for {phone}")
            
            return patient
            
        except Exception as e:
            logger.error(f"Error getting/creating patient: {e}")
            raise
    
    @staticmethod
    async def update_patient_info(
        phone: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        language: Optional[LanguageEnum] = None
    ) -> Optional[PatientRecord]:
        """Update patient information"""
        try:
            patient = await PatientRecord.find_one({"phone": phone})
            if not patient:
                return None
            
            if name:
                patient.name = name
            if email:
                patient.email = email
            if language:
                patient.preferred_language = language
            
            patient.updated_at = datetime.utcnow()
            await patient.save()
            
            logger.info(f"Updated patient info for {phone}")
            return patient
            
        except Exception as e:
            logger.error(f"Error updating patient info: {e}")
            raise
    
    @staticmethod
    async def increment_appointment_count(phone: str) -> None:
        """Increment patient's appointment count"""
        try:
            patient = await PatientRecord.find_one({"phone": phone})
            if patient:
                patient.total_appointments += 1
                await patient.save()
                
        except Exception as e:
            logger.error(f"Error incrementing appointment count: {e}")


# Global service instances
conversation_service = ConversationService()
patient_service = PatientService()