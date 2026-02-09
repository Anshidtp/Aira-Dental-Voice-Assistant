from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger
import uuid

from backend.models.database import LanguageEnum
from backend.models.schemas import (
    LiveKitTokenRequest,
    LiveKitTokenResponse,
    IncomingCallRequest,
    VoiceResponse
)
from backend.core.livekit_handler import livekit_handler
from backend.core.language_service import language_service
from backend.agents.dent_agent import create_dental_agent
from backend.services.conversation_service import conversation_service, patient_service
from backend.config.settings import settings


router = APIRouter()


# Store active conversations (in production, use Redis)
active_conversations = {}


@router.post("/incoming-call", response_model=VoiceResponse)
async def handle_incoming_call(
    request: IncomingCallRequest,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming call - Create room and session
    
    Args:
        request: Incoming call data
        
    Returns:
        Voice response with session and room info
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Detect initial language based on phone number
        initial_language = language_service.get_initial_language(request.caller_phone)
        
        # Create LiveKit room
        room_name = livekit_handler.generate_room_name()
        
        await livekit_handler.create_room(
            room_name=room_name,
            empty_timeout=settings.AI_CONVERSATION_TIMEOUT,
            max_participants=2,
        )
        
        # Create conversation record
        conversation = await conversation_service.create_conversation(
            session_id=session_id,
            caller_phone=request.caller_phone,
            language=LanguageEnum(initial_language),
            room_name=room_name,
        )
        
        # Get or create patient record
        await patient_service.get_or_create_patient(
            phone=request.caller_phone,
            name=request.caller_name,
            language=LanguageEnum(initial_language),
        )
        
        # Create dental agent for this conversation
        agent = create_dental_agent(language=initial_language)
        active_conversations[session_id] = {
            "agent": agent,
            "conversation_id": str(conversation.id),
            "language": initial_language,
        }
        
        # Generate access token for caller
        token = await livekit_handler.create_access_token(
            room_name=room_name,
            participant_identity=request.caller_phone,
            participant_name=request.caller_name or "Caller",
            metadata={"session_id": session_id, "phone": request.caller_phone}
        )
        
        logger.info(f"Created session {session_id} for caller {request.caller_phone}")
        
        return VoiceResponse(
            success=True,
            message="Call session created",
            session_id=session_id,
            room_name=room_name,
            token=token
        )
        
    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token", response_model=LiveKitTokenResponse)
async def get_livekit_token(request: LiveKitTokenRequest):
    """
    Get LiveKit access token for joining a room
    
    Args:
        request: Token request data
        
    Returns:
        LiveKit token response
    """
    try:
        token = await livekit_handler.create_access_token(
            room_name=request.room_name,
            participant_identity=request.participant_name,
            participant_name=request.participant_name,
            metadata=request.metadata
        )
        
        return LiveKitTokenResponse(
            token=token,
            room_name=request.room_name,
            url=settings.LIVEKIT_URL
        )
        
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end-call/{session_id}")
async def end_call(session_id: str):
    """
    End a call session
    
    Args:
        session_id: Session ID
        
    Returns:
        Success response
    """
    try:
        # Get conversation from active sessions
        if session_id in active_conversations:
            conv_data = active_conversations[session_id]
            
            # Update conversation record
            conversation = await conversation_service.get_conversation_by_session(session_id)
            
            if conversation:
                # End conversation
                await conversation_service.end_conversation(
                    session_id=session_id,
                    appointment_id=conv_data.get("appointment_id")
                )
                
                # Delete LiveKit room
                if conversation.room_name:
                    await livekit_handler.delete_room(conversation.room_name)
            
            # Remove from active conversations
            del active_conversations[session_id]
            
            logger.info(f"Ended call session {session_id}")
        
        return {"success": True, "message": "Call ended"}
        
    except Exception as e:
        logger.error(f"Error ending call: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-sessions")
async def get_active_sessions():
    """Get list of active call sessions"""
    try:
        sessions = [
            {
                "session_id": sid,
                "language": data["language"],
                "conversation_id": data["conversation_id"]
            }
            for sid, data in active_conversations.items()
        ]
        
        return {
            "active_sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session/{session_id}/messages")
async def get_session_messages(session_id: str):
    """Get conversation messages for a session"""
    try:
        conversation = await conversation_service.get_conversation_by_session(session_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Session not found")
        
        messages = await conversation_service.get_conversation_messages(
            str(conversation.id)
        )
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "language": msg.language,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ],
            "count": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))