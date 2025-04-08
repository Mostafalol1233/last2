# Deploying to Vercel

This guide explains how to deploy your Flask application to Vercel.

## Prerequisites

- A [Vercel](https://vercel.com/) account
- Git installed on your computer
- [Stripe](https://stripe.com/) account for payment processing
- [Twilio](https://twilio.com/) account for SMS functionality
- A PostgreSQL database (from services like Supabase, Railway, Neon, or others)

## Steps for Deployment

### 1. Prepare Your Database

Create a PostgreSQL database using one of these services:
- [Supabase](https://supabase.com/)
- [Railway](https://railway.app/)
- [Neon](https://neon.tech/)
- [ElephantSQL](https://www.elephantsql.com/)

Copy your database connection string. It should look like:
```
postgresql://username:password@hostname:port/database
```

### 2. Configure Application Secrets

Run the `config_secrets.py` script to set up your environment variables and Vercel configuration:

```bash
python config_secrets.py --vercel --stripe-key=sk_test_your_key --twilio-sid=AC123456 --twilio-token=your_token --twilio-phone=+1234567890 --db-url=your_database_url
```

This will generate a `vercel.json` file configured with your secrets.

### 3. Push to GitHub

Create a repository on GitHub and push your code:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 4. Deploy to Vercel

1. Sign in to your Vercel account
2. Click "New Project"
3. Import your GitHub repository
4. Configure the project:
   - Framework Preset: Other
   - Root Directory: ./
   - Build Command: Leave empty
   - Output Directory: Leave empty
5. Click "Deploy"

### 5. Setup Database Tables

After deployment, you need to create the database tables. You have two options:

#### Option 1: Using the Vercel CLI

Install and use the Vercel CLI to run the migration script:

```bash
npm i -g vercel
vercel login
vercel env pull .env.production
python db_migrate.py create
```

#### Option 2: Create a One-Time Setup Script

Create a simple setup endpoint in your application and access it once after deployment:

```
https://your-vercel-app.vercel.app/setup-database
```

### 6. Configure Stripe Webhook

1. In your Stripe dashboard, go to Developers > Webhooks
2. Add a new endpoint: `https://your-vercel-app.vercel.app/payment/webhook`
3. Select the following events:
   - `checkout.session.completed`
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
4. Note the webhook signing secret and update your Vercel configuration:

```bash
python config_secrets.py --vercel --stripe-webhook=whsec_your_webhook_secret
```

### 7. Test Your Deployment

Verify all functionality is working correctly:
- User authentication
- Payment processing
- SMS messaging
- Database operations

## Troubleshooting

### Database Connection Issues

If you're having trouble connecting to your database:

1. Verify your `DATABASE_URL` environment variable is correct
2. Check that your database allows connections from Vercel's IP ranges
3. Ensure your database credentials are correct

### Webhook Issues

For Stripe webhook problems:

1. Check the webhook logs in your Stripe Dashboard
2. Verify the webhook secret is correctly set in your environment variables
3. Check the routes are correctly defined in your application

### SMS Sending Failures

For Twilio SMS issues:

1. Verify your Twilio credentials (SID, Auth Token)
2. Ensure your Twilio phone number is active and properly formatted
3. Check if you need to upgrade from a trial account

## Maintenance Tips

1. **Updating your application**: Simply push changes to your GitHub repository and Vercel will automatically redeploy
2. **Monitoring**: Use Vercel's built-in logs to monitor application performance
3. **Database Migrations**: If you make schema changes, run the migration script after deployment

## Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Flask on Vercel Guide](https://vercel.com/guides/using-flask-with-vercel)
- [Stripe API Documentation](https://stripe.com/docs/api)
- [Twilio API Documentation](https://www.twilio.com/docs/api)