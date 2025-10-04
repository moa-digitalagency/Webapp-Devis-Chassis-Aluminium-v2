from cryptography.fernet import Fernet
import os
import base64
from hashlib import sha256

def get_encryption_key():
    key = os.environ.get('ENCRYPTION_KEY')
    if not key:
        key = base64.urlsafe_b64encode(sha256(os.environ.get('SECRET_KEY', 'default-secret-key').encode()).digest())
    else:
        key = key.encode()
    return key

def encrypt_data(data):
    if not data:
        return None
    
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data):
    if not encrypted_data:
        return None
    
    try:
        f = Fernet(get_encryption_key())
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()
    except:
        return encrypted_data
