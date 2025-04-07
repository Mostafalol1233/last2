from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app, abort
from flask_login import login_required, current_user
import os
import logging
from datetime import datetime
import random
import string

from app import db
from models import User, SMSMessage
from services import SMSService

# Create a blueprint for SMS routes
sms_bp = Blueprint('sms', __name__)

@sms_bp.route('/send_verification', methods=['POST'])
@login_required
def send_verification():
    """Send verification code to user's phone number"""
    if not current_user.phone:
        flash('يجب تحديث رقم هاتفك أولاً.', 'warning')
        return redirect(url_for('profile'))
    
    # Generate a 6-digit verification code
    code = ''.join(random.choices(string.digits, k=6))
    
    # Store the code in session or database as needed
    # This is just a placeholder - in a real app, you would:
    # 1. Generate a proper verification token
    # 2. Store it securely with an expiration time
    # 3. Associate it with the user
    
    # Send the verification code via SMS
    result = SMSService.send_verification_code(current_user, code)
    
    if result:
        flash('تم إرسال رمز التحقق إلى هاتفك.', 'success')
    else:
        flash('فشل إرسال رمز التحقق. الرجاء المحاولة مرة أخرى.', 'danger')
    
    return redirect(url_for('profile'))

@sms_bp.route('/send_notification', methods=['POST'])
@login_required
def send_notification():
    """Send a custom notification SMS to a user (admin only)"""
    if not current_user.is_admin():
        abort(403)
    
    user_id = request.form.get('user_id')
    message = request.form.get('message')
    
    if not user_id or not message:
        flash('يجب تحديد المستخدم ونص الرسالة.', 'warning')
        return redirect(url_for('admin.users_list'))
    
    user = User.query.get(user_id)
    if not user or not user.phone:
        flash('المستخدم غير موجود أو لا يملك رقم هاتف.', 'warning')
        return redirect(url_for('admin.users_list'))
    
    # Send the SMS notification
    success = SMSService.send_message(user.phone, message)
    
    # Record the SMS message in the database
    sms = SMSMessage(
        user_id=user.id,
        phone_number=user.phone,
        message=message,
        status='sent' if success else 'failed',
        message_type='admin_notification'
    )
    db.session.add(sms)
    db.session.commit()
    
    if success:
        flash(f'تم إرسال الرسالة النصية إلى {user.full_name} بنجاح.', 'success')
    else:
        flash('فشل إرسال الرسالة النصية. الرجاء التحقق من الإعدادات والمحاولة مرة أخرى.', 'danger')
    
    return redirect(url_for('admin.users_list'))

@sms_bp.route('/bulk_send', methods=['POST'])
@login_required
def bulk_send():
    """Send a bulk SMS to multiple users (admin only)"""
    if not current_user.is_admin():
        abort(403)
    
    user_ids = request.form.getlist('user_ids')
    message = request.form.get('message')
    
    if not user_ids or not message:
        flash('يجب تحديد مستخدم واحد على الأقل ونص الرسالة.', 'warning')
        return redirect(url_for('admin.users_list'))
    
    success_count = 0
    fail_count = 0
    
    for user_id in user_ids:
        user = User.query.get(user_id)
        if user and user.phone:
            # Send the SMS
            success = SMSService.send_message(user.phone, message)
            
            # Record the SMS in the database
            sms = SMSMessage(
                user_id=user.id,
                phone_number=user.phone,
                message=message,
                status='sent' if success else 'failed',
                message_type='bulk_notification'
            )
            db.session.add(sms)
            
            if success:
                success_count += 1
            else:
                fail_count += 1
    
    db.session.commit()
    
    if success_count > 0:
        flash(f'تم إرسال الرسالة بنجاح إلى {success_count} مستخدم.', 'success')
    
    if fail_count > 0:
        flash(f'فشل إرسال الرسالة إلى {fail_count} مستخدم.', 'warning')
    
    return redirect(url_for('admin.users_list'))

@sms_bp.route('/history')
@login_required
def history():
    """View SMS messaging history (admin only)"""
    if not current_user.is_admin():
        abort(403)
    
    messages = SMSMessage.query.order_by(SMSMessage.sent_at.desc()).all()
    return render_template('sms/history.html', messages=messages)

@sms_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Configure SMS settings (admin only)"""
    if not current_user.is_admin():
        abort(403)
    
    if request.method == 'POST':
        # Update Twilio settings
        account_sid = request.form.get('account_sid')
        auth_token = request.form.get('auth_token')
        phone_number = request.form.get('phone_number')
        
        # In a real app, you would update these in the database or env vars
        # For now, we'll just show a success message
        flash('تم تحديث إعدادات الرسائل النصية بنجاح.', 'success')
        return redirect(url_for('sms.settings'))
    
    # For a real app, you would get these from env vars or database
    twilio_settings = {
        'account_sid': os.environ.get('TWILIO_ACCOUNT_SID', ''),
        'phone_number': os.environ.get('TWILIO_PHONE_NUMBER', '')
    }
    
    return render_template('sms/settings.html', settings=twilio_settings)

@sms_bp.route('/test', methods=['POST'])
@login_required
def test_sms():
    """Send a test SMS (admin only)"""
    if not current_user.is_admin():
        abort(403)
    
    phone_number = request.form.get('phone_number')
    message = request.form.get('message', 'This is a test message from your application.')
    
    if not phone_number:
        flash('يجب إدخال رقم هاتف للاختبار.', 'warning')
        return redirect(url_for('sms.settings'))
    
    # Send the test SMS
    success = SMSService.send_message(phone_number, message)
    
    # Record the test message
    sms = SMSMessage(
        user_id=current_user.id,
        phone_number=phone_number,
        message=message,
        status='sent' if success else 'failed',
        message_type='test'
    )
    db.session.add(sms)
    db.session.commit()
    
    if success:
        flash('تم إرسال رسالة الاختبار بنجاح.', 'success')
    else:
        flash('فشل إرسال رسالة الاختبار. تأكد من إعدادات Twilio الخاصة بك.', 'danger')
    
    return redirect(url_for('sms.settings'))

@sms_bp.route('/send_lecture_code', methods=['POST'])
@login_required
def send_lecture_code():
    """Send a lecture code to a student"""
    if not current_user.is_admin():
        abort(403)
    
    student_id = request.form.get('student_id')
    code = request.form.get('code')
    video_id = request.form.get('video_id')
    
    if not student_id or not code or not video_id:
        flash('معلومات غير كاملة.', 'warning')
        return redirect(url_for('admin.lecture_codes'))
    
    student = User.query.get(student_id)
    if not student or not student.phone:
        flash('الطالب غير موجود أو لا يملك رقم هاتف.', 'warning')
        return redirect(url_for('admin.lecture_codes'))
    
    # Get video information for the message
    from models import Video
    video = Video.query.get(video_id)
    if not video:
        flash('المحاضرة غير موجودة.', 'warning')
        return redirect(url_for('admin.lecture_codes'))
    
    # Prepare the message
    message = f"كود حضور المحاضرة: {code}\nعنوان المحاضرة: {video.title}\nيمكنك استخدام هذا الكود لحضور المحاضرة عبر منصتنا."
    
    # Send the SMS
    success = SMSService.send_message(student.phone, message)
    
    # Record the message
    sms = SMSMessage(
        user_id=student.id,
        phone_number=student.phone,
        message=message,
        status='sent' if success else 'failed',
        message_type='lecture_code'
    )
    db.session.add(sms)
    db.session.commit()
    
    if success:
        flash(f'تم إرسال كود المحاضرة إلى الطالب {student.full_name} بنجاح.', 'success')
    else:
        flash('فشل إرسال كود المحاضرة. الرجاء المحاولة مرة أخرى.', 'danger')
    
    return redirect(url_for('admin.lecture_codes'))