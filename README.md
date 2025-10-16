# Clinic AI Assistant

A comprehensive AI-powered clinic assistant system built with Flask and OpenAI, designed to automate patient interactions, appointment scheduling, and information management.

## Features

### Core Modules
1. **Patient Intake Module** - Collects patient information, symptoms, and insurance details
2. **Appointment Scheduling Module** - Integrates with Google Calendar for booking management
3. **FAQ Assistant** - Answers common questions about clinic services and policies
4. **Aftercare Guidance Module** - Provides post-treatment instructions and reminders
5. **Multilingual Support** - Enables communication in multiple languages

### Key Capabilities
- **AI-Powered Chatbot** - Intelligent conversation handling with OpenAI integration
- **Patient Portal** - Self-service portal for patients to manage appointments and information
- **Admin Dashboard** - Comprehensive management interface for staff
- **Google Calendar Integration** - Seamless appointment scheduling and management
- **Security & Compliance** - HIPAA-aligned security practices and data protection
- **Responsive Design** - Mobile-friendly interface for all devices

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python Flask framework
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **AI Engine**: OpenAI API for conversational intelligence
- **Calendar**: Google Calendar API for appointment management
- **Hosting**: Compatible with Render, Railway, Heroku, and other cloud platforms

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clinic-ai-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Access the application**
   - Main Interface: http://localhost:12000
   - Admin Dashboard: http://localhost:12000/admin
   - Patient Portal: http://localhost:12000/patient-portal

### Default Admin Credentials
- Username: `admin`
- Password: `admin123`

**⚠️ Change these credentials in production!**

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///clinic_assistant.db

# OpenAI API (Optional - system works without it)
OPENAI_API_KEY=your_openai_api_key_here

# Google Calendar API (Optional)
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:12000/oauth2callback

# Security
ALLOWED_ORIGINS=http://localhost:12000
```

### API Keys Setup

#### OpenAI API (Optional)
1. Visit [OpenAI API](https://platform.openai.com/api-keys)
2. Create an API key
3. Add to `.env` file as `OPENAI_API_KEY`

**Note**: The system includes fallback responses and works without OpenAI API.

#### Google Calendar API (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials
5. Add credentials to `.env` file

## Deployment

### Render Deployment

1. **Connect your repository** to Render
2. **Set environment variables** in Render dashboard
3. **Deploy** - Render will automatically install dependencies and start the app

### Railway Deployment

1. **Connect repository** to Railway
2. **Configure environment variables**
3. **Deploy** - Railway handles the rest automatically

### Manual Deployment

For other platforms:

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set environment variables**
3. **Run with Gunicorn**: `gunicorn run:app --bind 0.0.0.0:$PORT`

## Usage Guide

### For Patients

1. **Chat Interface**
   - Visit the main page
   - Start chatting with the AI assistant
   - Ask about appointments, services, or general questions

2. **Patient Portal**
   - Access via "Patient Portal" link
   - Log in with email and phone number
   - Manage appointments and update profile
   - Complete intake forms

### For Staff/Admin

1. **Admin Dashboard**
   - Access via "Admin" link
   - Log in with admin credentials
   - Manage patients, appointments, and FAQs
   - Monitor system status

2. **Patient Management**
   - Add new patients
   - Update patient information
   - View appointment history

3. **Content Management**
   - Add/edit FAQ entries
   - Manage aftercare instructions
   - Configure system settings

## API Endpoints

### Chat API
- `POST /api/chat` - Send message to AI assistant

### Patient Management
- `GET /api/patients` - List all patients
- `POST /api/patients` - Create new patient
- `GET /api/patients/{id}` - Get patient details
- `PUT /api/patients/{id}` - Update patient
- `DELETE /api/patients/{id}` - Delete patient

### Appointment Management
- `GET /api/appointments` - List appointments
- `POST /api/appointments` - Create appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Delete appointment

### FAQ Management
- `GET /api/faqs` - List FAQs
- `POST /api/faqs` - Create FAQ

### Other Endpoints
- `POST /api/intake-form` - Submit intake form
- `GET /api/available-slots` - Get available appointment slots
- `GET /api/aftercare` - Get aftercare instructions

## Security Features

- **Password Hashing** - Secure password storage using Werkzeug
- **Session Management** - Secure session handling
- **CORS Protection** - Configurable cross-origin resource sharing
- **Input Validation** - Server-side validation for all inputs
- **SQL Injection Prevention** - SQLAlchemy ORM protection
- **HTTPS Ready** - SSL/TLS support for production

## Customization

### Adding New Languages

1. **Update language utilities** in `app/utils/language_utils.py`
2. **Add translations** to the TRANSLATIONS dictionary
3. **Update frontend** language selector

### Adding New FAQ Categories

1. **Update admin interface** dropdown options
2. **Add category handling** in chatbot service
3. **Update frontend** category filters

### Extending AI Capabilities

1. **Modify chatbot service** in `app/services/chatbot_service.py`
2. **Add new intent detection** logic
3. **Implement new response handlers**

## Troubleshooting

### Common Issues

1. **Database not found**
   - Run `python run.py` to initialize database
   - Check DATABASE_URL in .env file

2. **OpenAI API errors**
   - Verify API key in .env file
   - Check API quota and billing
   - System works without OpenAI (fallback responses)

3. **Google Calendar not working**
   - Verify OAuth credentials
   - Check redirect URI configuration
   - System works without Calendar API

4. **Port already in use**
   - Change PORT in environment variables
   - Kill existing processes on the port

### Logs and Debugging

- **Enable debug mode**: Set `FLASK_ENV=development`
- **Check console logs** for JavaScript errors
- **Monitor server logs** for backend issues

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

## Roadmap

### Planned Features
- [ ] SMS notifications
- [ ] Email integration
- [ ] Advanced reporting
- [ ] Mobile app
- [ ] Telemedicine integration
- [ ] Insurance verification
- [ ] Payment processing
- [ ] Advanced analytics

### Version History
- **v1.0.0** - Initial release with core features
- **v1.1.0** - Enhanced security and multilingual support
- **v1.2.0** - Google Calendar integration
- **v2.0.0** - Advanced AI capabilities (planned)

---

**Built with ❤️ for healthcare providers worldwide**