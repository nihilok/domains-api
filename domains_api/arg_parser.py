import argparse
from .constants import __VERSION__


class OptionalAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            values = True
        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser(
    description=f"Domains DDNS API version {__VERSION__}", prog="domains-api"
)
parser.add_argument(
    "-i", "--ip", action="store_true", help="get current external IP address"
)
parser.add_argument(
    "-l",
    "--load-user",
    help="load user data from file (eg domains.user)",
    metavar="<file>",
)
parser.add_argument(
    "-d",
    "--delete-user",
    action="store_true",
    help="delete current user data file (~/.domains-api/domains.user)",
)
parser.add_argument(
    "-f",
    "--force",
    action=OptionalAction,
    nargs="?",
    metavar="IP?",
    help="force a call to Google Domains API, optionally include an IP to use to override your own IP",
)
parser.add_argument(
    "-e",
    "--email",
    action="store_true",
    help="run email setup wizard",
)
parser.add_argument(
    "-p",
    "--profile-wizard",
    action="store_true",
    help="rerun user setup wizard (runs automatically if no user is found)",
)
parser.add_argument(
    "-n",
    "--notify",
    action=OptionalAction,
    nargs="?",
    choices=["all", "errors", "off"],
    help="toggle notifications for all events, errors only or off.",
)
