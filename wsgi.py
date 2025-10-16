#!/usr/bin/env python3
"""
WSGI entry point for Clinic AI Assistant
"""

import os
from app import create_app, db
from app.models import User, Patient, FAQ, AftercareInstruction

# Create Flask application
app = create_app()

def init_database():
    """Initialize database with sample data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if we need to create sample data
        if User.query.count() == 0:
            print("Creating sample data...")
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@clinic.com',
                role='admin'
            )
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            
            # Create sample FAQs
            sample_faqs = [
                {
                    'category': 'general',
                    'question': 'What are your clinic hours?',
                    'answer': 'Our clinic is open Monday through Friday from 9:00 AM to 5:00 PM, and Saturday from 9:00 AM to 1:00 PM. We are closed on Sundays.',
                    'language': 'en'
                },
                {
                    'category': 'appointments',
                    'question': 'How do I schedule an appointment?',
                    'answer': 'You can schedule an appointment by using our AI assistant, calling us at (555) 123-4567, or using our patient portal online.',
                    'language': 'en'
                },
                {
                    'category': 'insurance',
                    'question': 'What insurance do you accept?',
                    'answer': 'We accept most major insurance plans including Blue Cross Blue Shield, Aetna, Cigna, UnitedHealthcare, and Medicare. Please contact us to verify your specific plan.',
                    'language': 'en'
                },
                {
                    'category': 'services',
                    'question': 'What services do you offer?',
                    'answer': 'We offer comprehensive primary care services including general consultations, physical exams, vaccinations, minor procedures, and preventive care.',
                    'language': 'en'
                },
                {
                    'category': 'general',
                    'question': '¿Cuáles son los horarios de la clínica?',
                    'answer': 'Nuestra clínica está abierta de lunes a viernes de 9:00 AM a 5:00 PM, y los sábados de 9:00 AM a 1:00 PM. Estamos cerrados los domingos.',
                    'language': 'es'
                }
            ]
            
            for faq_data in sample_faqs:
                faq = FAQ(**faq_data)
                db.session.add(faq)
            
            # Create sample aftercare instructions
            sample_aftercare = [
                {
                    'title': 'General Consultation Follow-up',
                    'treatment_type': 'consultation',
                    'instructions': 'Follow all prescribed medications as directed. Monitor your symptoms and contact us if they worsen.',
                    'precautions': 'Avoid strenuous activities if advised. Take medications with food if specified.',
                    'follow_up_timeline': '1-2 weeks',
                    'emergency_signs': 'Severe pain, difficulty breathing, high fever (over 101°F), or any concerning symptoms.',
                    'language': 'en'
                },
                {
                    'title': 'Vaccination Aftercare',
                    'treatment_type': 'vaccination',
                    'instructions': 'Keep the injection site clean and dry. Apply ice if there is swelling or pain.',
                    'precautions': 'Avoid rubbing the injection site. Stay hydrated and rest if feeling tired.',
                    'follow_up_timeline': '24-48 hours for any reactions',
                    'emergency_signs': 'Severe allergic reaction, difficulty breathing, widespread rash, or severe swelling.',
                    'language': 'en'
                }
            ]
            
            for aftercare_data in sample_aftercare:
                aftercare = AftercareInstruction(**aftercare_data)
                db.session.add(aftercare)
            
            # Create sample patient
            sample_patient = Patient(
                first_name='John',
                last_name='Doe',
                email='john.doe@example.com',
                phone='(555) 123-4567',
                preferred_language='en'
            )
            db.session.add(sample_patient)
            
            db.session.commit()
            print("Sample data created successfully!")

# Initialize database on startup
init_database()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))