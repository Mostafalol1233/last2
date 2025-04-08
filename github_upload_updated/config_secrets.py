import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if present
load_dotenv()

def setup_secrets():
    """
    Set up API keys and secrets for the application.
    These variables should be set in the environment or a .env file.
    """
    
    # List of required secrets
    required_secrets = {
        'STRIPE_SECRET_KEY': "Stripe Secret API Key (e.g., sk_test_...)",
        'STRIPE_PUBLISHABLE_KEY': "Stripe Publishable API Key (e.g., pk_test_...)",
        'STRIPE_WEBHOOK_SECRET': "Stripe Webhook Secret (e.g., whsec_...)",
        'TWILIO_ACCOUNT_SID': "Twilio Account SID",
        'TWILIO_AUTH_TOKEN': "Twilio Auth Token",
        'TWILIO_PHONE_NUMBER': "Twilio Phone Number with country code (e.g., +1234567890)",
        'OPENAI_API_KEY': "OpenAI API Key for AI chat functionality"
    }
    
    # Check for missing secrets
    missing_secrets = [k for k in required_secrets if not os.environ.get(k)]
    
    # Log warnings for missing secrets
    if missing_secrets:
        logger.warning("The following environment variables are not set:")
        for secret in missing_secrets:
            logger.warning(f"  - {secret}: {required_secrets[secret]}")
        
        logger.info(
            "Set these environment variables or add them to a .env file in the root directory.\n"
            "Example .env file:\n"
            "STRIPE_SECRET_KEY=sk_test_...\n"
            "STRIPE_PUBLISHABLE_KEY=pk_test_...\n"
            "STRIPE_WEBHOOK_SECRET=whsec_...\n"
            "TWILIO_ACCOUNT_SID=AC...\n"
            "TWILIO_AUTH_TOKEN=...\n"
            "TWILIO_PHONE_NUMBER=+1234567890\n"
            "OPENAI_API_KEY=sk-..."
        )
    else:
        logger.info("All required environment variables are set.")
    
    # Return a dictionary of available secrets
    return {
        key: os.environ.get(key) for key in required_secrets
    }

# Initialize secrets on import
secrets = setup_secrets()

def get_stripe_keys():
    """Get Stripe API keys"""
    return {
        'secret_key': secrets.get('STRIPE_SECRET_KEY'),
        'publishable_key': secrets.get('STRIPE_PUBLISHABLE_KEY'),
        'webhook_secret': secrets.get('STRIPE_WEBHOOK_SECRET')
    }

def get_twilio_keys():
    """Get Twilio API keys"""
    return {
        'account_sid': secrets.get('TWILIO_ACCOUNT_SID'),
        'auth_token': secrets.get('TWILIO_AUTH_TOKEN'),
        'phone_number': secrets.get('TWILIO_PHONE_NUMBER')
    }

def get_openai_key():
    """Get OpenAI API key"""
    return secrets.get('OPENAI_API_KEY')

# Function to check if a service is configured
def is_service_configured(service_name):
    """
    Check if a specific service has all required environment variables set.
    
    Args:
        service_name: String indicating which service to check ('stripe', 'twilio', or 'openai')
        
    Returns:
        Boolean indicating whether the service is fully configured
    """
    if service_name.lower() == 'stripe':
        keys = ['STRIPE_SECRET_KEY', 'STRIPE_PUBLISHABLE_KEY', 'STRIPE_WEBHOOK_SECRET']
        return all(os.environ.get(key) for key in keys)
    
    elif service_name.lower() == 'twilio':
        keys = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
        return all(os.environ.get(key) for key in keys)
    
    elif service_name.lower() == 'openai':
        return bool(os.environ.get('OPENAI_API_KEY'))
    
    return False