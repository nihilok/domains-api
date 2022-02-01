import os
from pathlib import Path

with open(Path(os.path.dirname(__file__)) / "version.txt", "r") as f:
    __VERSION__ = f.read().strip()

api_responses = {
    "nohost": {
        "status": False,
        "help_text": "The hostname doesn't exist, "
        "or doesn't have Dynamic DNS enabled.",
    },
    "notfqdn": {
        "status": False,
        "help_text": "The supplied hostname isn't a "
        "valid fully-qualified domain name.",
    },
    "badauth": {
        "status": False,
        "help_text": "The username/password combination "
        "isn't valid for the specified host.",
    },
    "badagent": {
        "status": False,
        "help_text": "Your Dynamic DNS client makes bad requests. "
        "Ensure the user agent is set in the request.",
    },
    "conflict": {
        "status": False,
        "help_text": "A custom A or AAAA resource record conflicts with the update. "
        "Delete the indicated resource record within the DNS settings page "
        "and try the update again.",
    },
    "abuse": {
        "status": False,
        "help_text": "Dynamic DNS access for the hostname has been blocked "
        "due to failure to interpret previous responses correctly.",
    },
    "911": {
        "status": False,
        "help_text": "An error happened on our end. Wait 5 minutes and retry.",
    },
    "nochg": {
        "status": True,
        "help_text": "The supplied IP address is already set for this host. "
        "You should not attempt another update until your IP address changes.",
    },
    "good": {
        "message": "IP Changed successfully.",
        "status": True,
        "help_text": "The update was successful. "
        "You should not attempt another update until your IP address changes.",
    },
}
