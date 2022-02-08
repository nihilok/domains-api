import os
from pathlib import Path

from cryptography.fernet import Fernet

from domains_api.constants import HOME_PATH_DIR_NAME

file = Path(os.getenv("HOME")) / HOME_PATH_DIR_NAME / "fnet"

if not os.path.exists(file):
    os.makedirs(os.path.dirname(file), exist_ok=True)
    old_file = Path(os.path.abspath(os.path.dirname(__file__))) / "fnet"
    if os.path.exists(old_file):
        os.system(f"mv {old_file} {file}")
    if not os.path.exists(file):
        key = Fernet.generate_key()
        with open(file, "wb") as f:
            f.write(key)

with open(file, "rb") as f:
    key = f.read()

encrypter = Fernet(key)
