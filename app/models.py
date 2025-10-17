from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    """User model for staff and admin authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='staff')  # staff, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Patient(db.Model):
    """Patient model for storing patient information."""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    emergency_contact = db.Column(db.String(100))
    emergency_phone = db.Column(db.String(20))
    insurance_provider = db.Column(db.String(100))
    insurance_number = db.Column(db.String(50))
    medical_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    preferred_language = db.Column(db.String(10), default='en')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy=True)
    intake_forms = db.relationship('IntakeForm', backref='patient', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'address': self.address,
            'emergency_contact': self.emergency_contact,
            'emergency_phone': self.emergency_phone,
            'insurance_provider': self.insurance_provider,
            'insurance_number': self.insurance_number,
            'preferred_language': self.preferred_language,
            'created_at': self.created_at.isoformat()
        }

class Appointment(db.Model):
    """Appointment model for managing patient appointments."""
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    appointment_date = db.Column(db.DateTime, nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)  # consultation, follow-up, etc.
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, completed, cancelled
    reason_for_visit = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    notes = db.Column(db.Text)
    google_event_id = db.Column(db.String(100))  # Google Calendar event ID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'appointment_date': self.appointment_date.isoformat(),
            'appointment_type': self.appointment_type,
            'status': self.status,
            'reason_for_visit': self.reason_for_visit,
            'symptoms': self.symptoms,
            'notes': self.notes,
            'created_at': self.created_at.isoformat()
        }

class IntakeForm(db.Model):
    """Intake form model for pre-appointment patient information."""
    __tablename__ = 'intake_forms'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    chief_complaint = db.Column(db.Text, nullable=False)
    symptoms = db.Column(db.Text)
    symptom_duration = db.Column(db.String(50))
    pain_level = db.Column(db.Integer)  # 1-10 scale
    previous_treatments = db.Column(db.Text)
    additional_notes = db.Column(db.Text)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'appointment_id': self.appointment_id,
            'chief_complaint': self.chief_complaint,
            'symptoms': self.symptoms,
            'symptom_duration': self.symptom_duration,
            'pain_level': self.pain_level,
            'previous_treatments': self.previous_treatments,
            'additional_notes': self.additional_notes,
            'completed_at': self.completed_at.isoformat()
        }

class FAQ(db.Model):
    """FAQ model for storing frequently asked questions."""
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)  # general, insurance, appointments, etc.
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), default='en')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'question': self.question,
            'answer': self.answer,
            'language': self.language,
            'is_active': self.is_active
        }

class AftercareInstruction(db.Model):
    """Aftercare instructions model for post-treatment guidance."""
    __tablename__ = 'aftercare_instructions'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    treatment_type = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    precautions = db.Column(db.Text)
    follow_up_timeline = db.Column(db.String(100))
    emergency_signs = db.Column(db.Text)
    language = db.Column(db.String(10), default='en')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'treatment_type': self.treatment_type,
            'instructions': self.instructions,
            'precautions': self.precautions,
            'follow_up_timeline': self.follow_up_timeline,
            'emergency_signs': self.emergency_signs,
            'language': self.language
        }

class ChatSession(db.Model):
    """Chat session model for tracking patient conversations."""
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'))
    language = db.Column(db.String(10), default='en')
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'patient_id': self.patient_id,
            'language': self.language,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ChatMessage(db.Model):
    """Chat message model for storing conversation history."""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False)
    sender = db.Column(db.String(20), nullable=False)  # user, assistant
    message = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50))  # text, form_data, appointment_request, etc.
    message_metadata = db.Column(db.Text)  # JSON string for additional data
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender': self.sender,
            'message': self.message,
            'message_type': self.message_type,
            'metadata': self.message_metadata,
            'timestamp': self.timestamp.isoformat()
        }

class ClinicSettings(db.Model):
    """Clinic settings model for storing clinic information and configuration."""
    __tablename__ = 'clinic_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    clinic_name = db.Column(db.String(200), nullable=False, default='Medical Clinic')
    clinic_logo_url = db.Column(db.String(500))
    address_line1 = db.Column(db.String(200))
    address_line2 = db.Column(db.String(200))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    zip_code = db.Column(db.String(20))
    country = db.Column(db.String(100), default='USA')
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    website = db.Column(db.String(200))
    
    # Operating Hours (JSON format)
    operating_hours = db.Column(db.Text)  # JSON: {"monday": {"open": "09:00", "close": "17:00", "closed": false}, ...}
    
    # Departments/Specialties (JSON format)
    departments = db.Column(db.Text)  # JSON: [{"name": "Dental", "description": "..."}, ...]
    
    # Notification settings
    email_notifications = db.Column(db.Boolean, default=True)
    sms_notifications = db.Column(db.Boolean, default=False)
    
    # Timezone
    timezone = db.Column(db.String(50), default='UTC')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'clinic_name': self.clinic_name,
            'clinic_logo_url': self.clinic_logo_url,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'operating_hours': self.operating_hours,
            'departments': self.departments,
            'email_notifications': self.email_notifications,
            'sms_notifications': self.sms_notifications,
            'timezone': self.timezone,
            'updated_at': self.updated_at.isoformat()
        }

class Doctor(db.Model):
    """Doctor model for storing doctor information and availability."""
    __tablename__ = 'doctors'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(20))  # Dr., MD, etc.
    specialization = db.Column(db.String(100))
    department = db.Column(db.String(100))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    license_number = db.Column(db.String(50))
    
    # Availability (JSON format)
    availability = db.Column(db.Text)  # JSON: {"monday": [{"start": "09:00", "end": "12:00"}, ...], ...}
    
    # Consultation modes
    in_person_consultation = db.Column(db.Boolean, default=True)
    video_consultation = db.Column(db.Boolean, default=False)
    phone_consultation = db.Column(db.Boolean, default=False)
    
    # Profile information
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.String(500))
    years_of_experience = db.Column(db.Integer)
    languages_spoken = db.Column(db.String(200))  # Comma-separated
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'title': self.title,
            'specialization': self.specialization,
            'department': self.department,
            'email': self.email,
            'phone': self.phone,
            'availability': self.availability,
            'in_person_consultation': self.in_person_consultation,
            'video_consultation': self.video_consultation,
            'phone_consultation': self.phone_consultation,
            'bio': self.bio,
            'profile_image_url': self.profile_image_url,
            'years_of_experience': self.years_of_experience,
            'languages_spoken': self.languages_spoken,
            'is_active': self.is_active
        }

class BookingSettings(db.Model):
    """Booking settings model for appointment configuration."""
    __tablename__ = 'booking_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Time slot settings
    slot_duration = db.Column(db.Integer, default=30)  # minutes per appointment
    buffer_time = db.Column(db.Integer, default=5)  # minutes between appointments
    
    # Daily limits
    max_appointments_per_day = db.Column(db.Integer, default=20)
    max_appointments_per_doctor = db.Column(db.Integer, default=10)
    
    # Booking window
    advance_booking_days = db.Column(db.Integer, default=30)  # how far in advance can patients book
    min_booking_notice_hours = db.Column(db.Integer, default=2)  # minimum notice required
    
    # Approval settings
    auto_approve_appointments = db.Column(db.Boolean, default=False)
    require_staff_approval = db.Column(db.Boolean, default=True)
    
    # Cancellation settings
    allow_patient_cancellation = db.Column(db.Boolean, default=True)
    cancellation_notice_hours = db.Column(db.Integer, default=24)
    
    # Notification settings
    send_confirmation_email = db.Column(db.Boolean, default=True)
    send_reminder_email = db.Column(db.Boolean, default=True)
    reminder_hours_before = db.Column(db.Integer, default=24)
    
    # Working hours (JSON format)
    working_hours = db.Column(db.Text)  # JSON: {"monday": {"start": "09:00", "end": "17:00", "enabled": true}, ...}
    
    # Holiday/blocked dates (JSON format)
    blocked_dates = db.Column(db.Text)  # JSON: ["2024-12-25", "2024-01-01", ...]
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'slot_duration': self.slot_duration,
            'buffer_time': self.buffer_time,
            'max_appointments_per_day': self.max_appointments_per_day,
            'max_appointments_per_doctor': self.max_appointments_per_doctor,
            'advance_booking_days': self.advance_booking_days,
            'min_booking_notice_hours': self.min_booking_notice_hours,
            'auto_approve_appointments': self.auto_approve_appointments,
            'require_staff_approval': self.require_staff_approval,
            'allow_patient_cancellation': self.allow_patient_cancellation,
            'cancellation_notice_hours': self.cancellation_notice_hours,
            'send_confirmation_email': self.send_confirmation_email,
            'send_reminder_email': self.send_reminder_email,
            'reminder_hours_before': self.reminder_hours_before,
            'working_hours': self.working_hours,
            'blocked_dates': self.blocked_dates,
            'updated_at': self.updated_at.isoformat()
        }