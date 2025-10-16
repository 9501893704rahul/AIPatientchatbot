from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from flask import current_app, session, url_for
from datetime import datetime, timedelta
import json
import os

class CalendarService:
    """Service for Google Calendar integration."""
    
    def __init__(self):
        self.service = None
        self.scopes = ['https://www.googleapis.com/auth/calendar']
    
    def _get_credentials(self):
        """Get Google Calendar API credentials."""
        try:
            # Check if we have stored credentials
            if 'google_credentials' in session:
                creds_data = session['google_credentials']
                creds = Credentials.from_authorized_user_info(creds_data, self.scopes)
                
                # Refresh if expired
                if creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                    session['google_credentials'] = creds.to_json()
                
                return creds
            
            return None
            
        except Exception as e:
            print(f"Error getting credentials: {e}")
            return None
    
    def _get_service(self):
        """Get Google Calendar service."""
        if not self.service:
            creds = self._get_credentials()
            if creds:
                self.service = build('calendar', 'v3', credentials=creds)
        return self.service
    
    def get_auth_url(self):
        """Get Google OAuth authorization URL."""
        try:
            client_config = {
                "web": {
                    "client_id": current_app.config.get('GOOGLE_CLIENT_ID'),
                    "client_secret": current_app.config.get('GOOGLE_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [current_app.config.get('GOOGLE_REDIRECT_URI')]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                redirect_uri=current_app.config.get('GOOGLE_REDIRECT_URI')
            )
            
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url
            
        except Exception as e:
            print(f"Error getting auth URL: {e}")
            return None
    
    def handle_oauth_callback(self, code):
        """Handle OAuth callback and store credentials."""
        try:
            client_config = {
                "web": {
                    "client_id": current_app.config.get('GOOGLE_CLIENT_ID'),
                    "client_secret": current_app.config.get('GOOGLE_CLIENT_SECRET'),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [current_app.config.get('GOOGLE_REDIRECT_URI')]
                }
            }
            
            flow = Flow.from_client_config(
                client_config,
                scopes=self.scopes,
                redirect_uri=current_app.config.get('GOOGLE_REDIRECT_URI')
            )
            
            flow.fetch_token(code=code)
            
            # Store credentials in session
            session['google_credentials'] = flow.credentials.to_json()
            
            return True
            
        except Exception as e:
            print(f"Error handling OAuth callback: {e}")
            return False
    
    def create_appointment(self, appointment, patient):
        """Create a Google Calendar event for an appointment."""
        try:
            service = self._get_service()
            if not service:
                return None
            
            # Create event
            event = {
                'summary': f'Appointment - {patient.first_name} {patient.last_name}',
                'description': f'Patient: {patient.first_name} {patient.last_name}\nEmail: {patient.email}\nPhone: {patient.phone}\nReason: {appointment.reason_for_visit or "General consultation"}',
                'start': {
                    'dateTime': appointment.appointment_date.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': (appointment.appointment_date + timedelta(hours=1)).isoformat(),
                    'timeZone': 'UTC',
                },
                'attendees': [
                    {'email': patient.email},
                ],
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 24 hours before
                        {'method': 'popup', 'minutes': 60},       # 1 hour before
                    ],
                },
            }
            
            # Insert event
            event = service.events().insert(calendarId='primary', body=event).execute()
            return event.get('id')
            
        except Exception as e:
            print(f"Error creating calendar event: {e}")
            return None
    
    def update_appointment(self, appointment, patient):
        """Update a Google Calendar event."""
        try:
            service = self._get_service()
            if not service or not appointment.google_event_id:
                return False
            
            # Get existing event
            event = service.events().get(calendarId='primary', eventId=appointment.google_event_id).execute()
            
            # Update event details
            event['summary'] = f'Appointment - {patient.first_name} {patient.last_name}'
            event['description'] = f'Patient: {patient.first_name} {patient.last_name}\nEmail: {patient.email}\nPhone: {patient.phone}\nReason: {appointment.reason_for_visit or "General consultation"}\nStatus: {appointment.status}'
            event['start']['dateTime'] = appointment.appointment_date.isoformat()
            event['end']['dateTime'] = (appointment.appointment_date + timedelta(hours=1)).isoformat()
            
            # Update event
            service.events().update(calendarId='primary', eventId=appointment.google_event_id, body=event).execute()
            return True
            
        except Exception as e:
            print(f"Error updating calendar event: {e}")
            return False
    
    def delete_appointment(self, event_id):
        """Delete a Google Calendar event."""
        try:
            service = self._get_service()
            if not service:
                return False
            
            service.events().delete(calendarId='primary', eventId=event_id).execute()
            return True
            
        except Exception as e:
            print(f"Error deleting calendar event: {e}")
            return False
    
    def get_available_slots(self, date, duration_hours=1):
        """Get available appointment slots for a given date."""
        try:
            service = self._get_service()
            if not service:
                # Return default slots if no calendar access
                return self._get_default_slots(date)
            
            # Define business hours (9 AM to 5 PM)
            start_time = datetime.combine(date, datetime.min.time().replace(hour=9))
            end_time = datetime.combine(date, datetime.min.time().replace(hour=17))
            
            # Get existing events for the day
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Generate available slots
            available_slots = []
            current_time = start_time
            
            while current_time < end_time:
                slot_end = current_time + timedelta(hours=duration_hours)
                
                # Check if this slot conflicts with any existing event
                is_available = True
                for event in events:
                    event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
                    event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))
                    
                    if (current_time < event_end and slot_end > event_start):
                        is_available = False
                        break
                
                if is_available:
                    available_slots.append(current_time.strftime('%H:%M'))
                
                current_time += timedelta(hours=duration_hours)
            
            return available_slots
            
        except Exception as e:
            print(f"Error getting available slots: {e}")
            return self._get_default_slots(date)
    
    def _get_default_slots(self, date):
        """Get default available slots when calendar is not accessible."""
        # Return standard business hour slots
        slots = []
        for hour in range(9, 17):  # 9 AM to 5 PM
            slots.append(f"{hour:02d}:00")
            if hour < 16:  # Don't add 30-minute slot for the last hour
                slots.append(f"{hour:02d}:30")
        
        return slots