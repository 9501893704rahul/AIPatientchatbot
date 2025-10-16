from flask import Blueprint, request, jsonify, session
from app.models import Patient, Appointment, FAQ, AftercareInstruction, ChatSession, ChatMessage, IntakeForm
from app.services.chatbot_service import ChatbotService
from app.services.calendar_service import CalendarService
from app.routes.auth import login_required, admin_required
from app import db
from datetime import datetime, timedelta
import json
import uuid

api_bp = Blueprint('api', __name__)

# Initialize services
chatbot_service = ChatbotService()
calendar_service = CalendarService()

@api_bp.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint for patient interactions."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id') or session.get('chat_session_id')
        language = data.get('language', 'en')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        if not session_id:
            session_id = str(uuid.uuid4())
            session['chat_session_id'] = session_id
        
        # Get or create chat session
        chat_session = ChatSession.query.filter_by(session_id=session_id).first()
        if not chat_session:
            chat_session = ChatSession(
                session_id=session_id,
                language=language
            )
            db.session.add(chat_session)
            db.session.commit()
        
        # Save user message
        user_message = ChatMessage(
            session_id=chat_session.id,
            sender='user',
            message=message,
            message_type='text'
        )
        db.session.add(user_message)
        
        # Get AI response
        response = chatbot_service.process_message(message, session_id, language)
        
        # Save assistant response
        assistant_message = ChatMessage(
            session_id=chat_session.id,
            sender='assistant',
            message=response['message'],
            message_type=response.get('type', 'text'),
            message_metadata=json.dumps(response.get('metadata', {}))
        )
        db.session.add(assistant_message)
        db.session.commit()
        
        return jsonify({
            'message': response['message'],
            'type': response.get('type', 'text'),
            'metadata': response.get('metadata', {}),
            'session_id': session_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to process message'}), 500

@api_bp.route('/patients', methods=['GET', 'POST'])
@login_required
def patients():
    """Manage patients."""
    if request.method == 'GET':
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            # Check if patient already exists
            existing_patient = Patient.query.filter_by(email=data.get('email')).first()
            if existing_patient:
                return jsonify({'error': 'Patient with this email already exists'}), 400
            
            patient = Patient(
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email'),
                phone=data.get('phone'),
                date_of_birth=datetime.strptime(data.get('date_of_birth'), '%Y-%m-%d').date() if data.get('date_of_birth') else None,
                gender=data.get('gender'),
                address=data.get('address'),
                emergency_contact=data.get('emergency_contact'),
                emergency_phone=data.get('emergency_phone'),
                insurance_provider=data.get('insurance_provider'),
                insurance_number=data.get('insurance_number'),
                medical_history=data.get('medical_history'),
                allergies=data.get('allergies'),
                current_medications=data.get('current_medications'),
                preferred_language=data.get('preferred_language', 'en')
            )
            
            db.session.add(patient)
            db.session.commit()
            
            return jsonify(patient.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create patient'}), 500

@api_bp.route('/patients/<int:patient_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def patient_detail(patient_id):
    """Get, update, or delete a specific patient."""
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        return jsonify(patient.to_dict())
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update patient fields
            for field in ['first_name', 'last_name', 'phone', 'gender', 'address', 
                         'emergency_contact', 'emergency_phone', 'insurance_provider',
                         'insurance_number', 'medical_history', 'allergies', 
                         'current_medications', 'preferred_language']:
                if field in data:
                    setattr(patient, field, data[field])
            
            if 'date_of_birth' in data and data['date_of_birth']:
                patient.date_of_birth = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
            
            patient.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify(patient.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update patient'}), 500
    
    elif request.method == 'DELETE':
        try:
            db.session.delete(patient)
            db.session.commit()
            return jsonify({'message': 'Patient deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete patient'}), 500

@api_bp.route('/appointments', methods=['GET', 'POST'])
@login_required
def appointments():
    """Manage appointments."""
    if request.method == 'GET':
        appointments = Appointment.query.all()
        return jsonify([appointment.to_dict() for appointment in appointments])
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            
            appointment = Appointment(
                patient_id=data.get('patient_id'),
                appointment_date=datetime.fromisoformat(data.get('appointment_date')),
                appointment_type=data.get('appointment_type'),
                reason_for_visit=data.get('reason_for_visit'),
                symptoms=data.get('symptoms'),
                notes=data.get('notes')
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            # Try to create Google Calendar event
            try:
                patient = Patient.query.get(appointment.patient_id)
                event_id = calendar_service.create_appointment(appointment, patient)
                if event_id:
                    appointment.google_event_id = event_id
                    db.session.commit()
            except Exception as e:
                # Log error but don't fail the appointment creation
                print(f"Failed to create calendar event: {e}")
            
            return jsonify(appointment.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create appointment'}), 500

@api_bp.route('/appointments/<int:appointment_id>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def appointment_detail(appointment_id):
    """Get, update, or delete a specific appointment."""
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == 'GET':
        return jsonify(appointment.to_dict())
    
    elif request.method == 'PUT':
        try:
            data = request.get_json()
            
            # Update appointment fields
            for field in ['appointment_type', 'status', 'reason_for_visit', 'symptoms', 'notes']:
                if field in data:
                    setattr(appointment, field, data[field])
            
            if 'appointment_date' in data:
                appointment.appointment_date = datetime.fromisoformat(data['appointment_date'])
            
            appointment.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Update Google Calendar event if exists
            if appointment.google_event_id:
                try:
                    patient = Patient.query.get(appointment.patient_id)
                    calendar_service.update_appointment(appointment, patient)
                except Exception as e:
                    print(f"Failed to update calendar event: {e}")
            
            return jsonify(appointment.to_dict())
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update appointment'}), 500
    
    elif request.method == 'DELETE':
        try:
            # Delete Google Calendar event if exists
            if appointment.google_event_id:
                try:
                    calendar_service.delete_appointment(appointment.google_event_id)
                except Exception as e:
                    print(f"Failed to delete calendar event: {e}")
            
            db.session.delete(appointment)
            db.session.commit()
            return jsonify({'message': 'Appointment deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete appointment'}), 500

@api_bp.route('/faqs', methods=['GET', 'POST'])
def faqs():
    """Manage FAQs."""
    if request.method == 'GET':
        category = request.args.get('category')
        language = request.args.get('language', 'en')
        
        query = FAQ.query.filter_by(is_active=True, language=language)
        if category:
            query = query.filter_by(category=category)
        
        faqs = query.all()
        return jsonify([faq.to_dict() for faq in faqs])
    
    elif request.method == 'POST':
        # Require authentication for creating FAQs
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            data = request.get_json()
            
            faq = FAQ(
                category=data.get('category'),
                question=data.get('question'),
                answer=data.get('answer'),
                language=data.get('language', 'en')
            )
            
            db.session.add(faq)
            db.session.commit()
            
            return jsonify(faq.to_dict()), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to create FAQ'}), 500

@api_bp.route('/aftercare', methods=['GET'])
def aftercare():
    """Get aftercare instructions."""
    treatment_type = request.args.get('treatment_type')
    language = request.args.get('language', 'en')
    
    query = AftercareInstruction.query.filter_by(is_active=True, language=language)
    if treatment_type:
        query = query.filter_by(treatment_type=treatment_type)
    
    instructions = query.all()
    return jsonify([instruction.to_dict() for instruction in instructions])

@api_bp.route('/intake-form', methods=['POST'])
def submit_intake_form():
    """Submit patient intake form."""
    try:
        data = request.get_json()
        
        # Find or create patient
        patient_email = data.get('patient_email')
        patient = Patient.query.filter_by(email=patient_email).first()
        
        if not patient:
            return jsonify({'error': 'Patient not found'}), 404
        
        intake_form = IntakeForm(
            patient_id=patient.id,
            appointment_id=data.get('appointment_id'),
            chief_complaint=data.get('chief_complaint'),
            symptoms=data.get('symptoms'),
            symptom_duration=data.get('symptom_duration'),
            pain_level=data.get('pain_level'),
            previous_treatments=data.get('previous_treatments'),
            additional_notes=data.get('additional_notes')
        )
        
        db.session.add(intake_form)
        db.session.commit()
        
        return jsonify(intake_form.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit intake form'}), 500

@api_bp.route('/available-slots', methods=['GET'])
def available_slots():
    """Get available appointment slots."""
    try:
        date_str = request.args.get('date')
        if not date_str:
            return jsonify({'error': 'Date parameter required'}), 400
        
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = calendar_service.get_available_slots(date)
        
        return jsonify({'slots': slots})
        
    except Exception as e:
        return jsonify({'error': 'Failed to get available slots'}), 500