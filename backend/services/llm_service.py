from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import List, Dict, Optional
from loguru import logger

from ..config.settings import settings


class LLMService:
    """Service for interacting with Groq Cloud LLM"""
    
    def __init__(self):
        """Initialize Groq LLM service"""
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name=settings.GROQ_MODEL,
            temperature=settings.GROQ_TEMPERATURE,
            max_tokens=settings.GROQ_MAX_TOKENS,
        )
        logger.info(f"Groq LLM initialized with model: {settings.GROQ_MODEL}")
    
    async def generate_response(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Generate a response from the LLM
        
        Args:
            message: User's message
            conversation_history: Previous conversation messages
            system_prompt: System prompt for context
            
        Returns:
            LLM response text
        """
        try:
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            # Add conversation history
            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))
            
            # Add current message
            messages.append(HumanMessage(content=message))
            
            # Generate response
            response = await self.llm.ainvoke(messages)
            
            logger.debug(f"Generated response for message: {message[:50]}...")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            raise
    
    async def extract_entities(self, text: str, language: str = "en") -> Dict:
        """
        Extract entities from text (name, phone, date, time, etc.)
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            Dictionary of extracted entities
        """
        system_prompt = f"""
            You are an entity extraction assistant for a dental clinic appointment system.
            Extract the following entities from the user's message:
            - patient_name: Full name of the patient
            - phone: Phone number
            - email: Email address
            - appointment_date: Date in YYYY-MM-DD format
            - appointment_time: Time in HH:MM format (24-hour)
            - reason: Reason for appointment

            Language: {language}

            Return ONLY a JSON object with extracted entities. Use null for missing entities.
            Example: {{"patient_name": "John Doe", "phone": "+919876543210", "email": null, "appointment_date": "2024-03-15", "appointment_time": "10:00", "reason": "dental checkup"}}
            """
        
        try:
            response = await self.generate_response(
                message=text,
                system_prompt=system_prompt
            )
            
            # Parse JSON response
            import json
            entities = json.loads(response)
            logger.debug(f"Extracted entities: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {}
    
    async def detect_intent(self, text: str, language: str = "en") -> str:
        """
        Detect user intent from text
        
        Args:
            text: Input text
            language: Language code
            
        Returns:
            Intent string
        """
        system_prompt = f"""
            You are an intent detection assistant for a dental clinic.
            Detect the primary intent from the user's message.

            Possible intents:
            - book_appointment: User wants to book an appointment
            - cancel_appointment: User wants to cancel
            - reschedule_appointment: User wants to reschedule
            - inquiry: General inquiry about services
            - emergency: Dental emergency
            - greeting: Just greeting
            - other: Other intents

            Language: {language}

            Return ONLY the intent name, nothing else.
            """
        
        try:
            intent = await self.generate_response(
                message=text,
                system_prompt=system_prompt
            )
            
            intent = intent.strip().lower()
            logger.debug(f"Detected intent: {intent}")
            return intent
            
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            return "other"


# Global instance
groq_service = LLMService()