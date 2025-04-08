#!/usr/bin/env python
'''
Test script for SMS functionality.
This script tests sending an SMS to a specific phone number.
'''

import os
import sys
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def test_sms():
    """Test sending an SMS message"""
    # Check if Twilio credentials are set
    required_vars = ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("Error: The following environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("Please set these variables in the environment or in a .env file.")
        return 1
    
    # Get Twilio credentials
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    # The number to send the test SMS to
    to_number = "01500302461"  # User's requested test number
    
    # Format the phone number if needed
    if not to_number.startswith('+'):
        to_number = f"+{to_number}"
    
    # Create Twilio client
    try:
        client = Client(account_sid, auth_token)
        
        # Send message
        message_body = "This is a test message from the educational platform."
        message = client.messages.create(
            body=message_body,
            from_=from_number,
            to=to_number
        )
        
        print(f"SMS sent successfully! SID: {message.sid}")
        print(f"Message sent to: {to_number}")
        return 0
        
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(test_sms())
