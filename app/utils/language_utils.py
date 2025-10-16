"""Language utilities for multilingual support."""

# Simple language detection and translation utilities
# In a production environment, you might want to use services like Google Translate API

SUPPORTED_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic'
}

# Basic translations for common phrases
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome to our clinic!',
        'how_can_help': 'How can I help you today?',
        'appointment_scheduled': 'Your appointment has been scheduled.',
        'thank_you': 'Thank you!',
        'goodbye': 'Goodbye! Have a great day!',
        'error': 'I apologize, but I encountered an error.',
        'contact_staff': 'Please contact our staff for assistance.'
    },
    'es': {
        'welcome': '¡Bienvenido a nuestra clínica!',
        'how_can_help': '¿Cómo puedo ayudarte hoy?',
        'appointment_scheduled': 'Su cita ha sido programada.',
        'thank_you': '¡Gracias!',
        'goodbye': '¡Adiós! ¡Que tengas un gran día!',
        'error': 'Me disculpo, pero encontré un error.',
        'contact_staff': 'Por favor contacte a nuestro personal para asistencia.'
    },
    'fr': {
        'welcome': 'Bienvenue dans notre clinique!',
        'how_can_help': 'Comment puis-je vous aider aujourd\'hui?',
        'appointment_scheduled': 'Votre rendez-vous a été programmé.',
        'thank_you': 'Merci!',
        'goodbye': 'Au revoir! Passez une excellente journée!',
        'error': 'Je m\'excuse, mais j\'ai rencontré une erreur.',
        'contact_staff': 'Veuillez contacter notre personnel pour assistance.'
    }
}

def detect_language(text):
    """
    Simple language detection based on common words.
    In production, use a proper language detection library.
    """
    text_lower = text.lower()
    
    # Spanish indicators
    spanish_words = ['hola', 'gracias', 'por favor', 'sí', 'no', 'cómo', 'qué', 'dónde', 'cuándo']
    if any(word in text_lower for word in spanish_words):
        return 'es'
    
    # French indicators
    french_words = ['bonjour', 'merci', 's\'il vous plaît', 'oui', 'non', 'comment', 'que', 'où', 'quand']
    if any(word in text_lower for word in french_words):
        return 'fr'
    
    # Default to English
    return 'en'

def translate_text(text, target_language, source_language='en'):
    """
    Simple translation using predefined phrases.
    In production, use Google Translate API or similar service.
    """
    if target_language == source_language:
        return text
    
    # Check if we have a translation for this text
    if source_language in TRANSLATIONS and target_language in TRANSLATIONS:
        source_translations = TRANSLATIONS[source_language]
        target_translations = TRANSLATIONS[target_language]
        
        # Find the key for the source text
        for key, value in source_translations.items():
            if value.lower() == text.lower():
                return target_translations.get(key, text)
    
    # If no translation found, return original text
    return text

def get_language_name(language_code):
    """Get the full name of a language from its code."""
    return SUPPORTED_LANGUAGES.get(language_code, 'Unknown')

def is_supported_language(language_code):
    """Check if a language is supported."""
    return language_code in SUPPORTED_LANGUAGES

def get_supported_languages():
    """Get all supported languages."""
    return SUPPORTED_LANGUAGES