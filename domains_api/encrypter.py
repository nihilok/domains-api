import os

from cryptography.fernet import Fernet

file = os.path.join(os.path.dirname(__file__), "fnet")

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
