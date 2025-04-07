# Vercel Deployment Guide

This guide provides detailed instructions for deploying the Educational Platform on Vercel.

## Prerequisites

Before deploying to Vercel, make sure you have the following:

1. A [Vercel account](https://vercel.com/signup)
2. The [Vercel CLI](https://vercel.com/download) installed (optional, for local development)
3. Required API keys set up:
   - Stripe API keys for payment processing
   - Twilio API keys for SMS functionality
   - OpenAI API key (if using AI features)
4. A database service (PostgreSQL) ready to use

## Step 1: Prepare Your Project

1. Make sure your code is ready for deployment
2. Run the Vercel setup script:
   ```
   python vercel_setup.py
   ```
3. This script will:
   - Ensure all required folders exist
   - Create a `.vercelignore` file
   - Ensure `requirements.txt` is up-to-date
   - Check for required environment variables

## Step 2: Set up a Database

1. Create a PostgreSQL database with your preferred provider (e.g., Railway, Supabase, Render, Neon)
2. Get the database connection URL in the format:
   ```
   postgresql://username:password@host:port/database
   ```

## Step 3: Deploy to Vercel

### Option 1: Deploy via Git Integration

1. Push your project to a Git repository (GitHub, GitLab, or Bitbucket)
2. Visit [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New" and select "Project"
4. Select your repository
5. Configure the project:
   - Framework Preset: Other
   - Build Command: Leave empty
   - Output Directory: Leave empty
   - Root Directory: Leave as `.`
6. Add Environment Variables:
   - `DATABASE_URL`: Your PostgreSQL connection URL
   - `SESSION_SECRET`: A strong random string for session security
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret (optional)
   - `TWILIO_ACCOUNT_SID`: Your Twilio account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio auth token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number
   - `OPENAI_API_KEY`: Your OpenAI API key (if using AI features)
7. Click "Deploy"

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check that your `DATABASE_URL` is correctly formatted
   - Ensure your database provider allows connections from Vercel IP addresses

2. **Missing Environment Variables**:
   - Make sure all required environment variables are set in the Vercel dashboard
   - Variables set locally will not be available in the deployment

3. **500 Internal Server Errors**:
   - Check the Vercel logs for detailed error messages
   - Common causes are database connection issues or missing environment variables

For more information, refer to the [Vercel Documentation](https://vercel.com/docs).
