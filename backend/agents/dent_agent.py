# from langchain.agents import AgentExecutor, create_structured_chat_agent
# from langchain.tools import Tool
# from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from ..core.llm_setup import groq_service
from ..core.language_service import language_service
from ..config.settings import settings


class DentalAgent:
    """AI Agent for handling dental clinic conversations"""
    
    def __init__(self, language: str = "en"):
        """
        Initialize dental agent
        
        Args:
            language: Language code for the conversation
        """
        self.language = language
        self.conversation_state = {
            "stage": "greeting",  # greeting, collecting_info, confirming, closing
            "collected_data": {},
        }
        
        # System prompts by language
        self.system_prompts = {
            "en": self._get_english_system_prompt(),
            "ml": self._get_malayalam_system_prompt(),
            "hi": self._get_hindi_system_prompt(),
            "ta": self._get_tamil_system_prompt(),
        }
        
        logger.info(f"Dental agent initialized for language: {language}")
    
    def _get_english_system_prompt(self) -> str:
        """Get English system prompt"""
        return f"""You are an AI assistant for {settings.CLINIC_NAME}, a dental clinic.
Your role is to help patients book appointments over the phone.

Clinic Information:
- Name: {settings.CLINIC_NAME}
- Address: {settings.CLINIC_ADDRESS}
- Phone: {settings.CLINIC_PHONE}
- Working Hours: {settings.CLINIC_WORKING_HOURS}
- Working Days: {settings.CLINIC_WORKING_DAYS}

Your responsibilities:
1. Greet callers warmly and professionally
2. Understand their needs (appointment booking, inquiry, emergency)
3. Collect necessary information: name, phone number, preferred date and time
4. Confirm appointment details
5. Provide helpful information about the clinic
6. Handle emergencies by escalating to staff

Guidelines:
- Be warm, friendly, and professional
- Speak clearly and concisely
- Ask one question at a time
- Confirm understanding before moving forward
- For emergencies, advise immediate visit or call emergency services
- Keep responses brief for phone conversations

Current date: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _get_malayalam_system_prompt(self) -> str:
        """Get Malayalam system prompt"""
        return f"""നിങ്ങൾ {settings.CLINIC_NAME} എന്ന ഡെന്റൽ ക്ലിനിക്കിന്റെ AI അസിസ്റ്റന്റാണ്.
ഫോണിലൂടെ രോഗികളെ അപ്പോയിന്റ്മെന്റ് ബുക്ക് ചെയ്യാൻ സഹായിക്കുക എന്നതാണ് നിങ്ങളുടെ റോൾ.

ക്ലിനിക് വിവരങ്ങൾ:
- പേര്: {settings.CLINIC_NAME}
- വിലാസം: {settings.CLINIC_ADDRESS}
- ഫോൺ: {settings.CLINIC_PHONE}
- സമയം: {settings.CLINIC_WORKING_HOURS}
- പ്രവൃത്തി ദിവസങ്ങൾ: {settings.CLINIC_WORKING_DAYS}

നിങ്ങളുടെ ഉത്തരവാദിത്തങ്ങൾ:
1. വിളിക്കുന്നവരെ സ്നേഹപൂർവ്വം സ്വീകരിക്കുക
2. അവരുടെ ആവശ്യങ്ങൾ മനസ്സിലാക്കുക
3. ആവശ്യമായ വിവരങ്ങൾ ശേഖരിക്കുക: പേര്, ഫോൺ നമ്പർ, തീയതി, സമയം
4. അപ്പോയിന്റ്മെന്റ് വിശദാംശങ്ങൾ സ്ഥിരീകരിക്കുക
5. ക്ലിനിക്കിനെ കുറിച്ച് സഹായകരമായ വിവരങ്ങൾ നൽകുക

മാർഗ്ഗനിർദ്ദേശങ്ങൾ:
- സ്നേഹപൂർവ്വവും പ്രൊഫഷണലും ആയിരിക്കുക
- വ്യക്തമായും സംക്ഷിപ്തമായും സംസാരിക്കുക
- ഒരു സമയം ഒരു ചോദ്യം മാത്രം ചോദിക്കുക
- ഫോൺ സംഭാഷണങ്ങൾക്കായി ഹ്രസ്വ പ്രതികരണങ്ങൾ നൽകുക

ഇന്നത്തെ തീയതി: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _get_hindi_system_prompt(self) -> str:
        """Get Hindi system prompt"""
        return f"""आप {settings.CLINIC_NAME} डेंटल क्लिनिक के AI सहायक हैं।
फोन पर मरीजों को अपॉइंटमेंट बुक करने में मदद करना आपकी भूमिका है।

क्लिनिक की जानकारी:
- नाम: {settings.CLINIC_NAME}
- पता: {settings.CLINIC_ADDRESS}
- फोन: {settings.CLINIC_PHONE}
- समय: {settings.CLINIC_WORKING_HOURS}
- कार्य दिवस: {settings.CLINIC_WORKING_DAYS}

आपकी जिम्मेदारियां:
1. कॉल करने वालों का स्वागत करें
2. उनकी जरूरतों को समझें
3. आवश्यक जानकारी एकत्र करें: नाम, फोन नंबर, तारीख, समय
4. अपॉइंटमेंट विवरण की पुष्टि करें
5. क्लिनिक के बारे में सहायक जानकारी प्रदान करें

दिशानिर्देश:
- गर्मजोशी और पेशेवर बनें
- स्पष्ट और संक्षिप्त बोलें
- एक समय में एक प्रश्न पूछें
- फोन बातचीत के लिए संक्षिप्त प्रतिक्रियाएं दें

आज की तारीख: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    def _get_tamil_system_prompt(self) -> str:
        """Get Tamil system prompt"""
        return f"""நீங்கள் {settings.CLINIC_NAME} பல் மருத்துவ கிளினிக்கின் AI உதவியாளர்.
தொலைபேசியில் நோயாளிகளுக்கு சந்திப்புகளை பதிவு செய்ய உதவுவது உங்கள் பங்கு.

கிளினிக் தகவல்:
- பெயர்: {settings.CLINIC_NAME}
- முகவரி: {settings.CLINIC_ADDRESS}
- தொலைபேசி: {settings.CLINIC_PHONE}
- நேரம்: {settings.CLINIC_WORKING_HOURS}
- வேலை நாட்கள்: {settings.CLINIC_WORKING_DAYS}

உங்கள் பொறுப்புகள்:
1. அழைப்பவர்களை அன்புடன் வரவேற்கவும்
2. அவர்களின் தேவைகளைப் புரிந்து கொள்ளுங்கள்
3. தேவையான தகவலை சேகரிக்கவும்: பெயர், தொலைபேசி, தேதி, நேரம்
4. சந்திப்பு விவரங்களை உறுதிப்படுத்தவும்
5. கிளினிக் பற்றி பயனுள்ள தகவல்களை வழங்கவும்

வழிகாட்டுதல்கள்:
- அன்பாகவும் தொழில்முறையாகவும் இருங்கள்
- தெளிவாகவும் சுருக்கமாகவும் பேசுங்கள்
- ஒரு நேரத்தில் ஒரு கேள்வி கேளுங்கள்
- தொலைபேசி உரையாடல்களுக்கு சுருக்கமான பதில்களை வழங்கவும்

இன்றைய தேதி: {datetime.now().strftime('%Y-%m-%d')}
"""
    
    async def process_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, any]:
        """
        Process user message and generate response
        
        Args:
            message: User's message
            conversation_history: Previous conversation
            
        Returns:
            Dictionary with response and extracted data
        """
        try:
            # Get system prompt for current language
            system_prompt = self.system_prompts.get(
                self.language,
                self.system_prompts["en"]
            )
            
            # Detect intent
            intent = await groq_service.detect_intent(message, self.language)
            logger.debug(f"Detected intent: {intent}")
            
            # Extract entities
            entities = await groq_service.extract_entities(message, self.language)
            logger.debug(f"Extracted entities: {entities}")
            
            # Update collected data
            self.conversation_state["collected_data"].update(
                {k: v for k, v in entities.items() if v}
            )
            
            # Generate contextual response
            response_text = await self._generate_contextual_response(
                message=message,
                intent=intent,
                entities=entities,
                conversation_history=conversation_history,
                system_prompt=system_prompt
            )
            
            return {
                "response": response_text,
                "intent": intent,
                "entities": entities,
                "collected_data": self.conversation_state["collected_data"],
                "stage": self.conversation_state["stage"],
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": language_service.get_template("error", self.language),
                "intent": "error",
                "entities": {},
                "collected_data": self.conversation_state["collected_data"],
                "stage": self.conversation_state["stage"],
            }
    
    async def _generate_contextual_response(
        self,
        message: str,
        intent: str,
        entities: Dict,
        conversation_history: Optional[List[Dict[str, str]]],
        system_prompt: str
    ) -> str:
        """Generate contextual response based on conversation state"""
        
        # Determine what information is still needed
        collected = self.conversation_state["collected_data"]
        missing_fields = []
        
        required_fields = ["patient_name", "phone", "appointment_date", "appointment_time"]
        for field in required_fields:
            if field not in collected or not collected[field]:
                missing_fields.append(field)
        
        # Build context for LLM
        context = f"\nConversation Stage: {self.conversation_state['stage']}\n"
        context += f"Collected Information: {collected}\n"
        context += f"Missing Information: {missing_fields}\n"
        context += f"User Intent: {intent}\n\n"
        
        if missing_fields:
            context += f"Ask for the next missing field: {missing_fields[0]}\n"
        else:
            context += "All information collected. Confirm the appointment details.\n"
        
        full_prompt = system_prompt + context
        
        # Generate response
        response = await groq_service.generate_response(
            message=message,
            conversation_history=conversation_history,
            system_prompt=full_prompt
        )
        
        # Update conversation stage
        if not missing_fields and self.conversation_state["stage"] != "confirming":
            self.conversation_state["stage"] = "confirming"
        elif missing_fields and self.conversation_state["stage"] == "greeting":
            self.conversation_state["stage"] = "collecting_info"
        
        return response
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.conversation_state = {
            "stage": "greeting",
            "collected_data": {},
        }
        logger.debug("Conversation state reset")
    
    def get_collected_data(self) -> Dict:
        """Get all collected data"""
        return self.conversation_state["collected_data"]
    
    def is_appointment_ready(self) -> bool:
        """Check if all required appointment data is collected"""
        required = ["patient_name", "phone", "appointment_date", "appointment_time"]
        collected = self.conversation_state["collected_data"]
        return all(field in collected and collected[field] for field in required)


# Factory function to create agent instances
def create_dental_agent(language: str = "en") -> DentalAgent:
    """
    Create a new dental agent instance
    
    Args:
        language: Language code
        
    Returns:
        DentalAgent instance
    """
    return DentalAgent(language=language)