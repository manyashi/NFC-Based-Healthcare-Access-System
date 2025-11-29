from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(100))
    role = db.Column(db.String(20), nullable=False) # 'patient', 'staff'
    google_sub = db.Column(db.String(100), unique=True)
    
    # NEW: Affiliation for Staff
    # In a multi-tenant system, this links the doctor to their workplace
    hospital_name = db.Column(db.String(150), default="General City Hospital") 
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_profile = db.relationship('PatientProfile', backref='user', uselist=False)

class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    last_scanned_at = db.Column(db.DateTime, nullable=True)

    # Encrypted Fields
    _personal_data = db.Column("personal_data", db.LargeBinary)
    _medical_data = db.Column("medical_data", db.LargeBinary)

    def has_active_access(self):
        if not self.last_scanned_at:
            return False
        return datetime.utcnow() < self.last_scanned_at + timedelta(hours=24)

    def set_data(self, personal=None, medical=None):
        from app.encryption import encrypt_data
        if personal: self._personal_data = encrypt_data(personal)
        if medical: self._medical_data = encrypt_data(medical)

class NFCToken(db.Model):
    __tablename__ = 'nfc_tokens'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    nfc_uid_hash = db.Column(db.String(256), nullable=False)

class MedicalEntry(db.Model):
    __tablename__ = 'medical_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # ACCOUNTABILITY FIELDS
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False) # Snapshot of where it happened
    
    # Metadata
    entry_type = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Encrypted Content
    _encrypted_details = db.Column("details", db.LargeBinary, nullable=False)

    def set_details(self, data_dict):
        from app.encryption import encrypt_data
        self._encrypted_details = encrypt_data(data_dict)

    def get_details(self):
        from app.encryption import decrypt_data
        return decrypt_data(self._encrypted_details)