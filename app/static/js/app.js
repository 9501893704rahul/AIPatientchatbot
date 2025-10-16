// Main JavaScript file for Clinic AI Assistant

// Global variables
let currentSessionId = null;
let currentLanguage = 'en';
let isTyping = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize chat if on main page
    if (document.getElementById('chat-messages')) {
        initializeChat();
    }
    
    // Initialize admin dashboard if on admin page
    if (document.getElementById('adminTabs')) {
        initializeAdmin();
    }
    
    // Initialize patient portal if on patient page
    if (document.getElementById('patientLoginForm')) {
        initializePatientPortal();
    }
});

// Chat functionality
function initializeChat() {
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    const languageSelect = document.getElementById('language-select');
    
    // Set session ID from template
    if (typeof sessionId !== 'undefined') {
        currentSessionId = sessionId;
    }
    
    // Event listeners
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    sendButton.addEventListener('click', sendMessage);
    
    if (languageSelect) {
        languageSelect.addEventListener('change', function() {
            currentLanguage = this.value;
        });
    }
    
    // Focus on input
    chatInput.focus();
}

function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();
    
    if (!message || isTyping) return;
    
    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    chatInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send message to API
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            session_id: currentSessionId,
            language: currentLanguage
        })
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        
        if (data.error) {
            addMessageToChat('assistant', 'I apologize, but I encountered an error. Please try again.');
        } else {
            addMessageToChat('assistant', data.message, data.type, data.metadata);
            
            // Update session ID if provided
            if (data.session_id) {
                currentSessionId = data.session_id;
            }
        }
    })
    .catch(error => {
        hideTypingIndicator();
        console.error('Error:', error);
        addMessageToChat('assistant', 'I apologize, but I encountered a connection error. Please try again.');
    });
}

function addMessageToChat(sender, message, type = 'text', metadata = {}) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    const timestamp = new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    
    messageDiv.className = `message ${sender}-message fade-in`;
    
    const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
    const senderName = sender === 'user' ? 'You' : 'AI Assistant';
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <i class="${icon} me-2"></i>
            <strong>${senderName}:</strong> ${formatMessage(message, type, metadata)}
        </div>
        <small class="text-muted">${timestamp}</small>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(message, type, metadata) {
    // Convert markdown-style formatting
    let formattedMessage = message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    // Handle special message types
    if (type === 'appointment_scheduling' && metadata.needs_followup) {
        formattedMessage += '<br><br><button class="btn btn-sm btn-primary mt-2" onclick="openAppointmentForm()">Schedule Now</button>';
    }
    
    return formattedMessage;
}

function showTypingIndicator() {
    if (isTyping) return;
    
    isTyping = true;
    const chatMessages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <i class="fas fa-robot me-2"></i>
        <strong>AI Assistant is typing</strong>
        <span></span>
        <span></span>
        <span></span>
    `;
    
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function quickMessage(message) {
    const chatInput = document.getElementById('chat-input');
    chatInput.value = message;
    sendMessage();
}

// Admin Dashboard functionality
function initializeAdmin() {
    loadPatients();
    loadAppointments();
    loadFaqs();
    checkApiStatus();
    updateLastUpdated();
}

function loadPatients() {
    fetch('/api/patients')
    .then(response => response.json())
    .then(patients => {
        const tbody = document.querySelector('#patientsTable tbody');
        tbody.innerHTML = '';
        
        patients.forEach(patient => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${patient.first_name} ${patient.last_name}</td>
                <td>${patient.email}</td>
                <td>${patient.phone}</td>
                <td>-</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editPatient(${patient.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deletePatient(${patient.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error loading patients:', error);
    });
}

function loadAppointments() {
    fetch('/api/appointments')
    .then(response => response.json())
    .then(appointments => {
        const tbody = document.querySelector('#appointmentsTable tbody');
        tbody.innerHTML = '';
        
        appointments.forEach(appointment => {
            const row = document.createElement('tr');
            const date = new Date(appointment.appointment_date).toLocaleString();
            const statusBadge = getStatusBadge(appointment.status);
            
            row.innerHTML = `
                <td>Patient #${appointment.patient_id}</td>
                <td>${date}</td>
                <td>${appointment.appointment_type}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editAppointment(${appointment.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteAppointment(${appointment.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error loading appointments:', error);
    });
}

function loadFaqs() {
    fetch('/api/faqs')
    .then(response => response.json())
    .then(faqs => {
        const tbody = document.querySelector('#faqsTable tbody');
        tbody.innerHTML = '';
        
        faqs.forEach(faq => {
            const row = document.createElement('tr');
            const statusBadge = faq.is_active ? 
                '<span class="badge bg-success">Active</span>' : 
                '<span class="badge bg-secondary">Inactive</span>';
            
            row.innerHTML = `
                <td>${faq.category}</td>
                <td>${faq.question.substring(0, 50)}...</td>
                <td>${faq.language.toUpperCase()}</td>
                <td>${statusBadge}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editFaq(${faq.id})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteFaq(${faq.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });
    })
    .catch(error => {
        console.error('Error loading FAQs:', error);
    });
}

function getStatusBadge(status) {
    const badges = {
        'scheduled': '<span class="badge bg-primary">Scheduled</span>',
        'confirmed': '<span class="badge bg-success">Confirmed</span>',
        'completed': '<span class="badge bg-info">Completed</span>',
        'cancelled': '<span class="badge bg-danger">Cancelled</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
}

function checkApiStatus() {
    // Check OpenAI API status
    const openaiStatus = document.getElementById('openai-status');
    const calendarStatus = document.getElementById('calendar-status');
    
    // This would typically make API calls to check status
    // For now, we'll simulate the check
    setTimeout(() => {
        openaiStatus.className = 'badge bg-success';
        openaiStatus.textContent = 'Connected';
        
        calendarStatus.className = 'badge bg-warning';
        calendarStatus.textContent = 'Not Configured';
    }, 1000);
}

function updateLastUpdated() {
    const lastUpdatedElement = document.getElementById('last-updated');
    if (lastUpdatedElement) {
        lastUpdatedElement.textContent = new Date().toLocaleString();
    }
}

function savePatient() {
    const form = document.getElementById('addPatientForm');
    const formData = new FormData(form);
    const patientData = Object.fromEntries(formData.entries());
    
    fetch('/api/patients', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(patientData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Patient saved successfully!');
            bootstrap.Modal.getInstance(document.getElementById('addPatientModal')).hide();
            form.reset();
            loadPatients();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving patient');
    });
}

function saveFaq() {
    const form = document.getElementById('addFaqForm');
    const formData = new FormData(form);
    const faqData = Object.fromEntries(formData.entries());
    
    fetch('/api/faqs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(faqData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('FAQ saved successfully!');
            bootstrap.Modal.getInstance(document.getElementById('addFaqModal')).hide();
            form.reset();
            loadFaqs();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving FAQ');
    });
}

// Patient Portal functionality
function initializePatientPortal() {
    const loginForm = document.getElementById('patientLoginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            patientLogin();
        });
    }
}

function patientLogin() {
    const email = document.getElementById('patientEmail').value;
    const phone = document.getElementById('patientPhone').value;
    
    // Simple patient lookup (in production, this would be more secure)
    fetch('/api/patients')
    .then(response => response.json())
    .then(patients => {
        const patient = patients.find(p => p.email === email && p.phone === phone);
        
        if (patient) {
            currentPatient = patient;
            sessionStorage.setItem('currentPatient', JSON.stringify(patient));
            showPatientDashboard();
        } else {
            alert('Patient not found. Please check your email and phone number.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error during login');
    });
}

function showPatientDashboard() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('patientDashboard').classList.remove('d-none');
    document.getElementById('patientInfoSection').style.display = 'block';
    document.getElementById('patientName').textContent = `${currentPatient.first_name} ${currentPatient.last_name}`;
    
    loadPatientData();
}

function loadPatientData() {
    // Load patient profile data
    const profileForm = document.getElementById('profileForm');
    if (profileForm && currentPatient) {
        Object.keys(currentPatient).forEach(key => {
            const input = profileForm.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = currentPatient[key] || '';
            }
        });
    }
}

function logout() {
    currentPatient = null;
    sessionStorage.removeItem('currentPatient');
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('patientDashboard').classList.add('d-none');
    document.getElementById('patientInfoSection').style.display = 'none';
    document.getElementById('patientLoginForm').reset();
}

function scheduleAppointment() {
    if (!currentPatient) {
        alert('Please log in first');
        return;
    }
    
    const modal = new bootstrap.Modal(document.getElementById('scheduleModal'));
    modal.show();
}

function scheduleNewAppointment() {
    scheduleAppointment();
}

function viewAppointments() {
    // Load patient appointments
    console.log('Loading appointments for patient:', currentPatient.id);
}

function updateProfile() {
    if (!currentPatient) {
        alert('Please log in first');
        return;
    }
    
    const form = document.getElementById('profileForm');
    const formData = new FormData(form);
    const profileData = Object.fromEntries(formData.entries());
    
    fetch(`/api/patients/${currentPatient.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Profile updated successfully!');
            currentPatient = data;
            sessionStorage.setItem('currentPatient', JSON.stringify(data));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error updating profile');
    });
}

function intakeForm() {
    // Switch to intake form tab
    const intakeTab = document.getElementById('intake-tab');
    if (intakeTab) {
        intakeTab.click();
    }
}

function submitIntakeForm() {
    if (!currentPatient) {
        alert('Please log in first');
        return;
    }
    
    const form = document.getElementById('intakeForm');
    const formData = new FormData(form);
    const intakeData = Object.fromEntries(formData.entries());
    intakeData.patient_email = currentPatient.email;
    
    fetch('/api/intake-form', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(intakeData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Error: ' + data.error);
        } else {
            alert('Intake form submitted successfully!');
            form.reset();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting intake form');
    });
}

// Utility functions
function showLoading() {
    document.getElementById('loading-indicator').classList.remove('d-none');
}

function hideLoading() {
    document.getElementById('loading-indicator').classList.add('d-none');
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

function formatDateTime(dateString) {
    return new Date(dateString).toLocaleString();
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Service worker registration (for future PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker registration would go here
    });
}