from flask import Blueprint, render_template, request, jsonify, session
from app.models import Patient, Appointment, FAQ, AftercareInstruction
from app import db
from app.routes.auth import admin_required
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Clinic AI Assistant is running'
    })

@main_bp.route('/')
def index():
    """Main chatbot interface."""
    # Generate a unique session ID for the chat
    if 'chat_session_id' not in session:
        session['chat_session_id'] = str(uuid.uuid4())
    
    return render_template('index.html', session_id=session['chat_session_id'])

@main_bp.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard for managing the system."""
    # Get basic statistics
    stats = {
        'total_patients': Patient.query.count(),
        'total_appointments': Appointment.query.count(),
        'pending_appointments': Appointment.query.filter_by(status='scheduled').count(),
        'total_faqs': FAQ.query.filter_by(is_active=True).count()
    }
    
    return render_template('admin.html', stats=stats)

@main_bp.route('/patient-portal')
def patient_portal():
    """Patient portal for managing appointments and information."""
    return render_template('patient_portal.html')