# import os
# from cryptography.fernet import Fernet
# import json

# # Ensure this is set in your .env file
# # Generate one via: Fernet.generate_key()
# KEY = os.environ.get('FERNET_KEY') 
# cipher_suite = Fernet(KEY)

# def encrypt_data(data_dict):
#     """Converts dict to JSON string, then encrypts to bytes."""
#     json_str = json.dumps(data_dict)
#     return cipher_suite.encrypt(json_str.encode('utf-8'))

# def decrypt_data(encrypted_blob):
#     """Decrypts bytes, decodes to string, returns dict."""
#     decrypted_data = cipher_suite.decrypt(encrypted_blob)
#     return json.loads(decrypted_data.decode('utf-8'))


import os
import json
from cryptography.fernet import Fernet
from app.config import Config

# Initialize Cipher
cipher = Fernet(Config.FERNET_KEY)

def encrypt_data(data_dict):
    """Takes a dictionary, converts to JSON, then encrypts."""
    if not data_dict: return None
    json_str = json.dumps(data_dict)
    return cipher.encrypt(json_str.encode('utf-8'))

def decrypt_data(encrypted_bytes):
    """Decrypts bytes, returns dictionary."""
    if not encrypted_bytes: return {}
    try:
        decrypted_text = cipher.decrypt(encrypted_bytes).decode('utf-8')
        return json.loads(decrypted_text)
    except Exception as e:
        print(f"Decryption error: {e}")
        return {}