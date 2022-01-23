import smtplib
from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from getpass import getpass
from itertools import cycle
from typing import Optional, List

import outbox as outbox

from domains_api.encrypter import encrypter


@dataclass
class User:
    domain: str
    api_key: str
    api_sec: str
    email_notifications: str
    BASE_URL: str = "@domains.google.com/nic/update?hostname="
    outbox: List[EmailMessage] = field(default_factory=list)
    gmail_address: Optional[str] = None
    gmail_app_password: Optional[bytes] = None
    last_ip: Optional[str] = None

    @property
    def req_url(self):
        return f"https://{self.api_key}:{self.api_sec}{self.BASE_URL}{self.domain}"

    def set_domain(self, domain: str):
        self.domain = domain

    def set_api_credentials(self, api_key: str, api_sec: str):
        self.api_key = api_key
        self.api_sec = api_sec

    def set_notifications(self, n: str):
        self.email_notifications = n

    def set_email(self, email: str, password: bytes):
        if not email:
            self.email_notifications = 'n'
            return
        self.gmail_address = email
        self.gmail_app_password = password

    def email_wizard(self):
        """Set email attributes with encrypted password from command line input"""
        self.set_email(
            input("Gmail address: "),
            encrypter.encrypt(getpass("Gmail (app) password: ").encode()),
        )

    def toggle_notifications(self, option: Optional[str] = None) -> str:
        """Toggle notifications or set to given value"""
        n_options = {"Y": "[all changes]", "e": "[errors only]", "n": "[none]"}
        arg_hash = {"all": "Y", "errors": "e", "off": "n"}
        options_iter = cycle(n_options.keys())
        for option in options_iter:
            if self.email_notifications == option:
                break
        self.email_notifications = arg_hash.get(option) or next(options_iter)
        return n_options[self.email_notifications]

    def send_notification(
        self, ip=None, msg_type="success", error=None, clear: bool = False
    ):
        """Notify user via email if IP change is made successfully or if API call fails."""
        if self.email_notifications == "n":
            return

        msg = None

        if not clear:
            msg = EmailMessage()
            msg["From"] = self.gmail_address
            msg["To"] = self.gmail_address

            if ip and msg_type == "success" and self.email_notifications != "e":
                msg.set_content(f"IP for {self.domain} has changed! New IP: {ip}\n{datetime.now().isoformat()}")
                msg["Subject"] = "Your IP has changed!"

            elif msg_type == "error":
                msg.set_content(f"Error with {self.domain}'s IPChanger: ({error})!\n{datetime.now().isoformat()}")
                msg["Subject"] = "IPCHANGER ERROR!"

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.ehlo()
            server.login(
                self.gmail_address, encrypter.decrypt(self.gmail_app_password).decode()
            )

            box = self.outbox
            for m in box:
                server.send_message(m)
                self.outbox.remove(m)

            if msg is not None:
                server.send_message(msg)
            server.close()
            return True

        except Exception:
            if msg is not None:
                self.outbox.append(msg)

