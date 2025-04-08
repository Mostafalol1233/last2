#!/usr/bin/env python
'''
Setup script for Vercel deployment.
This script creates the necessary folders and files for Vercel deployment.
'''

import os
import sys
import json
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def main():
    """Main function to setup Vercel deployment"""
    print("Setting up Vercel deployment...")
    
    # Ensure environment variables are set
    required_env_vars = [
        'DATABASE_URL',
        'SESSION_SECRET',
        'STRIPE_SECRET_KEY',
        'STRIPE_PUBLISHABLE_KEY',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER'
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("Warning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"  - {var}")
        print("These variables will need to be configured in the Vercel dashboard.")
    
    # Create folders if they don't exist
    folders = ['static', 'templates', 'instance']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created folder: {folder}")
    
    # Ensure requirements.txt exists
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w') as f:
            f.write("flask\n")
            f.write("flask-sqlalchemy\n")
            f.write("flask-login\n")
            f.write("flask-wtf\n")
            f.write("gunicorn\n")
            f.write("python-dotenv\n")
            f.write("stripe\n")
            f.write("twilio\n")
            f.write("psycopg2-binary\n")
            f.write("werkzeug\n")
            f.write("openai\n")
            f.write("email-validator\n")
        print("Created requirements.txt file")
    
    # Create .vercelignore file
    with open('.vercelignore', 'w') as f:
        f.write("__pycache__\n")
        f.write("*.pyc\n")
        f.write(".env\n")
        f.write(".git\n")
        f.write(".gitignore\n")
        f.write(".venv\n")
        f.write("venv\n")
        f.write("env\n")
    print("Created .vercelignore file")
    
    print("Vercel setup completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
