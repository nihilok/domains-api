#!/usr/bin/env python3
import os
import sys
from pathlib import Path

NOT_SUDO = bool(os.getgid())

if NOT_SUDO:
    print("must be executed as superuser")
    sys.exit(1)

WITH_INTERVAL = None
if len(sys.argv) > 1 and not sys.argv[1].isdigit():
    print("interval arg must be integer [e.g 30]")
    sys.exit(1)
elif len(sys.argv) > 1:
    WITH_INTERVAL = int(sys.argv[1])

script_path = Path("/usr/bin")

with open(script_path / "domainsd30", "w") as f:
    f.write(
        f"""#!/bin/bash
/bin/bash /home/{os.getenv("SUDO_USER")}/.local/domainsd 30
"""
    )
os.chmod(script_path / "domainsd30", 755)

service_file = Path("/etc/systemd/system/domainsd.service")

with open(service_file, "w") as f:
    f.write(
        f"""[Unit]
Description=Domains DDNS Daemon
After=network-online.target

[Service]
ExecStart=/usr/bin/domainsd{WITH_INTERVAL if WITH_INTERVAL else 30}

[Install]
WantedBy=multi-user.target 
"""
    )

os.system("systemctl daemon-reload")
os.system("systemctl enable domainsd")
os.system("systemctl start domainsd")
