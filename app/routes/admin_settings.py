from flask import Blueprint, request, jsonify, render_template
from app.models import ClinicSettings, Doctor, BookingSettings, FAQ
from app import db
from app.routes.auth import admin_required
import json
from datetime import datetime

admin_settings_bp = Blueprint('admin_settings', __name__)

# Clinic Settings Routes
@admin_settings_bp.route('/clinic-settings', methods=['GET'])
@admin_required
def get_clinic_settings():
    """Get clinic settings."""
    settings = ClinicSettings.query.first()
    if not settings:
        # Create default settings if none exist
        settings = ClinicSettings(
            clinic_name='Medical Clinic',
            operating_hours=json.dumps({
                'monday': {'open': '09:00', 'close': '17:00', 'closed': False},
                'tuesday': {'open': '09:00', 'close': '17:00', 'closed': False},
                'wednesday': {'open': '09:00', 'close': '17:00', 'closed': False},
                'thursday': {'open': '09:00', 'close': '17:00', 'closed': False},
                'friday': {'open': '09:00', 'close': '17:00', 'closed': False},
                'saturday': {'open': '09:00', 'close': '13:00', 'closed': False},
                'sunday': {'open': '09:00', 'close': '13:00', 'closed': True}
            }),
            departments=json.dumps([
                {'name': 'General Medicine', 'description': 'Primary care and general health services'},
                {'name': 'Pediatrics', 'description': 'Healthcare for children and adolescents'},
                {'name': 'Dental', 'description': 'Oral health and dental care services'}
            ])
        )
        db.session.add(settings)
        db.session.commit()
    
    return jsonify(settings.to_dict())

@admin_settings_bp.route('/clinic-settings', methods=['POST'])
@admin_required
def update_clinic_settings():
    """Update clinic settings."""
    data = request.get_json()
    
    settings = ClinicSettings.query.first()
    if not settings:
        settings = ClinicSettings()
        db.session.add(settings)
    
    # Update basic information
    settings.clinic_name = data.get('clinic_name', settings.clinic_name)
    settings.clinic_logo_url = data.get('clinic_logo_url', settings.clinic_logo_url)
    settings.address_line1 = data.get('address_line1', settings.address_line1)
    settings.address_line2 = data.get('address_line2', settings.address_line2)
    settings.city = data.get('city', settings.city)
    settings.state = data.get('state', settings.state)
    settings.zip_code = data.get('zip_code', settings.zip_code)
    settings.country = data.get('country', settings.country)
    settings.phone = data.get('phone', settings.phone)
    settings.email = data.get('email', settings.email)
    settings.website = data.get('website', settings.website)
    
    # Update operating hours
    if 'operating_hours' in data:
        settings.operating_hours = json.dumps(data['operating_hours'])
    
    # Update departments
    if 'departments' in data:
        settings.departments = json.dumps(data['departments'])
    
    # Update notification settings
    settings.email_notifications = data.get('email_notifications', settings.email_notifications)
    settings.sms_notifications = data.get('sms_notifications', settings.sms_notifications)
    settings.timezone = data.get('timezone', settings.timezone)
    
    settings.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Clinic settings updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Doctor Management Routes
@admin_settings_bp.route('/doctors', methods=['GET'])
@admin_required
def get_doctors():
    """Get all doctors."""
    doctors = Doctor.query.filter_by(is_active=True).all()
    return jsonify([doctor.to_dict() for doctor in doctors])

@admin_settings_bp.route('/doctors', methods=['POST'])
@admin_required
def add_doctor():
    """Add a new doctor."""
    data = request.get_json()
    
    doctor = Doctor(
        first_name=data['first_name'],
        last_name=data['last_name'],
        title=data.get('title', ''),
        specialization=data.get('specialization', ''),
        department=data.get('department', ''),
        email=data.get('email', ''),
        phone=data.get('phone', ''),
        license_number=data.get('license_number', ''),
        availability=json.dumps(data.get('availability', {})),
        in_person_consultation=data.get('in_person_consultation', True),
        video_consultation=data.get('video_consultation', False),
        phone_consultation=data.get('phone_consultation', False),
        bio=data.get('bio', ''),
        profile_image_url=data.get('profile_image_url', ''),
        years_of_experience=data.get('years_of_experience', 0),
        languages_spoken=data.get('languages_spoken', '')
    )
    
    try:
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor added successfully', 'doctor': doctor.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_settings_bp.route('/doctors/<int:doctor_id>', methods=['PUT'])
@admin_required
def update_doctor(doctor_id):
    """Update a doctor."""
    data = request.get_json()
    doctor = Doctor.query.get_or_404(doctor_id)
    
    doctor.first_name = data.get('first_name', doctor.first_name)
    doctor.last_name = data.get('last_name', doctor.last_name)
    doctor.title = data.get('title', doctor.title)
    doctor.specialization = data.get('specialization', doctor.specialization)
    doctor.department = data.get('department', doctor.department)
    doctor.email = data.get('email', doctor.email)
    doctor.phone = data.get('phone', doctor.phone)
    doctor.license_number = data.get('license_number', doctor.license_number)
    
    if 'availability' in data:
        doctor.availability = json.dumps(data['availability'])
    
    doctor.in_person_consultation = data.get('in_person_consultation', doctor.in_person_consultation)
    doctor.video_consultation = data.get('video_consultation', doctor.video_consultation)
    doctor.phone_consultation = data.get('phone_consultation', doctor.phone_consultation)
    doctor.bio = data.get('bio', doctor.bio)
    doctor.profile_image_url = data.get('profile_image_url', doctor.profile_image_url)
    doctor.years_of_experience = data.get('years_of_experience', doctor.years_of_experience)
    doctor.languages_spoken = data.get('languages_spoken', doctor.languages_spoken)
    doctor.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_settings_bp.route('/doctors/<int:doctor_id>', methods=['DELETE'])
@admin_required
def delete_doctor(doctor_id):
    """Soft delete a doctor."""
    doctor = Doctor.query.get_or_404(doctor_id)
    doctor.is_active = False
    doctor.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Doctor deactivated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Booking Settings Routes
@admin_settings_bp.route('/booking-settings', methods=['GET'])
@admin_required
def get_booking_settings():
    """Get booking settings."""
    settings = BookingSettings.query.first()
    if not settings:
        # Create default booking settings
        settings = BookingSettings(
            working_hours=json.dumps({
                'monday': {'start': '09:00', 'end': '17:00', 'enabled': True},
                'tuesday': {'start': '09:00', 'end': '17:00', 'enabled': True},
                'wednesday': {'start': '09:00', 'end': '17:00', 'enabled': True},
                'thursday': {'start': '09:00', 'end': '17:00', 'enabled': True},
                'friday': {'start': '09:00', 'end': '17:00', 'enabled': True},
                'saturday': {'start': '09:00', 'end': '13:00', 'enabled': True},
                'sunday': {'start': '09:00', 'end': '13:00', 'enabled': False}
            }),
            blocked_dates=json.dumps([])
        )
        db.session.add(settings)
        db.session.commit()
    
    return jsonify(settings.to_dict())

@admin_settings_bp.route('/booking-settings', methods=['POST'])
@admin_required
def update_booking_settings():
    """Update booking settings."""
    data = request.get_json()
    
    settings = BookingSettings.query.first()
    if not settings:
        settings = BookingSettings()
        db.session.add(settings)
    
    # Update time slot settings
    settings.slot_duration = data.get('slot_duration', settings.slot_duration)
    settings.buffer_time = data.get('buffer_time', settings.buffer_time)
    
    # Update daily limits
    settings.max_appointments_per_day = data.get('max_appointments_per_day', settings.max_appointments_per_day)
    settings.max_appointments_per_doctor = data.get('max_appointments_per_doctor', settings.max_appointments_per_doctor)
    
    # Update booking window
    settings.advance_booking_days = data.get('advance_booking_days', settings.advance_booking_days)
    settings.min_booking_notice_hours = data.get('min_booking_notice_hours', settings.min_booking_notice_hours)
    
    # Update approval settings
    settings.auto_approve_appointments = data.get('auto_approve_appointments', settings.auto_approve_appointments)
    settings.require_staff_approval = data.get('require_staff_approval', settings.require_staff_approval)
    
    # Update cancellation settings
    settings.allow_patient_cancellation = data.get('allow_patient_cancellation', settings.allow_patient_cancellation)
    settings.cancellation_notice_hours = data.get('cancellation_notice_hours', settings.cancellation_notice_hours)
    
    # Update notification settings
    settings.send_confirmation_email = data.get('send_confirmation_email', settings.send_confirmation_email)
    settings.send_reminder_email = data.get('send_reminder_email', settings.send_reminder_email)
    settings.reminder_hours_before = data.get('reminder_hours_before', settings.reminder_hours_before)
    
    # Update working hours
    if 'working_hours' in data:
        settings.working_hours = json.dumps(data['working_hours'])
    
    # Update blocked dates
    if 'blocked_dates' in data:
        settings.blocked_dates = json.dumps(data['blocked_dates'])
    
    settings.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Booking settings updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# FAQ Management Routes
@admin_settings_bp.route('/faqs', methods=['GET'])
@admin_required
def get_faqs():
    """Get all FAQs."""
    faqs = FAQ.query.filter_by(is_active=True).all()
    return jsonify([faq.to_dict() for faq in faqs])

@admin_settings_bp.route('/faqs', methods=['POST'])
@admin_required
def add_faq():
    """Add a new FAQ."""
    data = request.get_json()
    
    faq = FAQ(
        category=data['category'],
        question=data['question'],
        answer=data['answer'],
        language=data.get('language', 'en')
    )
    
    try:
        db.session.add(faq)
        db.session.commit()
        return jsonify({'success': True, 'message': 'FAQ added successfully', 'faq': faq.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_settings_bp.route('/faqs/<int:faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    """Update an FAQ."""
    data = request.get_json()
    faq = FAQ.query.get_or_404(faq_id)
    
    faq.category = data.get('category', faq.category)
    faq.question = data.get('question', faq.question)
    faq.answer = data.get('answer', faq.answer)
    faq.language = data.get('language', faq.language)
    faq.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'FAQ updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_settings_bp.route('/faqs/<int:faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    """Soft delete an FAQ."""
    faq = FAQ.query.get_or_404(faq_id)
    faq.is_active = False
    faq.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'FAQ deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Settings Dashboard Route
@admin_settings_bp.route('/settings-dashboard')
@admin_required
def settings_dashboard():
    """Render the admin settings dashboard."""
    return render_template('admin_settings.html')