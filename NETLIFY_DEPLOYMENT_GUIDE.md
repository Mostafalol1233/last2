# Netlify Deployment Guide

This guide provides detailed instructions for deploying the Educational Platform on Netlify.

## Prerequisites

Before deploying to Netlify, make sure you have the following:

1. A [Netlify account](https://app.netlify.com/signup)
2. The [Netlify CLI](https://docs.netlify.com/cli/get-started/) installed (optional)
3. Required API keys set up:
   - Stripe API keys for payment processing
   - Twilio API keys for SMS functionality
   - OpenAI API key (if using AI features)
4. A database service (PostgreSQL) ready to use

## Step 1: Prepare Your Project

1. Make sure your code is ready for deployment
2. Create a `netlify.toml` file in the root of your project with the following content:

```
[build]
  command = "pip install -r requirements.txt"
  publish = "."

[functions]
  directory = "netlify/functions"

[[redirects]]
  from = "/*"
  to = "/.netlify/functions/api"
  status = 200
```

3. Create a directory structure for Netlify Functions:

```
mkdir -p netlify/functions
```

4. Create a serverless function to serve your Flask app in `netlify/functions/api.js`:

```
const serverless = require("serverless-http");
const { spawn } = require("child_process");
const path = require("path");

// Start the Flask app as a subprocess
const flask = spawn("python", [path.join(__dirname, "../../main.py")]);

// Log Flask output
flask.stdout.on("data", (data) => {
  console.log(`Flask: ${data}`);
});

flask.stderr.on("data", (data) => {
  console.error(`Flask error: ${data}`);
});

// Export the serverless handler
const handler = serverless(flask);
module.exports = { handler };
```

## Step 2: Set up a Database

1. Create a PostgreSQL database with your preferred provider (e.g., Railway, Supabase, Neon)
2. Get the database connection URL in the format:
   `postgresql://username:password@host:port/database`

## Step 3: Deploy to Netlify

### Option 1: Deploy via Git Integration

1. Push your project to a Git repository (GitHub, GitLab, or Bitbucket)
2. Visit [Netlify Dashboard](https://app.netlify.com/)
3. Click "Add new site" and select "Import an existing project"
4. Select your repository
5. Configure the build settings:
   - Build command: `pip install -r requirements.txt`
   - Publish directory: `.`
6. Add Environment Variables in the site settings:
   - `DATABASE_URL`: Your PostgreSQL connection URL
   - `SESSION_SECRET`: A strong random string for session security
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret (optional)
   - `TWILIO_ACCOUNT_SID`: Your Twilio account SID
   - `TWILIO_AUTH_TOKEN`: Your Twilio auth token
   - `TWILIO_PHONE_NUMBER`: Your Twilio phone number
   - `OPENAI_API_KEY`: Your OpenAI API key (if using AI features)
7. Click "Deploy site"

### Option 2: Deploy using Netlify CLI

1. Install Netlify CLI:
   `npm install -g netlify-cli`

2. Log in to your Netlify account:
   `netlify login`

3. Initialize Netlify in your project:
   `netlify init`

4. Set environment variables:
   ```
   netlify env:set DATABASE_URL "postgresql://username:password@host:port/database"
   netlify env:set SESSION_SECRET "your_secret_key"
   netlify env:set STRIPE_SECRET_KEY "your_stripe_secret"
   netlify env:set STRIPE_PUBLISHABLE_KEY "your_stripe_publishable"
   netlify env:set TWILIO_ACCOUNT_SID "your_twilio_sid"
   netlify env:set TWILIO_AUTH_TOKEN "your_twilio_token"
   netlify env:set TWILIO_PHONE_NUMBER "your_twilio_phone"
   netlify env:set OPENAI_API_KEY "your_openai_key"
   ```

5. Deploy your site:
   `netlify deploy --prod`

## Step 4: Set up the Database Schema

After deployment, initialize your database using one of these methods:

1. **Using Netlify Environment & CLI**:
   ```
   netlify env:pull .env
   source .env
   python db_migrate.py create
   ```

2. **Create a Database Setup Endpoint**:
   Add a temporary endpoint to your Flask app that runs the database migrations:
   ```
   @app.route('/setup-database', methods=['GET'])
   def setup_database():
       try:
           # Import your models
           from models import db
           # Create all tables
           db.create_all()
           return 'Database setup complete!', 200
       except Exception as e:
           return f'Error: {str(e)}', 500
   ```
   
   Visit this URL once after deployment:
   `https://your-netlify-site.netlify.app/setup-database`
   
   Remember to remove this endpoint after use.

## Troubleshooting

### Common Issues

1. **Database Connection Errors**:
   - Check that your `DATABASE_URL` is correctly formatted
   - Ensure your database provider allows connections from Netlify IP addresses
   - If using a free database tier, check for connection limitations

2. **Function Timeout Issues**:
   - Netlify Functions have a default timeout of 10 seconds
   - For longer operations, consider background tasks or setting up a separate service

3. **Missing Environment Variables**:
   - Make sure all required environment variables are set in the Netlify dashboard
   - Verify that your application is reading environment variables correctly

4. **Deployment Failures**:
   - Check the build logs for specific errors
   - Ensure your Python dependencies are correctly specified in `requirements.txt`
   - Verify that your `netlify.toml` file is properly configured

For more information, refer to the [Netlify Documentation](https://docs.netlify.com/).
