import openai
from flask import current_app
from app.models import FAQ, Patient, Appointment, AftercareInstruction, ChatSession, ClinicSettings, Doctor, BookingSettings
from app.utils.language_utils import translate_text, detect_language
import json
import re
from datetime import datetime, timedelta

class ChatbotService:
    """Service for handling chatbot interactions using OpenAI API."""
    
    def __init__(self):
        self.client = None
        self._system_prompt_cache = None
    
    def _initialize_client(self):
        """Initialize OpenAI client if not already done."""
        if not self.client:
            api_key = current_app.config.get('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.client = openai
    
    def _get_system_prompt(self):
        """Get the system prompt for the AI assistant with dynamic clinic information."""
        # Use cached prompt if available
        if self._system_prompt_cache:
            return self._system_prompt_cache
            
        # Get clinic settings
        clinic_settings = ClinicSettings.query.first()
        
        clinic_name = clinic_settings.clinic_name if clinic_settings else "Medical Clinic"
        clinic_info = ""
        
        if clinic_settings:
            clinic_info = f"""
CLINIC INFORMATION:
- Name: {clinic_settings.clinic_name}
- Phone: {clinic_settings.phone or 'Contact us for phone number'}
- Email: {clinic_settings.email or 'Contact us for email'}
- Address: {self._format_address(clinic_settings)}
- Website: {clinic_settings.website or 'Not available'}

OPERATING HOURS:
{self._format_operating_hours(clinic_settings.operating_hours)}

DEPARTMENTS/SERVICES:
{self._format_departments(clinic_settings.departments)}
"""
        
        prompt = f"""You are a helpful AI assistant for {clinic_name}. Your role is to:

1. Help patients with appointment scheduling
2. Answer frequently asked questions about the clinic
3. Collect patient intake information
4. Provide aftercare instructions when appropriate
5. Guide patients through the clinic's services

{clinic_info}

Guidelines:
- Be professional, empathetic, and helpful
- Never provide medical diagnoses or treatment advice
- Always recommend consulting with healthcare professionals for medical concerns
- Collect necessary information step by step
- Be clear about what information you need and why
- Respect patient privacy and confidentiality
- If you cannot help with something, politely explain and suggest alternatives
- Use the clinic information above to answer questions about hours, location, services, etc.

Available actions you can perform:
- SCHEDULE_APPOINTMENT: Help schedule appointments
- COLLECT_INTAKE: Collect patient intake information
- PROVIDE_FAQ: Answer frequently asked questions
- PROVIDE_AFTERCARE: Provide aftercare instructions
- GENERAL_HELP: Provide general assistance

Always respond in a conversational, friendly manner while maintaining professionalism."""
        
        # Cache the prompt
        self._system_prompt_cache = prompt
        return prompt

    def _format_address(self, clinic_settings):
        """Format clinic address for display."""
        address_parts = []
        if clinic_settings.address_line1:
            address_parts.append(clinic_settings.address_line1)
        if clinic_settings.address_line2:
            address_parts.append(clinic_settings.address_line2)
        if clinic_settings.city:
            city_state = clinic_settings.city
            if clinic_settings.state:
                city_state += f", {clinic_settings.state}"
            if clinic_settings.zip_code:
                city_state += f" {clinic_settings.zip_code}"
            address_parts.append(city_state)
        if clinic_settings.country and clinic_settings.country != 'USA':
            address_parts.append(clinic_settings.country)
        
        return ", ".join(address_parts) if address_parts else "Address not available"

    def _format_operating_hours(self, operating_hours_json):
        """Format operating hours for display."""
        if not operating_hours_json:
            return "Operating hours not available"
        
        try:
            hours = json.loads(operating_hours_json)
            formatted_hours = []
            
            for day, info in hours.items():
                if info.get('closed', False):
                    formatted_hours.append(f"- {day.capitalize()}: Closed")
                else:
                    open_time = info.get('open', 'N/A')
                    close_time = info.get('close', 'N/A')
                    formatted_hours.append(f"- {day.capitalize()}: {open_time} - {close_time}")
            
            return "\n".join(formatted_hours)
        except (json.JSONDecodeError, AttributeError):
            return "Operating hours not available"

    def _format_departments(self, departments_json):
        """Format departments/services for display."""
        if not departments_json:
            return "Services information not available"
        
        try:
            departments = json.loads(departments_json)
            formatted_deps = []
            
            for dept in departments:
                name = dept.get('name', 'Unknown')
                description = dept.get('description', '')
                if description:
                    formatted_deps.append(f"- {name}: {description}")
                else:
                    formatted_deps.append(f"- {name}")
            
            return "\n".join(formatted_deps)
        except (json.JSONDecodeError, AttributeError):
            return "Services information not available"

    def process_message(self, message, session_id, language='en'):
        """Process a user message and return an appropriate response."""
        try:
            self._initialize_client()
            
            # Detect intent from the message
            intent = self._detect_intent(message)
            
            # Get conversation context
            context = self._get_conversation_context(session_id)
            
            # Process based on intent
            if intent == 'appointment_scheduling':
                return self._handle_appointment_scheduling(message, context, language)
            elif intent == 'faq':
                return self._handle_faq(message, language)
            elif intent == 'intake_form':
                return self._handle_intake_form(message, context, language)
            elif intent == 'aftercare':
                return self._handle_aftercare(message, language)
            else:
                return self._handle_general_conversation(message, context, language)
                
        except Exception as e:
            return {
                'message': 'I apologize, but I encountered an error. Please try again or contact our staff for assistance.',
                'type': 'error',
                'metadata': {'error': str(e)}
            }
    
    def _detect_intent(self, message):
        """Detect the intent of the user message."""
        message_lower = message.lower()
        
        # Appointment-related keywords
        appointment_keywords = ['appointment', 'schedule', 'book', 'reschedule', 'cancel', 'available', 'time', 'date']
        if any(keyword in message_lower for keyword in appointment_keywords):
            return 'appointment_scheduling'
        
        # FAQ-related keywords
        faq_keywords = ['hours', 'location', 'insurance', 'cost', 'price', 'services', 'doctor', 'clinic']
        if any(keyword in message_lower for keyword in faq_keywords):
            return 'faq'
        
        # Intake form keywords
        intake_keywords = ['symptoms', 'pain', 'medical history', 'allergies', 'medications', 'complaint']
        if any(keyword in message_lower for keyword in intake_keywords):
            return 'intake_form'
        
        # Aftercare keywords
        aftercare_keywords = ['aftercare', 'post-treatment', 'recovery', 'follow-up', 'instructions']
        if any(keyword in message_lower for keyword in aftercare_keywords):
            return 'aftercare'
        
        return 'general'
    
    def _get_conversation_context(self, session_id):
        """Get conversation context from the database."""
        session = ChatSession.query.filter_by(session_id=session_id).first()
        if session and session.messages:
            # Get last few messages for context
            recent_messages = session.messages[-5:]  # Last 5 messages
            return [{'sender': msg.sender, 'message': msg.message} for msg in recent_messages]
        return []
    
    def _handle_appointment_scheduling(self, message, context, language):
        """Handle appointment scheduling requests."""
        # Check if we have OpenAI API key
        if not current_app.config.get('OPENAI_API_KEY'):
            return self._handle_appointment_scheduling_fallback(message, context, language)
        
        try:
            # Use OpenAI to understand the appointment request
            prompt = f"""
            System: {self._get_system_prompt()}
            
            User message: {message}
            Context: {json.dumps(context)}
            
            The user wants to schedule an appointment. Extract the following information if available:
            - Preferred date and time
            - Type of appointment (consultation, follow-up, etc.)
            - Reason for visit
            - Patient contact information
            
            Respond with a helpful message and indicate what additional information is needed.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                'message': ai_response,
                'type': 'appointment_scheduling',
                'metadata': {'needs_followup': True}
            }
            
        except Exception as e:
            return self._handle_appointment_scheduling_fallback(message, context, language)
    
    def _handle_appointment_scheduling_fallback(self, message, context, language):
        """Fallback appointment scheduling without OpenAI."""
        # Get available doctors and booking settings
        doctors = Doctor.query.filter_by(is_active=True).all()
        booking_settings = BookingSettings.query.first()
        
        doctor_info = ""
        if doctors:
            doctor_list = []
            for doctor in doctors:
                specialization = f" ({doctor.specialization})" if doctor.specialization else ""
                doctor_list.append(f"- Dr. {doctor.first_name} {doctor.last_name}{specialization}")
            doctor_info = f"\n\nOur available doctors:\n" + "\n".join(doctor_list)
        
        booking_info = ""
        if booking_settings:
            slot_duration = booking_settings.slot_duration
            min_notice = booking_settings.min_booking_notice_hours
            advance_days = booking_settings.advance_booking_days
            booking_info = f"\n\nBooking Information:\n- Appointment duration: {slot_duration} minutes\n- Minimum notice required: {min_notice} hours\n- You can book up to {advance_days} days in advance"
        
        return {
            'message': f"I'd be happy to help you schedule an appointment! To get started, I'll need some information:\n\n1. What type of appointment do you need? (consultation, follow-up, etc.)\n2. Which doctor would you prefer to see?\n3. What is your preferred date and time?\n4. What is the reason for your visit?\n5. May I have your name and contact information?{doctor_info}{booking_info}\n\nPlease provide these details and I'll help you find the best available slot.",
            'type': 'appointment_scheduling',
            'metadata': {'step': 'collect_info', 'doctors': [d.to_dict() for d in doctors]}
        }
    
    def _handle_faq(self, message, language):
        """Handle FAQ requests."""
        # Search for relevant FAQs
        faqs = FAQ.query.filter_by(is_active=True, language=language).all()
        
        # Simple keyword matching for FAQ
        message_lower = message.lower()
        relevant_faqs = []
        
        for faq in faqs:
            if any(word in faq.question.lower() for word in message_lower.split()):
                relevant_faqs.append(faq)
        
        if relevant_faqs:
            # Return the most relevant FAQ
            faq = relevant_faqs[0]
            return {
                'message': f"**{faq.question}**\n\n{faq.answer}",
                'type': 'faq',
                'metadata': {'faq_id': faq.id, 'category': faq.category}
            }
        else:
            # If no FAQ matches, provide general clinic information
            clinic_settings = ClinicSettings.query.first()
            clinic_info_msg = "I don't have specific information about that topic, but here's some general information about our clinic:\n\n"
            
            if clinic_settings:
                if clinic_settings.phone:
                    clinic_info_msg += f"📞 Phone: {clinic_settings.phone}\n"
                if clinic_settings.email:
                    clinic_info_msg += f"📧 Email: {clinic_settings.email}\n"
                if clinic_settings.address_line1:
                    clinic_info_msg += f"📍 Address: {self._format_address(clinic_settings)}\n"
                
                # Add operating hours
                if clinic_settings.operating_hours:
                    clinic_info_msg += f"\n🕒 Operating Hours:\n{self._format_operating_hours(clinic_settings.operating_hours)}\n"
                
                # Add services
                if clinic_settings.departments:
                    clinic_info_msg += f"\n🏥 Our Services:\n{self._format_departments(clinic_settings.departments)}\n"
            
            clinic_info_msg += "\nFor specific questions, please contact our staff directly or try rephrasing your question."
            
            return {
                'message': clinic_info_msg,
                'type': 'faq',
                'metadata': {'no_match': True, 'clinic_info_provided': True}
            }
    
    def _handle_intake_form(self, message, context, language):
        """Handle intake form collection."""
        return {
            'message': "I'll help you complete your intake form. This information helps our medical team prepare for your visit.\n\nLet's start with your chief complaint - what is the main reason for your visit today?",
            'type': 'intake_form',
            'metadata': {'step': 'chief_complaint'}
        }
    
    def _handle_aftercare(self, message, language):
        """Handle aftercare instruction requests."""
        # Search for relevant aftercare instructions
        instructions = AftercareInstruction.query.filter_by(is_active=True, language=language).all()
        
        if instructions:
            # Return general aftercare information
            return {
                'message': "I can provide aftercare instructions for various treatments. What type of treatment or procedure did you have? For example:\n\n• General consultation\n• Minor procedure\n• Vaccination\n• Physical therapy\n\nPlease specify so I can provide the most relevant aftercare guidance.",
                'type': 'aftercare',
                'metadata': {'available_types': [inst.treatment_type for inst in instructions]}
            }
        else:
            return {
                'message': "For specific aftercare instructions, please refer to the information provided by your healthcare provider or contact our clinic directly. General aftercare tips include:\n\n• Follow all prescribed medications\n• Keep the treatment area clean and dry\n• Contact us if you experience unusual symptoms\n• Attend all follow-up appointments",
                'type': 'aftercare',
                'metadata': {}
            }
    
    def _handle_general_conversation(self, message, context, language):
        """Handle general conversation."""
        # Check if we have OpenAI API key for more sophisticated responses
        if not current_app.config.get('OPENAI_API_KEY'):
            return self._handle_general_conversation_fallback(message, context, language)
        
        try:
            # Use OpenAI for general conversation
            context_str = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in context[-3:]])
            
            prompt = f"""
            System: {self._get_system_prompt()}
            
            Previous conversation:
            {context_str}
            
            User: {message}
            
            Respond helpfully as a clinic AI assistant. Keep responses concise and professional.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return {
                'message': ai_response,
                'type': 'general',
                'metadata': {}
            }
            
        except Exception as e:
            return self._handle_general_conversation_fallback(message, context, language)
    
    def _handle_general_conversation_fallback(self, message, context, language):
        """Fallback general conversation without OpenAI."""
        greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        message_lower = message.lower()
        
        # Get clinic name for personalized greeting
        clinic_settings = ClinicSettings.query.first()
        clinic_name = clinic_settings.clinic_name if clinic_settings else "our clinic"
        
        if any(greeting in message_lower for greeting in greetings):
            return {
                'message': f"Hello! Welcome to {clinic_name}'s AI assistant. I'm here to help you with:\n\n• Scheduling appointments\n• Answering questions about our services\n• Collecting intake information\n• Providing aftercare instructions\n\nHow can I assist you today?",
                'type': 'greeting',
                'metadata': {}
            }
        
        return {
            'message': f"I'm here to help you with {clinic_name}-related questions and services. I can assist with appointment scheduling, answer frequently asked questions, help with intake forms, and provide aftercare information.\n\nWhat would you like help with today?",
            'type': 'general',
            'metadata': {}
        }