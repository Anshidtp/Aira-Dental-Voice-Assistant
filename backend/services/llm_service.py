from typing import List, Dict, Any, Optional, AsyncIterator
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_classic.chains import LLMChain
from ..config import settings
from ..utils.logger import log


class llmService:
    """
    Unified LLM service using Groq Llama for all operations
    Used for both web chat and telephony
    """
    
    def __init__(self):
        self.api_key = settings.groq_api_key
        self.model_name = settings.groq_model
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            api_key=self.api_key,
            model_name=self.model_name,
            temperature=settings.groq_temperature,
            max_tokens=settings.groq_max_tokens,
            top_p=settings.groq_top_p,
            timeout=30.0,
            max_retries=2,
        )
        
        log.info(f"Unified Groq service initialized with model: {self.model_name}")
    
    async def generate(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate response from messages
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream response
            temperature: Optional temperature override
            max_tokens: Optional max tokens override
        
        Returns:
            Generated response text
        """
        try:
            # Convert to LangChain format
            langchain_messages = self._convert_messages(messages)
            
            # Create temporary LLM with overrides if needed
            llm = self.llm
            if temperature is not None or max_tokens is not None:
                llm = ChatGroq(
                    api_key=self.api_key,
                    model_name=self.model_name,
                    temperature=temperature or settings.groq_temperature,
                    max_tokens=max_tokens or settings.groq_max_tokens,
                    top_p=settings.groq_top_p,
                    timeout=30.0,
                    max_retries=2,
                )
            
            if stream:
                # Streaming response
                full_response = ""
                async for chunk in llm.astream(langchain_messages):
                    full_response += chunk.content
                return full_response
            else:
                # Non-streaming response
                response = await llm.ainvoke(langchain_messages)
                return response.content
                
        except Exception as e:
            log.error(f"Error generating response: {e}")
            raise
    
    async def generate_streaming(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        """
        Generate streaming response
        
        Args:
            messages: List of message dictionaries
        
        Yields:
            Response chunks
        """
        try:
            langchain_messages = self._convert_messages(messages)
            
            async for chunk in self.llm.astream(langchain_messages):
                if chunk.content:
                    yield chunk.content
                    
        except Exception as e:
            log.error(f"Error in streaming: {e}")
            raise
    
    def create_conversation_chain(
        self,
        system_prompt: str,
        memory_key: str = "chat_history"
    ) -> ConversationChain:
        """
        Create conversation chain with memory
        
        Args:
            system_prompt: System prompt for conversation
            memory_key: Key for conversation memory
        
        Returns:
            ConversationChain instance
        """
        # Create memory
        memory = ConversationBufferMemory(
            memory_key=memory_key,
            return_messages=True
        )
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name=memory_key),
            ("human", "{input}")
        ])
        
        # Create conversation chain
        chain = ConversationChain(
            llm=self.llm,
            memory=memory,
            prompt=prompt,
            verbose=settings.debug
        )
        
        return chain
    
    def _convert_messages(
        self,
        messages: List[Dict[str, str]]
    ) -> List[Any]:
        """Convert message dictionaries to LangChain format"""
        langchain_messages = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                langchain_messages.append(SystemMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            else:
                langchain_messages.append(HumanMessage(content=content))
        
        return langchain_messages
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {
            "provider": "groq",
            "model": self.model_name,
            "temperature": settings.groq_temperature,
            "max_tokens": settings.groq_max_tokens,
            "top_p": settings.groq_top_p,
            "status": "active",
            "use_case": "unified (web + telephony)"
        }


class ConversationManager:
    """
    Manages conversation state and context
    Used for both web and telephony conversations
    """
    
    def __init__(
        self,
        session_id: str,
        language: str = "en",
        channel: str = "unknown"
    ):
        self.session_id = session_id
        self.language = language
        self.channel = channel  # 'web' or 'telephony'
        self.conversation_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.groq_service = llmService()
        
        log.info(f"Conversation manager created: {session_id} ({channel}, {language})")
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": self._get_timestamp(),
            "metadata": metadata or {}
        })
    
    def get_messages_for_llm(self) -> List[Dict[str, str]]:
        """Get conversation history in LLM format"""
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in self.conversation_history
        ]
    
    async def generate_response(
        self,
        user_message: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate AI response
        
        Args:
            user_message: User's message
            system_prompt: Optional system prompt override
            temperature: Optional temperature override
        
        Returns:
            AI response
        """
        # Add user message
        self.add_message("user", user_message)
        
        # Prepare messages
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend(self.get_messages_for_llm())
        
        # Generate response
        response = await self.groq_service.generate(
            messages=messages,
            temperature=temperature
        )
        
        # Add assistant response
        self.add_message("assistant", response)
        
        return response
    
    def update_context(self, key: str, value: Any):
        """Update conversation context"""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context value"""
        return self.context.get(key, default)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            "session_id": self.session_id,
            "channel": self.channel,
            "language": self.language,
            "message_count": len(self.conversation_history),
            "context": self.context,
            "duration": self._calculate_duration()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
    
    def _calculate_duration(self) -> float:
        """Calculate conversation duration in seconds"""
        if len(self.conversation_history) < 2:
            return 0.0
        
        from datetime import datetime
        start = datetime.fromisoformat(self.conversation_history[0]["timestamp"])
        end = datetime.fromisoformat(self.conversation_history[-1]["timestamp"])
        return (end - start).total_seconds()


# Global instance
groq_service = llmService()

# Active conversations storage (use Redis in production)
active_conversations: Dict[str, ConversationManager] = {}


def get_or_create_conversation(
    session_id: str,
    language: str = "en",
    channel: str = "unknown"
) -> ConversationManager:
    """Get or create conversation manager"""
    if session_id not in active_conversations:
        active_conversations[session_id] = ConversationManager(
            session_id=session_id,
            language=language,
            channel=channel
        )
    return active_conversations[session_id]


def end_conversation(session_id: str) -> Optional[Dict[str, Any]]:
    """End conversation and return summary"""
    if session_id in active_conversations:
        conversation = active_conversations[session_id]
        summary = conversation.get_summary()
        del active_conversations[session_id]
        return summary
    return None