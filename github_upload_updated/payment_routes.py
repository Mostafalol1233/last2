from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import login_required, current_user
import os
import stripe
from datetime import datetime, timedelta
import json

from app import db
from models import PaymentPlan, Transaction, Subscription, User
from services import PaymentService
from forms import PaymentForm, SubscriptionSelectForm

# Create a blueprint for payment routes
payment_bp = Blueprint('payment', __name__)

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
stripe_webhook_secret = os.environ.get('STRIPE_WEBHOOK_SECRET')

@payment_bp.route('/pricing')
def pricing():
    """Display available subscription plans"""
    plans = PaymentService.get_all_plans()
    return render_template('payment/pricing.html', plans=plans)

@payment_bp.route('/subscribe/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def subscribe(plan_id):
    """Handle subscription to a specific plan"""
    plan = PaymentService.get_plan_by_id(plan_id)
    if not plan:
        flash('خطة الاشتراك غير موجودة', 'danger')
        return redirect(url_for('payment.pricing'))
    
    if request.method == 'POST':
        try:
            # Create Stripe checkout session
            checkout_session = PaymentService.create_checkout_session(
                plan=plan,
                user=current_user,
                success_url=url_for('payment.checkout_success', _external=True),
                cancel_url=url_for('payment.checkout_cancel', _external=True)
            )
            
            # Redirect to Stripe checkout
            return redirect(checkout_session.url)
            
        except Exception as e:
            current_app.logger.error(f"Error creating checkout session: {e}")
            flash('حدث خطأ أثناء إنشاء جلسة الدفع. الرجاء المحاولة مرة أخرى.', 'danger')
            return redirect(url_for('payment.pricing'))
    
    return render_template('payment/subscribe.html', plan=plan)

@payment_bp.route('/checkout/success')
@login_required
def checkout_success():
    """Handle successful checkout"""
    flash('تم الدفع بنجاح! سيتم تفعيل اشتراكك قريبًا.', 'success')
    return redirect(url_for('student.dashboard'))

@payment_bp.route('/checkout/cancel')
@login_required
def checkout_cancel():
    """Handle canceled checkout"""
    flash('تم إلغاء عملية الدفع.', 'warning')
    return redirect(url_for('payment.pricing'))

@payment_bp.route('/webhook', methods=['POST'])
def webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    signature = request.headers.get('Stripe-Signature')
    
    if not stripe_webhook_secret:
        current_app.logger.warning("Stripe webhook secret is not configured")
        return jsonify({"error": "Webhook secret not configured"}), 500
    
    result = PaymentService.process_webhook_event(payload, signature)
    
    if "error" in result:
        return jsonify(result), 400
        
    return jsonify(result), 200

@payment_bp.route('/transactions')
@login_required
def transactions():
    """View user's payment transactions"""
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    return render_template('payment/transactions.html', transactions=transactions)

@payment_bp.route('/subscriptions')
@login_required
def subscriptions():
    """View user's active subscriptions"""
    active_subscriptions = Subscription.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).filter(
        Subscription.end_date > datetime.utcnow()
    ).all()
    
    return render_template('payment/subscriptions.html', subscriptions=active_subscriptions)

@payment_bp.route('/cancel_subscription/<int:subscription_id>', methods=['POST'])
@login_required
def cancel_subscription(subscription_id):
    """Cancel an active subscription"""
    subscription = Subscription.query.filter_by(
        id=subscription_id,
        user_id=current_user.id
    ).first_or_404()
    
    # Cancel auto-renewal
    subscription.auto_renew = False
    db.session.commit()
    
    # If there's a Stripe subscription, cancel it there too
    if subscription.stripe_subscription_id and stripe.api_key:
        try:
            stripe.Subscription.modify(
                subscription.stripe_subscription_id,
                cancel_at_period_end=True
            )
        except Exception as e:
            current_app.logger.error(f"Error canceling Stripe subscription: {e}")
    
    flash('تم إلغاء تجديد الاشتراك بنجاح.', 'success')
    return redirect(url_for('payment.subscriptions'))

# Admin routes for managing payments
@payment_bp.route('/admin/plans', methods=['GET'])
@login_required
def admin_plans():
    """Admin interface for managing payment plans"""
    if not current_user.is_admin():
        abort(403)
    
    plans = PaymentPlan.query.all()
    return render_template('payment/admin/plans.html', plans=plans)

@payment_bp.route('/admin/plan/create', methods=['GET', 'POST'])
@login_required
def admin_create_plan():
    """Admin interface for creating a new payment plan"""
    if not current_user.is_admin():
        abort(403)
    
    form = PaymentForm()
    if form.validate_on_submit():
        plan = PaymentPlan(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            currency=form.currency.data,
            duration_days=form.duration_days.data
        )
        
        # Set features from form data
        features = []
        if form.features.data:
            features = form.features.data.split('\n')
        plan.set_features([f for f in features if f.strip()])
        
        db.session.add(plan)
        db.session.commit()
        
        flash('تم إنشاء خطة الاشتراك بنجاح.', 'success')
        return redirect(url_for('payment.admin_plans'))
    
    return render_template('payment/admin/create_plan.html', form=form)

@payment_bp.route('/admin/plan/edit/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_plan(plan_id):
    """Admin interface for editing a payment plan"""
    if not current_user.is_admin():
        abort(403)
    
    plan = PaymentPlan.query.get_or_404(plan_id)
    form = PaymentForm(obj=plan)
    
    if request.method == 'GET':
        # Populate features field with existing features
        form.features.data = '\n'.join(plan.get_features())
    
    if form.validate_on_submit():
        plan.name = form.name.data
        plan.description = form.description.data
        plan.price = form.price.data
        plan.currency = form.currency.data
        plan.duration_days = form.duration_days.data
        
        # Set features from form data
        features = []
        if form.features.data:
            features = form.features.data.split('\n')
        plan.set_features([f for f in features if f.strip()])
        
        db.session.commit()
        
        flash('تم تحديث خطة الاشتراك بنجاح.', 'success')
        return redirect(url_for('payment.admin_plans'))
    
    return render_template('payment/admin/edit_plan.html', form=form, plan=plan)

@payment_bp.route('/admin/plan/toggle/<int:plan_id>', methods=['POST'])
@login_required
def admin_toggle_plan(plan_id):
    """Toggle plan active status"""
    if not current_user.is_admin():
        abort(403)
    
    plan = PaymentPlan.query.get_or_404(plan_id)
    plan.is_active = not plan.is_active
    db.session.commit()
    
    status = 'تفعيل' if plan.is_active else 'تعطيل'
    flash(f'تم {status} خطة الاشتراك بنجاح.', 'success')
    return redirect(url_for('payment.admin_plans'))

@payment_bp.route('/admin/transactions')
@login_required
def admin_transactions():
    """Admin interface for viewing all transactions"""
    if not current_user.is_admin():
        abort(403)
    
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    return render_template('payment/admin/transactions.html', transactions=transactions)

@payment_bp.route('/admin/subscriptions')
@login_required
def admin_subscriptions():
    """Admin interface for viewing all subscriptions"""
    if not current_user.is_admin():
        abort(403)
    
    subscriptions = Subscription.query.order_by(Subscription.created_at.desc()).all()
    return render_template('payment/admin/subscriptions.html', subscriptions=subscriptions)

# Models are imported from models.py at the top of this file