# backend/app/__init__.py (Updated)
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.models import db
from app.auth import auth_bp, init_oauth
from app.routes.staff import staff_bp  # <--- IMPORT THIS
from app.nfc_bridge import nfc_bp
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Allow Credentials for CORS
    CORS(app, supports_credentials=True, origins=["http://localhost:5173"])
    
    db.init_app(app)
    init_oauth(app)
    
    with app.app_context():
        db.create_all()

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(staff_bp, url_prefix='/staff') 
    app.register_blueprint(nfc_bp, url_prefix='/api/nfc')
    return app