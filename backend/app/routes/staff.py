from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from app.models import db, User, PatientProfile, MedicalEntry
from app.utils import login_required, role_required 

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/active-patients', methods=['GET'])
@login_required
@role_required(['staff'])
def get_active_patients():
    cutoff = datetime.utcnow() - timedelta(hours=24)
    active_profiles = db.session.query(User, PatientProfile).\
        join(PatientProfile, User.id == PatientProfile.user_id).\
        filter(PatientProfile.last_scanned_at > cutoff).all()

    result = []
    for user, profile in active_profiles:
        expires_at = profile.last_scanned_at + timedelta(hours=24)
        minutes_left = int((expires_at - datetime.utcnow()).total_seconds() / 60)
        
        result.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "minutes_remaining": minutes_left
        })
    return jsonify(result)

@staff_bp.route('/patients/<int:patient_id>/details', methods=['GET'])
@login_required
@role_required(['staff'])
def get_patient_details(patient_id):
    profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    
    if not profile or not profile.has_active_access():
        return jsonify({"error": "Access Expired. Please scan patient NFC."}), 403

    # Join MedicalEntry with User to get Staff Name
    entries_query = db.session.query(MedicalEntry, User.name).\
        join(User, MedicalEntry.staff_id == User.id).\
        filter(MedicalEntry.patient_id == patient_id).\
        order_by(MedicalEntry.created_at.desc()).all()

    history = []
    for entry, staff_name in entries_query:
        history.append({
            "id": entry.id,
            "type": entry.entry_type,
            "department": entry.department,
            "staff_name": staff_name,
            "hospital_name": entry.hospital_name, # NEW: Send to frontend
            "timestamp": entry.created_at.isoformat(),
            "details": entry.get_details()
        })

    return jsonify({
        "patient": profile.user.name,
        "history": history
    })

@staff_bp.route('/patients/<int:patient_id>/add-entry', methods=['POST'])
@login_required
@role_required(['staff'])
def add_medical_entry(patient_id):
    profile = PatientProfile.query.filter_by(user_id=patient_id).first()
    
    if not profile or not profile.has_active_access():
        return jsonify({"error": "Access Expired"}), 403

    # Get the Staff User object to find their Hospital Name
    current_staff = User.query.get(session['user_id'])
    
    data = request.json
    
    new_entry = MedicalEntry(
        patient_id=patient_id,
        staff_id=current_staff.id,
        hospital_name=current_staff.hospital_name, # NEW: Auto-fill from Staff Profile
        entry_type=data.get('entry_type'),
        department=data.get('department'),
    )
    
    new_entry.set_details({
        "notes": data.get('notes'),
        "prescription": data.get('prescription'),
        "vitals": data.get('vitals')
    })

    db.session.add(new_entry)
    db.session.commit()
    
    return jsonify({"message": "Record added successfully"}), 201