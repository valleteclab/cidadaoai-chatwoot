# Utility functions for the application
import hashlib
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)

def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())

def generate_hash(text: str) -> str:
    """Generate SHA-256 hash of text"""
    return hashlib.sha256(text.encode()).hexdigest()

def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)

def format_timestamp(dt: datetime) -> str:
    """Format datetime to ISO string"""
    return dt.isoformat()

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate Brazilian phone number format"""
    # Remove non-digit characters
    phone_digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid Brazilian phone number
    # Mobile: 11 digits (including area code)
    # Landline: 10 digits (including area code)
    return len(phone_digits) in [10, 11] and phone_digits.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9'))

def sanitize_text(text: str) -> str:
    """Sanitize text input by removing harmful characters"""
    if not text:
        return ""
    
    # Remove potential XSS characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()

def extract_entities(text: str) -> Dict[str, Any]:
    """Extract common entities from text (basic implementation)"""
    entities = {
        'emails': [],
        'phones': [],
        'urls': [],
        'cpfs': []
    }
    
    # Extract emails
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    entities['emails'] = re.findall(email_pattern, text)
    
    # Extract phone numbers
    phone_pattern = r'\b(?:\+55\s?)?(?:\(?[1-9]{2}\)?\s?)?(?:9\s?)?[0-9]{4}[-\s]?[0-9]{4}\b'
    entities['phones'] = re.findall(phone_pattern, text)
    
    # Extract URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    entities['urls'] = re.findall(url_pattern, text)
    
    # Extract CPF (basic pattern)
    cpf_pattern = r'\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b'
    entities['cpfs'] = re.findall(cpf_pattern, text)
    
    return entities

def mask_sensitive_data(text: str) -> str:
    """Mask sensitive information in text"""
    # Mask CPF
    text = re.sub(r'(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})', r'\1.***.***-\4', text)
    
    # Mask email
    text = re.sub(r'([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', 
                  lambda m: f"{m.group(1)[:2]}***@{m.group(2)}", text)
    
    # Mask phone numbers
    text = re.sub(r'(\d{2})(\d{4,5})(\d{4})', r'\1****\3', text)
    
    return text

def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate simple similarity between two texts (basic implementation)"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0

def format_response_for_chatwoot(message: str, message_type: str = "outgoing") -> Dict[str, Any]:
    """Format response for Chatwoot API"""
    return {
        "content": message,
        "message_type": message_type,
        "private": False,
        "content_type": "text"
    }

def log_api_call(endpoint: str, method: str, status_code: int, duration: float):
    """Log API call information"""
    logger.info(f"API Call - {method} {endpoint} - Status: {status_code} - Duration: {duration:.3f}s")

def handle_error(error: Exception, context: str = "") -> Dict[str, Any]:
    """Standard error handling"""
    error_id = generate_uuid()
    error_message = f"Error {error_id}: {str(error)}"
    
    if context:
        error_message = f"{context} - {error_message}"
    
    logger.error(error_message)
    
    return {
        "error_id": error_id,
        "message": "Ocorreu um erro interno. Tente novamente.",
        "details": str(error) if logger.level <= logging.DEBUG else None
    }
