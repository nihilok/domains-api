import os
import sys
import base64
import smtplib
from email.message import EmailMessage
from getpass import getpass
from itertools import cycle

from requests import get
from requests.exceptions import RequestException

from . import __VERSION__
from .file_handlers import FileHandlers
from .arg_parser import parser


fh = FileHandlers()

# # Uncomment or replicate in your code to set log level:
# fh.set_log_level('debug')
# fh.initialize_loggers()


def get_ip_only():
    """Gets current external IP from ipify.org"""
    current_ip = get("https://api.ipify.org").text
    return current_ip


class BaseUser:
    def __init__(self):
        """Create user instance and save it for future changes to API and for email notifications."""
        print(f"\n[ - Domains DDNS API Version {__VERSION__} - ]\n")
        print("Setting up user...")
        print(
            "To automatically update DDNS on Google Domains you will need your autogenerated credentials"
        )
        self.domain = input(
            'What is the reference for this IP? (Anything you like, e.g "example.com" or "Work PC"): '
        )
        self.notifications, self.gmail_address, self.gmail_password = self.set_email()
        self.outbox = []
        self.previous_ip = ""

    def set_email(self):
        """Set/return attributes for Gmail credentials if user enables notifications"""
        self.notifications = input(
            "Enable email notifications? [Y]all(default); [e]errors only; [n]no: "
        ).lower()
        if self.notifications != "n":
            self.gmail_address = input("What's your email address?: ")
            self.gmail_password = base64.b64encode(
                getpass(
                    "What's your email(less secure)/app(more secure) password?: "
                ).encode("utf-8")
            )
            if self.notifications != "e":
                self.notifications = "Y"
            return self.notifications, self.gmail_address, self.gmail_password
        else:
            return "n", None, None

    def send_notification(
        self, ip=None, msg_type="success", error=None, outbox_msg=None
    ):
        """Notify user via email if IP change is made successfully or if API call fails."""
        if self.notifications == "n":
            return
        msg = EmailMessage()
        msg["From"] = self.gmail_address
        msg["To"] = self.gmail_address
        if ip and msg_type == "success" and self.notifications != "e":
            msg.set_content(f"IP for {self.domain} has changed! New IP: {ip}")
            msg["Subject"] = "Your IP has changed!"
        elif msg_type == "error":
            msg.set_content(f"Error with {self.domain}'s IPChanger: ({error})!")
            msg["Subject"] = "IPCHANGER ERROR!"
        elif outbox_msg:
            msg = outbox_msg

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            server.ehlo()
            server.login(
                self.gmail_address,
                base64.b64decode(self.gmail_password).decode("utf-8"),
            )
            server.send_message(msg)
            server.close()
            return True
        except Exception as e:
            log_msg = "Email notification not sent: %s" % e
            fh.log(log_msg, "warning")
            self.outbox.append(msg)
            fh.save_user(self)

    def set_domains_credentials(self):
        raise NotImplementedError


class IPChecker:

    def __init__(self, argv=None, user_type=BaseUser):
        """Check for command line arguments, load/create User instance,
        check previous IP address against current external IP, and change via the API if different."""
        self.changed = False
        self.current_ip = self.get_ip()

        if [
            arg
            for arg in sys.argv
            if arg in {"-h", "--help", "-i", "--ip", "-l", "--load_user"}
        ]:
            self.get_opts(argv)
            return

        if os.path.isfile(fh.user_file):
            self.user = fh.load_user(fh.user_file)
            fh.log("User loaded from pickle", "debug")
        else:
            self.user = user_type()
            fh.log(
                "New user created.\n(See `python -m domains_api --help` for help changing/removing the user)",
                "info",
            )
        if argv:
            self.get_opts(argv)
        else:
            self.check_ip()

    def get_opts(self, argv):
        """Parse command line options"""
        self.arg_parse(parser.parse_args(argv))

    def get_ip(self):
        """Gets current external IP from api.ipify.org and sets self.current_ip"""
        try:
            return get_ip_only()
        except (RequestException, ConnectionError) as e:
            fh.log("Connection Error. Could not reach api.ipify.org", "warning")
            self.user.send_notification(msg_type="error", error=e)

    def check_ip(self):
        try:
            if self.user.previous_ip == self.current_ip:
                log_msg = "Current IP: %s (no change)" % self.user.previous_ip
                fh.log(log_msg, "debug")
            else:
                self.user.previous_ip = self.current_ip
                self.changed = True
                fh.save_user(self.user)
                log_msg = "Newly recorded IP: %s" % self.user.previous_ip
                fh.log(log_msg, "info")
        except AttributeError:
            setattr(self.user, "previous_ip", self.current_ip)
            self.changed = True
            log_msg = "Newly recorded IP: %s" % self.user.previous_ip
            fh.log(log_msg, "info")
            fh.save_user(self.user)

            # Send outbox emails:
            if self.user.outbox:
                for i in range(len(self.user.outbox)):
                    if self.user.send_notification(outbox_msg=self.user.outbox.pop(i)):
                        fh.log("Outbox message sent", "info")
                fh.save_user(self.user)
            fh.clear_logs()

    def arg_parse(self, opts):
        """Parses command line options: e.g. "domains-api --ip" """
        if opts.ip:
            print(
                """
[Domains API] Current external IP: %s
            """
                % get_ip_only()
            )

        elif opts.delete_user:
            fh.delete_user()

        elif opts.email:
            self.user.set_email()
            fh.save_user(self.user)
            fh.log("Notification settings changed", "info")

        elif opts.load_user:
            if (
                input("Are you sure you want to load a new user? [Y/n] ").lower()
                == "n"
            ):
                return
            self.user = fh.load_user(opts.load_user)
            fh.save_user(self.user)
            fh.log("New user loaded", "info")

        elif opts.notify:
            n_options = {"Y": "[all changes]", "e": "[errors only]", "n": "[none]"}
            arg_hash = {
                "all": 'Y',
                "errors": 'e',
                "off": 'n'
            }
            options_iter = cycle(n_options.keys())
            for option in options_iter:
                if self.user.notifications == option:
                    break
            self.user.notifications = arg_hash.get(opts.notify) or next(options_iter)
            fh.save_user(self.user)
            log_msg = (
                "Notification settings changed to %s"
                % n_options[self.user.notifications]
            )
            fh.log(log_msg, "info")
            if (
                self.user.notifications in {"Y", "e"}
                and not self.user.gmail_address
            ):
                fh.log("No email user set, running email set up wizard...", "info")
                self.user.set_email()
                fh.save_user(self.user)

        elif opts.force:
            fh.log("***Forcing API call***", "info")
            if opts.force is not True:
                self.current_ip = opts.force
                fh.log(f"Using IP: {opts.force}", "info")
            self.changed = True


if __name__ == "__main__":
    IPChecker(sys.argv[1:])
