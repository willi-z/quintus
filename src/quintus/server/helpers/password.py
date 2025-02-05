import hashlib
import uuid


def generate_salt(length=256):
    m = hashlib.sha256(uuid.uuid4().bytes)
    return m.hexdigest()[:length]


def hash_password(password: str, salt=None):
    if salt is None:
        salt = generate_salt()
    hash = password + salt
    for _ in range(4):
        m = hashlib.sha256(hash.encode())
        hash = m.hexdigest()
    return hash
