from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # determino el algoritmo de hashing

def hash(password: str):
    print("Hashing password:", password)  
    return pwd_context.hash(password)

def verify(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_file_hash(file_bytes: bytes):
    """Genera un hash único (SHA256) del archivo para detectar duplicados."""
    return hashlib.sha256(file_bytes).hexdigest()