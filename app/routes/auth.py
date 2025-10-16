from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.models import User
from app import db
from werkzeug.security import check_password_hash
import functools

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator to require login for protected routes."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role for protected routes."""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    """Staff/admin login endpoint."""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['username'] = user.username
            
            return jsonify({
                'message': 'Login successful',
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
            
    except Exception as e:
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout endpoint."""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/me')
@login_required
def get_current_user():
    """Get current user information."""
    user = User.query.get(session['user_id'])
    if user:
        return jsonify(user.to_dict())
    return jsonify({'error': 'User not found'}), 404

@auth_bp.route('/create-admin', methods=['POST'])
def create_admin():
    """Create initial admin user (only if no admin exists)."""
    try:
        # Check if any admin user already exists
        existing_admin = User.query.filter_by(role='admin').first()
        if existing_admin:
            return jsonify({'error': 'Admin user already exists'}), 400
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': 'Username, email, and password required'}), 400
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            role='admin'
        )
        admin_user.set_password(password)
        
        db.session.add(admin_user)
        db.session.commit()
        
        return jsonify({
            'message': 'Admin user created successfully',
            'user': admin_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create admin user'}), 500