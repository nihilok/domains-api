import os
from pathlib import Path

from cryptography.fernet import Fernet

from domains_api.constants import HOME_PATH_DIR_NAME

if os.name == 'nt':
    homedir = os.getenv("userprofile")
else:
    homedir = os.getenv("HOME")
file = Path(homedir) / HOME_PATH_DIR_NAME / "fnet"
if not os.path.exists(file):
    exists = False
    os.makedirs(os.path.dirname(file), exist_ok=True)
    if not os.path.exists(file):
        key = Fernet.generate_key()
        with open(file, "wb") as f:
            f.write(key)
    else:
        exists = True
else:
    exists = True

if exists:
    with open(file, "rb") as f:
        key = f.read()

encrypter = Fernet(key)


def decrypt_password(password: bytes):
    return encrypter.decrypt(password).decode()
