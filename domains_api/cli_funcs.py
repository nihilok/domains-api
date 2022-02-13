import argparse
from pickle import UnpicklingError
from typing import Callable, Sequence, Optional

from domains_api.constants import __VERSION__
from domains_api.exceptions import UserInstanceNotRecognised
from domains_api.ip_changer import IPChanger


def print_ip():
    print(IPChanger.get_ip())


_instance_singleton: Optional[IPChanger] = None
_actions_singleton: dict[str, Callable] = {}


class CLIAction(argparse.Action):
    non_user_actions: dict[str, Callable] = {
        "ip": print_ip,
        "version": lambda: print(__VERSION__),
        "delete_user": IPChanger.fh.delete_user,
    }
    instance = None

    def __init__(
        self, option_strings: Sequence[str], dest: str, nargs=0, *args, **kwargs
    ):
        super().__init__(option_strings, dest, nargs, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        global _instance_singleton
        global _actions_singleton
        if self.dest not in self.non_user_actions.keys():
            if _instance_singleton is None:
                _instance_singleton = IPChanger()
                _instance_singleton.load_user()

        self.instance = _instance_singleton
        if self.non_user_actions.get(self.dest):
            self.non_user_actions[self.dest]()
            return
        if not _actions_singleton:
            _actions_singleton = (
                {
                    "domain": self.print_domain,
                    "load_user": lambda filename: self.load_user(filename),
                    "email": self.instance.user.email_wizard,
                    "test_email": self.send_test_message,
                    "profile_wizard": self.instance.user_setup_wizard,
                    "force": lambda ip: self.instance.force_change(ip),
                    "notify": lambda opt: self.toggle_notifications(opt),
                }
                if self.instance is not None
                else {}
            )
        actions = _actions_singleton
        func = actions[self.dest]
        if values:
            try:
                if type(values) is str:
                    values = [values]
                func(*values)
            except FileNotFoundError as e:
                print(f"{e.__class__.__name__}: {e.__str__()}")
            except UnpicklingError:
                e = UserInstanceNotRecognised()
                print(f"{e.__class__.__name__}: {e.__str__()}")

        elif self.dest in {"force", "notify"}:
            func(None)
        else:
            func()

    def print_domain(self):
        print(self.instance.user.domain)

    def toggle_notifications(self, opt: str = None):
        notification_state = self.instance.user.toggle_notifications(opt)
        self.instance.fh.save_user(self.instance.user)
        log_msg = f"Notification settings changed to {notification_state}"
        self.instance.fh.log(log_msg, "info")
        if (
            self.instance.user.email_notifications != "n"
            and not self.instance.user.gmail_address
        ):
            self.instance.fh.log(
                "No email user set, running email set up wizard...", "info"
            )
            self.instance.user.email_wizard()
            self.instance.fh.save_user(self.instance.user)

    def load_user(self, user_file: str):
        if input("Are you sure you want to load a new user? [Y/n] ").lower() == "n":
            return
        self.instance.load_user(user_file)

    def send_test_message(self):
        print("Sending test message...")
        self.instance.user.send_test_message(log_fn=self.instance.fh.log)
