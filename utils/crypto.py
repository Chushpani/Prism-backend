from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

load_dotenv()

KEY = os.getenv("SECRET_CRYPTO_KEY")
KEY = os.getenv("SECRET_CRYPTO_KEY")
if not KEY:
    raise ValueError("❌ Критическая ошибка: SECRET_CRYPTO_KEY не найден в .env!")
cipher_suite = Fernet(KEY.encode())

def encrypt_imap(raw_password):
    return cipher_suite.encrypt(raw_password.encode()).decode()

def decrypt_imap(enc_password):
    return cipher_suite.decrypt(enc_password.encode()).decode()