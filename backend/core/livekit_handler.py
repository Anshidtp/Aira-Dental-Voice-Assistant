from livekit import api, rtc
from typing import Optional, Dict
import secrets
from loguru import logger

from ..config.settings import settings


class LiveKitHandler:
    """Handler for LiveKit real-time communication"""
    
    def __init__(self):
        """Initialize LiveKit handler"""
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self.url = settings.LIVEKIT_URL
        
        logger.info(f"LiveKit handler initialized with URL: {self.url}")
    
    def generate_room_name(self, prefix: Optional[str] = None) -> str:
        """
        Generate a unique room name
        
        Args:
            prefix: Optional prefix for room name
            
        Returns:
            Unique room name
        """
        prefix = prefix or settings.LIVEKIT_ROOM_PREFIX
        unique_id = secrets.token_urlsafe(8)
        room_name = f"{prefix}{unique_id}"
        logger.debug(f"Generated room name: {room_name}")
        return room_name
    
    async def create_access_token(
        self,
        room_name: str,
        participant_identity: str,
        participant_name: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> str:
        """
        Create an access token for a participant to join a room
        
        Args:
            room_name: Name of the room
            participant_identity: Unique identity for participant
            participant_name: Display name for participant
            metadata: Optional metadata
            
        Returns:
            Access token string
        """
        try:
            token = api.AccessToken(self.api_key, self.api_secret)
            
            token = (
                token
                .with_identity(participant_identity)
                .with_name(participant_name or participant_identity)
                .with_grants(
                    api.VideoGrants(
                        room_join=True,
                        room=room_name,
                        can_publish=True,
                        can_subscribe=True,
                    )
                )
            )
            
            if metadata:
                token = token.with_metadata(str(metadata))
            
            jwt_token = token.to_jwt()
            logger.info(f"Created access token for {participant_identity} in room {room_name}")
            
            return jwt_token
            
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise
    
    async def create_room(
        self,
        room_name: str,
        empty_timeout: int = 300,
        max_participants: int = 2,
    ) -> Dict:
        """
        Create a LiveKit room
        
        Args:
            room_name: Name of the room
            empty_timeout: Timeout in seconds for empty room
            max_participants: Maximum number of participants
            
        Returns:
            Room information
        """
        try:
            livekit_api = api.LiveKitAPI(
                url=self.url,
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
            
            room = await livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=empty_timeout,
                    max_participants=max_participants,
                )
            )
            
            logger.info(f"Created room: {room_name}")
            return {
                "name": room.name,
                "sid": room.sid,
                "created_at": room.creation_time,
            }
            
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            raise
    
    async def get_room(self, room_name: str) -> Optional[Dict]:
        """
        Get room information
        
        Args:
            room_name: Name of the room
            
        Returns:
            Room information or None
        """
        try:
            livekit_api = api.LiveKitAPI(
                url=self.url,
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
            
            rooms = await livekit_api.room.list_rooms(
                api.ListRoomsRequest(names=[room_name])
            )
            
            if rooms.rooms:
                room = rooms.rooms[0]
                return {
                    "name": room.name,
                    "sid": room.sid,
                    "num_participants": room.num_participants,
                    "created_at": room.creation_time,
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting room: {e}")
            return None
    
    async def delete_room(self, room_name: str) -> bool:
        """
        Delete a room
        
        Args:
            room_name: Name of the room
            
        Returns:
            True if successful
        """
        try:
            livekit_api = api.LiveKitAPI(
                url=self.url,
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
            
            await livekit_api.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            
            logger.info(f"Deleted room: {room_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting room: {e}")
            return False
    
    async def list_participants(self, room_name: str) -> list:
        """
        List participants in a room
        
        Args:
            room_name: Name of the room
            
        Returns:
            List of participants
        """
        try:
            livekit_api = api.LiveKitAPI(
                url=self.url,
                api_key=self.api_key,
                api_secret=self.api_secret,
            )
            
            participants = await livekit_api.room.list_participants(
                api.ListParticipantsRequest(room=room_name)
            )
            
            return [
                {
                    "identity": p.identity,
                    "name": p.name,
                    "sid": p.sid,
                    "state": p.state,
                }
                for p in participants.participants
            ]
            
        except Exception as e:
            logger.error(f"Error listing participants: {e}")
            return []


# Global instance
livekit_handler = LiveKitHandler()