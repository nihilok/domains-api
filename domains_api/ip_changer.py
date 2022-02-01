import re
from getpass import getpass
from typing import List, Optional

from requests import get, post

from domains_api import __VERSION__, FileHandlers, User, api_responses, parser
from domains_api.exceptions import UserInstanceNotRecognised, UserNotSetup


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
            self.user = User.update_user_instance(user)
            self.user.send_notification(clear=True, log_fn=self.fh.log)
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
                self.user.last_ip = ip
                self.fh.save_user(self.user)
                self.parse_api_response(self.call_api(ip))
        except Exception as e:
            self.user.send_notification(self.user.last_ip, "error", e.__str__())

    def call_api(self, ip: str) -> str:
        return post(f"{self.user.req_url}&myip={ip}").text

    def parse_api_response(self, response: str) -> bool:
        """Parse response from Google Domains API call"""
        keys = api_responses.keys()
        for key in keys:
            if key in response:
                response_data = api_responses[key]
                break
        help_text = f'API response: {response}: {response_data["help_text"]}'
        status = response_data["status"]
        if not status:
            help_text += (
                " ...see https://support.google.com/domains/answer/6147083?hl=en-CA "
                "for API documentation"
            )
        log_type = "info" if status else "warning"
        self.fh.log(help_text, log_type)
        if "good" in response:
            ip = response.split()[1]
            self.user.send_notification(ip, log_fn=self.fh.log)
        elif "nochg" in response:
            pass
        else:
            self.user.send_notification(
                type="error", error=f"{response}: {help_text}", log_fn=self.fh.log
            )
        return not not status

    def check_user(self):
        if self.user is None:
            raise UserNotSetup

    def parse_args(self, argv: List[str]):
        """Parse command line options (domains -h)"""
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
        if opts.email:
            if self.user.email_wizard():
                self.fh.save_user(self.user)
            if not opts.test_email:
                return
        if opts.test_email:
            self.user.send_test_message(self.fh.log)
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
            if type(opts.force) == str:
                pattern = r"(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})"
                if re.search(pattern, opts.force.strip()):
                    self.user.last_ip = opts.force
                    self.fh.log(f"Overriding IP: {opts.force}", "info")
                    self.fh.save_user(self.user)
                else:
                    print(f"'{opts.force}' is not a recognised IPv4 address")
                    print("Using last IP")
            self.parse_api_response(self.call_api(self.user.last_ip))

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
