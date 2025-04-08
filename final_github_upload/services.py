import os
import logging
import stripe
from datetime import datetime, timedelta
from twilio.rest import Client
from flask import current_app, url_for
from models import db, PaymentPlan, Transaction, Subscription, User, SMSMessage

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe_webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

# Initialize Twilio if credentials are available
twilio_client = None
twilio_phone_number = None

if all(k in os.environ for k in ('TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN', 'TWILIO_PHONE_NUMBER')):
    try:
        twilio_client = Client(
            os.environ.get('TWILIO_ACCOUNT_SID'),
            os.environ.get('TWILIO_AUTH_TOKEN')
        )
        twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
    except Exception as e:
        logger.error(f"Failed to initialize Twilio client: {e}")


class PaymentService:
    """Service for handling payment-related operations"""
    
    @staticmethod
    def get_all_plans():
        """Get all active payment plans"""
        return PaymentPlan.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_plan_by_id(plan_id):
        """Get a specific payment plan by ID"""
        return PaymentPlan.query.get(plan_id)
    
    @staticmethod
    def create_checkout_session(plan, user, success_url=None, cancel_url=None):
        """Create a Stripe checkout session for a plan"""
        if not stripe.api_key:
            raise ValueError("Stripe API key is not configured")
        
        if not success_url:
            success_url = url_for('payment.checkout_success', _external=True)
        
        if not cancel_url:
            cancel_url = url_for('payment.checkout_cancel', _external=True)
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': plan.currency.lower(),
                        'unit_amount': int(plan.price * 100),  # Convert to cents
                        'product_data': {
                            'name': plan.name,
                            'description': plan.description
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=str(user.id),
                metadata={
                    'plan_id': plan.id,
                    'user_id': user.id
                }
            )
            
            # Record the transaction
            transaction = Transaction(
                user_id=user.id,
                plan_id=plan.id,
                amount=plan.price,
                currency=plan.currency,
                status='pending',
                payment_processor='stripe',
                transaction_id=session.id
            )
            db.session.add(transaction)
            db.session.commit()
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            db.session.rollback()
            raise
    
    @staticmethod
    def process_webhook_event(payload, signature):
        """Process Stripe webhook events"""
        if not stripe_webhook_secret:
            raise ValueError("Stripe webhook secret is not configured")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, stripe_webhook_secret
            )
            
            if event.type == 'checkout.session.completed':
                session = event.data.object
                PaymentService._handle_checkout_completed(session)
                
            elif event.type == 'payment_intent.succeeded':
                payment_intent = event.data.object
                PaymentService._handle_payment_succeeded(payment_intent)
                
            elif event.type == 'payment_intent.payment_failed':
                payment_intent = event.data.object
                PaymentService._handle_payment_failed(payment_intent)
                
            return {"status": "success"}
            
        except ValueError as e:
            logger.error(f"Invalid payload: {e}")
            return {"error": "Invalid payload"}
            
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {e}")
            return {"error": "Invalid signature"}
            
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            return {"error": "Error processing webhook"}
    
    @staticmethod
    def _handle_checkout_completed(session):
        """Handle checkout.session.completed event"""
        user_id = session.get('client_reference_id')
        plan_id = session.get('metadata', {}).get('plan_id')
        
        # Update the transaction status
        transaction = Transaction.query.filter_by(
            transaction_id=session.id
        ).first()
        
        if transaction:
            transaction.status = 'completed'
            
            # Create a subscription record
            plan = PaymentPlan.query.get(plan_id)
            if plan:
                subscription = Subscription(
                    user_id=user_id,
                    plan_id=plan_id,
                    is_active=True,
                    start_date=datetime.utcnow(),
                    end_date=datetime.utcnow() + timedelta(days=plan.duration_days),
                    payment_transaction_id=transaction.id
                )
                db.session.add(subscription)
            
            db.session.commit()
            
            # Send confirmation SMS if Twilio is configured
            from models import User
            user = User.query.get(user_id)
            if user and user.phone and twilio_client:
                SMSService.send_message(
                    user.phone,
                    f"Your payment for {plan.name} has been completed successfully. Thank you!"
                )
    
    @staticmethod
    def _handle_payment_succeeded(payment_intent):
        """Handle payment_intent.succeeded event"""
        # This could be used for additional payment success handling
        pass
    
    @staticmethod
    def _handle_payment_failed(payment_intent):
        """Handle payment_intent.payment_failed event"""
        last_error = payment_intent.get('last_payment_error', {})
        error_message = last_error.get('message', 'Unknown error')
        
        # Find the transaction and update its status
        transaction = Transaction.query.filter_by(
            transaction_id=payment_intent.get('id')
        ).first()
        
        if transaction:
            transaction.status = 'failed'
            transaction.notes = error_message
            db.session.commit()


class SMSService:
    """Service for sending SMS messages"""
    
    @staticmethod
    def send_message(to_number, message):
        """Send an SMS message using Twilio"""
        if not twilio_client or not twilio_phone_number:
            logger.warning("Twilio is not properly configured. SMS not sent.")
            return False
        
        try:
            # Format the phone number if needed
            if not to_number.startswith('+'):
                to_number = f"+{to_number}"
                
            message = twilio_client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=to_number
            )
            
            logger.info(f"SMS sent successfully. SID: {message.sid}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    @staticmethod
    def send_verification_code(user, code):
        """Send a verification code to a user"""
        if not user.phone:
            logger.warning(f"User {user.id} does not have a phone number")
            return False
            
        message = f"Your verification code is: {code}"
        return SMSService.send_message(user.phone, message)
    
    @staticmethod
    def send_subscription_notification(user, subscription):
        """Send subscription notification to a user"""
        if not user.phone:
            return False
            
        plan = PaymentPlan.query.get(subscription.plan_id)
        if not plan:
            return False
            
        message = f"Your subscription to {plan.name} has been activated. Enjoy!"
        return SMSService.send_message(user.phone, message)