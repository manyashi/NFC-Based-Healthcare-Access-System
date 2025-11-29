from flask import Blueprint, session, url_for, redirect, jsonify, request
from authlib.integrations.flask_client import OAuth
from app.models import db, User, PatientProfile
from app.config import Config

auth_bp = Blueprint('auth', __name__)
oauth = OAuth()

def init_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=Config.GOOGLE_CLIENT_ID,
        client_secret=Config.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'}
    )

@auth_bp.route('/login')
def login():
    # Frontend sends ?role=patient or ?role=staff
    session['login_role'] = request.args.get('role', 'patient')
    redirect_uri = url_for('auth.callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/callback')
def callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    
    email = user_info['email']
    google_sub = user_info['sub']
    wanted_role = session.get('login_role', 'patient')

    # Check if user exists
    user = User.query.filter_by(google_sub=google_sub).first()
    
    if not user:
        # Create new user
        user = User(
            email=email, 
            name=user_info['name'], 
            google_sub=google_sub, 
            role=wanted_role
        )
        db.session.add(user)
        db.session.commit()
        
        # If patient, init profile
        if wanted_role == 'patient':
            profile = PatientProfile(user_id=user.id)
            profile.set_data(personal={"dob": "Unknown"}, medical={"history": []})
            db.session.add(profile)
            db.session.commit()

    # Create Session
    session['user_id'] = user.id
    session['role'] = user.role
    
    # Redirect to Frontend
    return redirect("http://localhost:5173/auth-success")

@auth_bp.route('/me')
def me():
    if 'user_id' not in session:
        return jsonify(None), 401
    
    user = User.query.get(session['user_id'])
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    })

@auth_bp.route('/logout')
def logout():
    session.clear()
    return jsonify({"message": "Logged out"}), 200