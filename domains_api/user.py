import smtplib
from dataclasses import dataclass, field
from datetime import datetime
from email.message import EmailMessage
from getpass import getpass
from itertools import cycle
from typing import List, Optional

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
        if not email or not password:
            self.email_notifications = "n"
            return
        self.gmail_address = email
        self.gmail_app_password = password
        return True

    def email_wizard(self):
        """Set email attributes with encrypted password from command line input"""
        return self.set_email(
            input("Gmail address: "),
            encrypter.encrypt(getpass("Gmail (app) password: ").encode()),
        )

    def toggle_notifications(self, option: Optional[str] = None) -> str:
        """Toggle notifications or set to given value"""
        n_options = {"y": "[all changes]", "e": "[errors only]", "n": "[none]"}
        arg_hash = {"all": "y", "errors": "e", "off": "n"}
        options_iter = cycle(opt.lower() for opt in n_options.keys())
        if option is not None and (opt := arg_hash.get(option)):
            self.email_notifications = opt
        else:
            limit = len(n_options)
            for key in options_iter:
                if self.email_notifications.lower() == key or limit == 0:
                    break
                limit -= 1
            self.email_notifications = next(options_iter)
        return n_options[self.email_notifications]

    def send_emails(self, message: EmailMessage = None, outbox=None, log_fn=None):
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.ehlo()
        server.login(
            self.gmail_address, encrypter.decrypt(self.gmail_app_password).decode()
        )

        if outbox is not None:
            box = self.outbox
            for m in box:
                print(type(m))
                log_fn(f"Sending message: {m['Subject']}, {len(self.outbox)=}", "debug")
                server.send_message(m)
                self.outbox.remove(m)
        if message is not None:
            log_fn("Sending main message: {message['Subject']}", "debug")
            server.send_message(message)
        server.close()
        return True

    def send_notification(
        self, ip=None, msg_type="success", error=None, clear: bool = False, log_fn=None
    ):
        """Notify user via email if IP change is made successfully or if API call fails."""
        if self.email_notifications == "n":
            return

        msg = None

        if not clear:
            msg = self.create_message()

            if ip and msg_type == "success" and self.email_notifications != "e":
                msg.set_content(
                    f"IP for {self.domain} has changed! New IP: {ip}\n{datetime.now().isoformat()}"
                )
                msg["Subject"] = "Your IP has changed!"

            elif msg_type == "error":
                msg.set_content(
                    f"Error with {self.domain}'s IPChanger: ({error})!\n{datetime.now().isoformat()}"
                )
                msg["Subject"] = "IP CHANGER ERROR!"

        try:
            self.send_emails(msg, self.outbox, log_fn)

        except Exception as e:
            if log_fn is not None:
                self.log_errors(e, log_fn)
            if msg is not None:
                self.outbox.append(msg)

    @staticmethod
    def log_errors(e, log_fn):
        log_msg = f"{e.__class__.__name__}: {e}"
        log_fn(log_msg, "error")

    def create_message(self):
        msg = EmailMessage()
        msg["From"] = self.gmail_address
        msg["To"] = self.gmail_address
        return msg

    def send_test_message(self, log_fn):
        msg = self.create_message()
        msg["Subject"] = "Test Message"
        content = encrypter.encrypt("Hello, world!".encode())
        msg.set_content(f"{content*9}")
        try:
            self.send_emails(msg, log_fn=log_fn)
        except Exception as e:
            self.log_errors(e, log_fn)

    @classmethod
    def update_user_instance(cls, old_user_instance):
        return User(**old_user_instance.__dict__)
