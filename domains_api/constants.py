import os
from pathlib import Path

with open(Path(os.path.dirname(__file__)) / 'version.txt', 'r') as f:
    __VERSION__ = f.read().strip()

help_texts = {
    "nohost": "",
    "notfqdn": "",
    "badauth": "",
    "nochg": "",
    "good": ""
    }
