from getpass import getpass
from typing import Optional, List

from requests import get, post

from domains_api.exceptions import UserNotSetup, UserInstanceNotRecognised
from domains_api.file_handlers import FileHandlers
from domains_api.arg_parser import parser
from domains_api.constants import __VERSION__
from domains_api.user import User


class IPChanger:

    fh = FileHandlers()

    def __init__(self, argv: Optional[List[str]] = None, cli: bool = False):
        self.user: Optional[User] = None
        self.cli = cli
        if argv:
            self.parse_args(argv)
        elif self.cli:
            self.run()

    def run(self):
        """Attempt to load user if no user and run check, updating DDNS if necessary."""
        try:
            if self.user is None:
                self.load_user()
            self.check_ip()
        except UserNotSetup:
            if self.cli:
                self.user_setup_wizard()

    def load_user(self, user_file: Optional[str] = None):
        """Load user from file or raise UserException"""
        try:
            user = self.fh.load_user(user_file or self.fh.user_file)
            if not isinstance(user, User):
                raise UserInstanceNotRecognised
            self.user = user
            self.user.send_notification(clear=True)
        except Exception:
            self.check_user()

    @staticmethod
    def get_ip() -> str:
        return get("https://api.ipify.org").text

    def check_ip(self):
        """Check last recorded IP address against current external IP address"""
        self.check_user()
        try:
            if (ip := self.get_ip()) != self.user.last_ip:
                if self.parse_api_response(self.call_api(ip)):
                    self.user.last_ip = ip
        except Exception as e:
            self.user.send_notification(self.user.last_ip, "error", e.__str__())

    def call_api(self, ip: str) -> str:
        return post(f"{self.user.req_url}&myip={ip}").text

    def parse_api_response(self, response: str) -> bool:
        """Parse response from Google Domains API call"""
        log_msg = "DDNS API response: %s" % response
        self.fh.log(log_msg, "info")

        # Successful request:
        if "good" in response:
            self.user.send_notification(self.user.last_ip)
            log_msg = f"IP changed successfully to {self.user.last_ip}"
            self.fh.log(log_msg, "info")
            return True
        if "nochg" in response:
            log_msg = "No change to IP"
            self.fh.log(log_msg, "info")
            return True
        # Unsuccessful requests:
        if response in {"nohost", "notfqdn"}:
            msg = (
                "The hostname does not exist, is not a fully qualified domain"
                " or does not have Dynamic DNS enabled. The script will not be "
                "able to run until you fix this. See https://support.google.com/domains/answer/6147083?hl=en-CA"
                " for API documentation"
            )
            self.fh.log(msg, "warning")
            self.user.send_notification(self.user.last_ip, "error", msg)
        else:
            self.fh.log(
                "Could not authenticate with current credentials\n"
                "Hint: run `domains-test -p` to run setup wizard",
                "warning",
            )
        return False

    def check_user(self):
        if self.user is None:
            raise UserNotSetup

    def parse_args(self, argv: List[str]):
        """Parse command line options (domains-ddns -h)"""
        opts = parser.parse_args(argv)
        if opts.ip:
            print(self.get_ip())
            return
        if opts.version:
            print(__VERSION__)
            return
        if opts.load_user:
            if input("Are you sure you want to load a new user? [Y/n] ").lower() == "n":
                return
            self.load_user(opts.load_user)
            self.fh.save_user(self.user)
            self.fh.log("New user loaded", "info")
            return
        if opts.profile_wizard:
            self.user_setup_wizard()
            return
        self.load_user()
        if opts.domain:
            print(self.user.domain)
            return
        if opts.delete_user:
            self.fh.delete_user()
            return
        if opts.notify:
            notification_state = self.user.toggle_notifications(opts.notify)
            self.fh.save_user(self.user)
            log_msg = f"Notification settings changed to {notification_state}"
            self.fh.log(log_msg, "info")
            if self.user.email_notifications != "n" and not self.user.gmail_address:
                self.fh.log("No email user set, running email set up wizard...", "info")
                self.user.email_wizard()
                self.fh.save_user(self.user)
            return
        if opts.force:
            self.fh.log("***Forcing API call***", "info")
            if opts.force is not True:
                self.user.last_ip = opts.force
                self.fh.log(f"Using IP: {opts.force}", "info")
            self.call_api(self.user.last_ip)

    def user_setup_wizard(self):
        """Set up user profile from command line input"""
        print("Performing user profile setup wizard....")
        self.user = User(
            domain=input(
                "What's the domain you wish to update? (include subdomain if relevant) "
            ),
            api_key=input("What's the autogenerated API key for this domain? "),
            api_sec=getpass("What's the autogenerated API secret for this domain? "),
            email_notifications=input(
                "Would you like to turn on email notifications for this domain? (You can change this later) "
                "[Y: yes to all; e: errors only; n: no emails] "
            ).lower()
            or "y",
        )
        if self.user.email_notifications != "n" and not self.user.gmail_address:
            self.user.email_wizard()
        self.fh.save_user(self.user)
