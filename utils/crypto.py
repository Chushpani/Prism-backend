from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

# Достаем ключ из .env
KEY = os.getenv("SECRET_CRYPTO_KEY")
cipher_suite = Fernet(KEY.encode())

def encrypt_imap(raw_password):
    return cipher_suite.encrypt(raw_password.encode()).decode()

def decrypt_imap(enc_password):
    return cipher_suite.decrypt(enc_password.encode()).decode()