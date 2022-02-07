import os
from pathlib import Path

from cryptography.fernet import Fernet

file = Path(os.getenv("HOME")) / '.domains-ddns' / "fnet"

if not os.path.exists(file):
    key = Fernet.generate_key()
    with open(file, "wb") as f:
        f.write(key)
else:
    with open(file, "rb") as f:
        key = f.read()

encrypter = Fernet(key)


def decrypt_password(password: bytes):
    return encrypter.decrypt(password).decode()
