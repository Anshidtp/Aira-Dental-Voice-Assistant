from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from backend.database.connect import Database

db = Database.get_db()


router = APIRouter()


@router.post("/livekit")
async def livekit_webhook(
    request: Request,
    db: AsyncSession = Depends(db)
):
    """
    Handle LiveKit webhooks
    
    Events include:
    - room_started
    - room_finished
    - participant_joined
    - participant_left
    - track_published
    - track_unpublished
    """
    try:
        # Get webhook payload
        payload = await request.json()
        event = payload.get("event")
        
        logger.info(f"Received LiveKit webhook: {event}")
        
        if event == "room_started":
            logger.info(f"Room started: {payload.get('room', {}).get('name')}")
        
        elif event == "room_finished":
            logger.info(f"Room finished: {payload.get('room', {}).get('name')}")
        
        elif event == "participant_joined":
            participant = payload.get("participant", {})
            logger.info(f"Participant joined: {participant.get('identity')}")
        
        elif event == "participant_left":
            participant = payload.get("participant", {})
            logger.info(f"Participant left: {participant.get('identity')}")
        
        elif event == "track_published":
            track = payload.get("track", {})
            logger.info(f"Track published: {track.get('type')}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/twilio")
async def twilio_webhook(request: Request):
    """
    Handle Twilio webhooks for phone calls
    """
    try:
        # Get form data from Twilio
        form_data = await request.form()
        
        call_sid = form_data.get("CallSid")
        from_number = form_data.get("From")
        to_number = form_data.get("To")
        call_status = form_data.get("CallStatus")
        
        logger.info(f"Twilio webhook - CallSid: {call_sid}, Status: {call_status}")
        
        # Handle different call statuses
        if call_status == "ringing":
            # Call is ringing
            pass
        elif call_status == "in-progress":
            # Call answered
            pass
        elif call_status == "completed":
            # Call ended
            pass
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"Error processing Twilio webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))