# Vercel Deployment Guide

This document provides detailed instructions for deploying this Flask application to Vercel.

## Prerequisites

Before deploying to Vercel, make sure you have:

1. A [Vercel account](https://vercel.com/signup)
2. The [Vercel CLI](https://vercel.com/docs/cli) installed (optional but recommended)
3. A GitHub, GitLab, or Bitbucket account to host your code
4. A PostgreSQL database (you can use [Vercel PostgreSQL](https://vercel.com/docs/storage/vercel-postgres), [Neon](https://neon.tech/), [Supabase](https://supabase.com/), or any other PostgreSQL provider)

## Step 1: Prepare Your Repository

Your repository should already contain all the required files for deployment, including:

- `main.py` - The main application entry point
- `vercel.json` - Configuration for Vercel deployment
- `requirements.txt` - Python dependencies
- `vercel_setup.py` - Setup script for Vercel deployment

## Step 2: Create a PostgreSQL Database

You'll need a PostgreSQL database for your application:

1. If using Vercel PostgreSQL:
   - Go to the [Vercel Dashboard](https://vercel.com/dashboard)
   - Click on "Storage" in the sidebar
   - Select "Create Database" and follow the prompts

2. If using other providers like Neon or Supabase:
   - Sign up and create a PostgreSQL database
   - Get the database connection string

## Step 3: Deploy to Vercel

### Option 1: Using the Vercel Dashboard (Recommended for first deployment)

1. Push your code to a GitHub, GitLab, or Bitbucket repository
2. Go to the [Vercel Dashboard](https://vercel.com/dashboard)
3. Click "Add New" > "Project"
4. Select your repository
5. Configure your project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: Leave as default (it's set in vercel.json)
   - Output Directory: Leave as default
6. Click "Environment Variables" and add the following:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SESSION_SECRET`: A random string for session security
   - `STRIPE_SECRET_KEY`: Your Stripe Secret Key
   - `STRIPE_PUBLISHABLE_KEY`: Your Stripe Publishable Key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe Webhook Secret
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
   - `TWILIO_PHONE_NUMBER`: Your Twilio Phone Number
   - `OPENAI_API_KEY`: Your OpenAI API Key
7. Click "Deploy"

### Option 2: Using the Vercel CLI

1. Open a terminal in your project directory
2. Log in to Vercel if you haven't already:
   ```
   vercel login
   ```
3. Deploy the project:
   ```
   vercel
   ```
4. Follow the CLI prompts to configure your project
5. Set environment variables:
   ```
   vercel env add DATABASE_URL
   vercel env add SESSION_SECRET
   vercel env add STRIPE_SECRET_KEY
   # ... add other environment variables
   ```
6. Deploy again to apply environment variables:
   ```
   vercel --prod
   ```

## Step 4: Configure Stripe Webhooks

After deployment, you'll need to configure Stripe webhooks:

1. Go to the [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Click "Add Endpoint"
3. Enter your webhook URL (e.g., `https://your-app.vercel.app/payment/webhook`)
4. Select the events to listen for (at minimum: `checkout.session.completed`, `payment_intent.succeeded`, `payment_intent.payment_failed`)
5. Copy the webhook signing secret
6. Add the webhook secret to your Vercel environment variables:
   - Go to your project in the Vercel Dashboard
   - Go to Settings > Environment Variables
   - Add `STRIPE_WEBHOOK_SECRET` with the value you copied

## Step 5: Test Your Deployment

1. Visit your deployed application at `https://your-app.vercel.app`
2. Test all functionality to ensure it works correctly:
   - User registration/login
   - Payment processing
   - SMS functionality (if Twilio credentials are configured)
   - AI Chat (if OpenAI API key is configured)

## Troubleshooting

If you encounter issues with your deployment:

1. Check the Vercel deployment logs in the Vercel Dashboard
2. Verify that all environment variables are set correctly
3. Ensure your database connection string is correct and accessible from Vercel
4. Check if your Stripe and Twilio credentials are correct and have the necessary permissions

## Continuous Deployment

Vercel automatically sets up continuous deployment from your repository. 
Any new commits to your main branch will trigger a new deployment.

## Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel CLI Documentation](https://vercel.com/docs/cli)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Twilio API Documentation](https://www.twilio.com/docs/api)