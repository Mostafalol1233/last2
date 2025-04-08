import os
import argparse
import json

def main():
    """
    Configure environment variables for the application
    This script helps set up the necessary environment variables for the application
    including payment processors and SMS services.
    """
    parser = argparse.ArgumentParser(description='Configure application environment variables')
    parser.add_argument('--env-file', default='.env', help='Path to .env file')
    parser.add_argument('--stripe-key', help='Stripe API Secret Key')
    parser.add_argument('--stripe-webhook-secret', help='Stripe Webhook Secret')
    parser.add_argument('--twilio-sid', help='Twilio Account SID')
    parser.add_argument('--twilio-token', help='Twilio Auth Token')
    parser.add_argument('--twilio-phone', help='Twilio Phone Number')
    parser.add_argument('--db-url', help='Database URL (for Vercel)')
    
    args = parser.parse_args()
    
    # Initialize environment variables
    env_vars = {}
    
    # Try to load existing .env file if it exists
    if os.path.exists(args.env_file):
        with open(args.env_file, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    env_vars[key] = value
    
    # Update with provided arguments
    if args.stripe_key:
        env_vars['STRIPE_SECRET_KEY'] = args.stripe_key
    
    if args.stripe_webhook_secret:
        env_vars['STRIPE_WEBHOOK_SECRET'] = args.stripe_webhook_secret
    
    if args.twilio_sid:
        env_vars['TWILIO_ACCOUNT_SID'] = args.twilio_sid
    
    if args.twilio_token:
        env_vars['TWILIO_AUTH_TOKEN'] = args.twilio_token
    
    if args.twilio_phone:
        env_vars['TWILIO_PHONE_NUMBER'] = args.twilio_phone
    
    if args.db_url:
        env_vars['DATABASE_URL'] = args.db_url
    
    # Write environment variables to .env file
    with open(args.env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print(f"Environment configuration saved to {args.env_file}")
    
    # Generate Vercel configuration file
    vercel_config = {
        "env": {k: {"value": v} for k, v in env_vars.items()},
        "build": {
            "env": {k: {"value": v} for k, v in env_vars.items()}
        }
    }
    
    with open('vercel.json', 'w') as f:
        json.dump(vercel_config, f, indent=2)
    
    print("Vercel configuration saved to vercel.json")

if __name__ == "__main__":
    main()