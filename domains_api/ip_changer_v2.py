from dataclasses import dataclass
from getpass import getpass
from itertools import cycle
from typing import Optional, List

from requests import get, post

from domains_api.file_handlers import FileHandlers
from domains_api.arg_parser import parser
from domains_api.constants import __VERSION__


class UserNotSetupException(Exception):
    def __init__(self):
        message = (
            "User profile has not been set up.\nEither run from the command line to run the user setup wizard, "
            "or manually set domain and password properties in your application.\n"
            "Refer to documentation for further details."
        )
        super().__init__(message)


@dataclass
class User:
    domain: str
    api_key: str
    api_sec: str
    email_notifications: str
    BASE_URL = "@domains.google.com/nic/update?hostname="
    gmail_address: Optional[str] = None
    gmail_app_password: Optional[str] = None
    last_ip: Optional[str] = None

    def set_domain(self, domain: str):
        self.domain = domain

    def set_api_credentials(self, api_key: str, api_sec: str):
        self.api_key = api_key
        self.api_sec = api_sec

    def set_notifications(self, n: str):
        self.email_notifications = n

    def set_email(self, email: str, password: str):
        self.gmail_address = email
        self.gmail_app_password = password


class IPChanger:

    fh = FileHandlers()

    def __init__(self, argv: Optional[List[str]] = None):
        self.user: Optional[User] = None
        self.changed: bool = False
        if argv is not None:
            self.parse_args(argv)

    def load_user(self, cli=False):
        try:
            self.user = self.fh.load_user(self.fh.user_file)
        except Exception:
            if cli is True:
                self.cli_user_setup()
            else:
                raise UserNotSetupException

    @staticmethod
    def get_ip():
        return get('https://api.ipify.com').text

    def check_ip(self):
        self.check_user()
        if ip := self.get_ip() != self.user.last_ip:
            self.call_api(ip)

    def call_api(self, ip: str):
        return post(f"{self.user.req_url}&myip={ip}").text

    def parse_api_response(self, response: str):
        log_msg = "DDNS API response: %s" % response
        self.fh.log(log_msg, "info")

        # Successful request:
        if "good" in response:
            self.user.send_notification(self.current_ip)
            log_msg = f"IP changed successfully to {self.current_ip}"
            self.fh.log(log_msg, "info")
        elif "nochg" in response:
            log_msg = "No change to IP"
            self.fh.log(log_msg, "info")

        # Unsuccessful requests:
        elif response in {"nohost", "notfqdn"}:
            msg = (
                "The hostname does not exist, is not a fully qualified domain"
                " or does not have Dynamic DNS enabled. The script will not be "
                "able to run until you fix this. See https://support.google.com/domains/answer/6147083?hl=en-CA"
                " for API documentation"
            )
            self.fh.log(msg, "warning")
            self.user.send_notification(self.current_ip, "error", msg)
        else:
            self.fh.log("Could not authenticate with these credentials", "warning")

    def check_user(self):
        if self.user is None:
            raise UserNotSetupException

    def parse_args(self, argv: List[str]):
        opts = parser.parse_args(argv)
        if {"-h", "--help", "-i", "--ip", "-l", "--load_user", "-v", "--version"}.difference(argv):
            self.load_user()
        if opts.ip:
            print(self.get_ip())
            return
        if opts.version:
            print(__VERSION__)
            return
        elif opts.domain:
            print(self.user.domain)
            return
        elif opts.delete_user:
            self.fh.delete_user()
            return
        elif opts.email:
            self.user.set_email()
            self.fh.save_user(self.user)
            self.fh.log("Notification settings changed", "info")

        elif opts.load_user:
            if input("Are you sure you want to load a new user? [Y/n] ").lower() == "n":
                return
            self.user = self.fh.load_user(opts.load_user)
            self.fh.save_user(self.user)
            self.fh.log("New user loaded", "info")

        elif opts.notify:
            n_options = {"Y": "[all changes]", "e": "[errors only]", "n": "[none]"}
            arg_hash = {"all": "Y", "errors": "e", "off": "n"}
            options_iter = cycle(n_options.keys())
            for option in options_iter:
                if self.user.notifications == option:
                    break
            self.user.notifications = arg_hash.get(opts.notify) or next(options_iter)
            self.fh.save_user(self.user)
            log_msg = (
                    "Notification settings changed to %s"
                    % n_options[self.user.notifications]
            )
            self.fh.log(log_msg, "info")
            if self.user.notifications != 'n' and not self.user.gmail_address:
                self.fh.log("No email user set, running email set up wizard...", "info")
                self.user.set_email()
                self.fh.save_user(self.user)

        elif opts.force:
            self.fh.log("***Forcing API call***", "info")
            if opts.force is not True:
                self.current_ip = opts.force
                self.fh.log(f"Using IP: {opts.force}", "info")
            self.call_api(self.current_ip)

    def cli_user_setup(self):
        print("Performing user profile setup wizard....")
        self.user = User(
            domain=input(
                "What's the domain you wish to monitor? (include subdomain if relevant) "
            ),
            api_key=input("What's the autogenerated API key for this domain? "),
            api_sec=getpass("What's the autogenerated API secret for this domain? "),
            email_notifications=input(
                "Would you like to turn on email notifications for this domain? (You can change this later) "
                "[Y: yes to all; e: errors only; n: no emails] "
            ).lower()
            or "y",
        )
        if self.user.email_notifications != "n":
            self.user.gmail_address = input("What's your gmail address? ")
            self.user.gmail_app_password = getpass("What's your gmail app password? ")
        self.fh.save_user(self.user)
