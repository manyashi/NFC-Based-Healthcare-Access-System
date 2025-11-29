from flask import Blueprint, request, jsonify
from app.models import db, NFCToken, PatientProfile, User
from datetime import datetime
import os

nfc_bp = Blueprint('nfc', __name__)

@nfc_bp.route('/scan', methods=['POST']) # This matches POST /api/nfc/scan
def handle_nfc_scan():
    # 1. Verify Device Security
    device_key = request.headers.get('X-Device-API-Key')
    if device_key != os.environ.get('IOT_DEVICE_SECRET'):
        print(f"Unauthorized Device Attempt: {device_key}")
        return jsonify({'error': 'Unauthorized Device'}), 401

    data = request.json
    raw_uid = data.get('uid')
    
    if not raw_uid:
        return jsonify({'error': 'No UID provided'}), 400

    print(f"Device Scanned UID: {raw_uid}")

    # 2. Find the Token in DB
    # (In a real app, hash the raw_uid before comparing!)
    token = NFCToken.query.filter_by(nfc_uid_hash=raw_uid).first()
    
    if token:
        # 3. Update Patient Access Logic
        patient_profile = PatientProfile.query.filter_by(user_id=token.user_id).first()
        if patient_profile:
            patient_profile.last_scanned_at = datetime.utcnow()
            db.session.commit()
            print(f"Access granted for patient: {patient_profile.user.name}")
            return jsonify({'status': 'access_granted', 'patient': patient_profile.user.name}), 200
    
    print("Unknown Tag")
    return jsonify({'status': 'unknown_tag'}), 404