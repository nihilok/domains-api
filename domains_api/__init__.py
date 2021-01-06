#!/usr/bin/python3
import os
import sys
import getopt
import logging
import pickle
import base64
import smtplib
from email.errors import MessageError
from email.message import EmailMessage
from getpass import getpass
from itertools import cycle
from pathlib import Path

from requests import get, post
from requests.exceptions import ConnectionError as ReqConError


<<<<<<< HEAD
if os.name == "nt":
    LOG_FILE = Path(os.getenv('LOCALAPPDATA')) / '.domains-api.log'
    USER_PICKLE = Path(os.getenv('LOCALAPPDATA')) / '.domains.user'

else:
    DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_FILE = Path(DIR) / 'domains-api.log'
    USER_PICKLE = Path(DIR) / '.domains.user'
    os.chdir(DIR)


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler(LOG_FILE)
sh = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('[%(levelname)s]|%(asctime)s|%(message)s',
                              datefmt='%d %b %Y %H:%M:%S')
sh_formatter = logging.Formatter('[%(levelname)s]|[%(name)s]|%(asctime)s| %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)
sh.setFormatter(sh_formatter)
logger.addHandler(sh)
logger.addHandler(fh)


def arg_parse(opts, instance):

    """Parses command line options: e.g. "python -m domains_api --help" """

    for opt, arg in opts:
        if opt in {'-i', '--ip'}:
            log_msg = 'Current IP: %s' % instance.get_ip()
            logger.info(log_msg)
        elif opt in {'-h', '--help'}:
            print(
                """

    domains-api help manual (command line options):
    ```````````````````````````````````````````````````````````````````````````````````````
    python -m domains_api                    || -run the script normally without arguments
    python -m domains_api -h --help          || -show this help manual
    python -m domains_api -i --ip            || -show current external IP address
    python -m domains_api -c --credentials   || -change API credentials
    python -m domains_api -e --email         || -email set up wizard > use to delete email credentials (choose 'n')
    python -m domains_api -n --notifications || -toggle email notification settings > will not delete email address
    python -m domains_api -d --delete_user   || -delete current user profile
    python -m domains_api -u user.file       || (or "--user_load path/to/user.file") -load user from pickle file**
                                             || **this will overwrite any current user profile without warning!
                                             || **Backup "./.domains.user" file to store multiple profiles.
"""
            )
        elif opt in {'-c', '--credentials'}:
            user = User()
            user.set_credentials(update=True)
            instance.domains_api_call()
            logger.info('***API credentials changed***')
        elif opt in {'-d', '--delete'}:
            User.delete_user()
            logger.info('***User deleted***')
            print('>>>Run the script without options to create a new user, or '
                  '"python3 -m domains_api -u path/to/pickle" to load one from file')
        elif opt in {'-e', '--email'}:
            user = User()
            user.set_email()
            user.save_user()
            logger.info('***Notification settings changed***')
        elif opt in {'-n', '--notifications'}:
            n_options = {'Y': '[all changes]', 'e': '[errors only]', 'n': '[none]'}
            user = User()
            options_iter = cycle(n_options.keys())
            for option in options_iter:
                if user.notifications == option:
                    break
            user.notifications = next(options_iter)
            user.save_user()
            log_msg = '***Notification settings changed to %s***' % n_options[user.notifications]
            logger.info(log_msg)
            if user.notifications in ('Y', 'e') and not user.gmail_address:
                logger.info('No email user set, running email set up wizard...')
                user.set_email()
        elif opt in {'-u', '--user_load'}:
            try:
                user = User.load_user(pickle_file=arg)
                user.save_user()
                logger.info('***User loaded***')
            except FileNotFoundError as e:
                logger.warning(e)
                sys.exit(2)
        sys.exit()


class User:
=======
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


def file_handling(path=PACKAGE_DIR):
    if os.name == "nt":
        log_file = Path(os.getenv('LOCALAPPDATA')) / '.domains-api.log'
        user_pickle = Path(os.getenv('LOCALAPPDATA')) / '.domains.user'

    else:
        log_file = Path(path) / 'domains-api.log'
        user_pickle = Path(path) / '.domains.user'
    return log_file, user_pickle


LOG_FILE, USER_PICKLE = file_handling()


def initialize_logger(log_file):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_file)
    sh = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(levelname)s]|%(asctime)s|%(message)s',
                                  datefmt='%d %b %Y %H:%M:%S')
    sh_formatter = logging.Formatter('[%(levelname)s]|[%(name)s]|%(asctime)s| %(message)s',
                                     datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    sh.setFormatter(sh_formatter)
    logger.addHandler(sh)
    logger.addHandler(fh)
    return logger


logger = initialize_logger(LOG_FILE)


class User:

>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
    BASE_URL = '@domains.google.com/nic/update?hostname='

    def __init__(self):

<<<<<<< HEAD
        """Create user instance and save it for future changes to API and for email notifications,
        or load previous user profile"""

        if os.path.isfile(USER_PICKLE):
            self.__dict__.update(self.load_user().__dict__)
        else:
            self.domain, self.dns_username, self.dns_password, self.req_url = self.set_credentials()
            self.notifications, self.gmail_address, self.gmail_password = self.set_email()
            self.save_user()
            logging.info('New user created. (See `python3 ipchecker.py --help` for help changing/removing the user)')

    def set_credentials(self, update=False):
=======
        """Create user instance and save it for future changes to API and for email notifications."""

        self.domain, self.dns_username, self.dns_password, self.req_url = self.set_credentials()
        self.notifications, self.gmail_address, self.gmail_password = self.set_email()
        self.outbox = []
        self.save_user()
        logger.info('New user created. (See `python3 ipchecker.py --help` for help changing/removing the user)')

    def set_credentials(self):
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0

        """Set/return attributes for Google Domains credentials"""

        self.domain = input("What's your domain? (example.com / subdomain.example.com): ")
        self.dns_username = input("What's your autogenerated dns username?: ")
        self.dns_password = getpass("What's your autogenerated dns password?: ")
        self.req_url = f'https://{self.dns_username}:{self.dns_password}{self.BASE_URL}{self.domain}'
<<<<<<< HEAD
        if update:
            self.save_user()
=======
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
        return self.domain, self.dns_username, self.dns_password, self.req_url

    def set_email(self):

        """Set/return attributes for Gmail credentials if user enables notifications"""

        self.notifications = input("Enable email notifications? [Y]all(default); [e]errors only; [n]no: ").lower()
        if self.notifications != 'n':
            self.gmail_address = input("What's your email address?: ")
            self.gmail_password = base64.b64encode(getpass("What's your email password?: ").encode("utf-8"))
            if self.notifications != 'e':
                self.notifications = 'Y'
            return self.notifications, self.gmail_address, self.gmail_password
        else:
            return 'n', None, None

<<<<<<< HEAD
    def send_notification(self, ip, msg_type='success', error=None):
=======
    def send_notification(self, ip=None, msg_type='success', error=None, outbox_msg=None):
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0

        """Notify user via email if IP change is made successfully or if API call fails."""

        if self.notifications != 'n':
            msg = EmailMessage()
<<<<<<< HEAD
            if msg_type == 'success' and self.notifications not in ('n', 'e'):
                msg.set_content(f'IP for {self.domain} has changed! New IP: {ip}')
                msg['Subject'] = 'IP CHANGED SUCCESSFULLY!'
            elif msg_type == 'error' and self.notifications != 'n':
                msg.set_content(f'IP for {self.domain} has changed but the API call failed ({error})! New IP: {ip}')
                msg['Subject'] = 'IP CHANGE FAILED!'
            msg['From'] = self.gmail_address
            msg['To'] = self.gmail_address
=======
            msg['From'] = self.gmail_address
            msg['To'] = self.gmail_address
            if ip and msg_type == 'success' and self.notifications not in ('n', 'e'):
                msg.set_content(f'IP for {self.domain} has changed! New IP: {ip}')
                msg['Subject'] = 'IP CHANGED SUCCESSFULLY!'
            elif ip and msg_type == 'error' and self.notifications != 'n':
                msg.set_content(f'IP for {self.domain} has changed but the API call failed ({error})! New IP: {ip}')
                msg['Subject'] = 'IP CHANGE FAILED!'
            elif outbox_msg and not ip:
                msg = outbox_msg
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(self.gmail_address, base64.b64decode(self.gmail_password).decode('utf-8'))
                server.send_message(msg)
                server.close()
            except (MessageError, ConnectionError) as e:
                log_msg = 'Email notification not sent: %s' % e
                logger.warning(log_msg)
<<<<<<< HEAD

    def save_user(self):
        with open(USER_PICKLE, 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    @staticmethod
    def load_user(pickle_file=USER_PICKLE):
=======
                self.outbox.append(msg)

    def save_user(self):

        """Pickle (serialize) user instance."""

        with open(os.path.abspath(USER_PICKLE), 'wb') as pickle_file:
            pickle.dump(self, pickle_file)

    @staticmethod
    def load_user(pickle_file=os.path.abspath(USER_PICKLE)):

        """Unpickle (deserialize) user instance."""

>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
        with open(pickle_file, 'rb') as pickle_file:
            return pickle.load(pickle_file)

    @staticmethod
    def delete_user():
<<<<<<< HEAD
        os.remove(USER_PICKLE)
=======

        """Delete pickle file (serialized user instance)."""

        if input('Are you sure? (Y/n): ').lower() != 'n':
            os.remove(USER_PICKLE)
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0


class IPChanger:

<<<<<<< HEAD
    def __init__(self, argv=None):

        """Check for command line arguments, load User instance,
        check previous IP address against current external IP, and change if different."""

        self.current_ip = self.get_ip()
        try:
            opts, _args = getopt.getopt(argv, 'cdehinu:', ['credentials',
                                                           'delete_user',
                                                           'email',
                                                           'help',
                                                           'ip',
                                                           'notifications',
                                                           'user_load='])

=======
    ARG_STRING = 'cdehinu:'
    ARG_LIST = ['credentials',
                'delete_user',
                'email',
                'help',
                'ip',
                'notifications',
                'user_load=']

    def __init__(self, argv=None):

        """Check for command line arguments, load/create User instance,
        check previous IP address against current external IP, and change via the API if different."""

        # Load old user, or create new one:
        if os.path.isfile(USER_PICKLE):
            self.user = User.load_user()
        else:
            self.user = User()
        setattr(self.user, 'outbox', [])
        self.user.save_user()
        self.current_ip = self.get_ip()

        # Parse command line options:
        try:
            opts, _args = getopt.getopt(argv, self.ARG_STRING, self.ARG_LIST)
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
        except getopt.GetoptError:
            print('''Usage:
python/python3 -m domains_api --help''')
            sys.exit(2)
<<<<<<< HEAD
        except ReqConError:
            logger.warning('Connection Error')
            sys.exit(1)
        if opts:
            arg_parse(opts, self)
        try:
            self.user = User()
=======
        if opts:
            self.arg_parse(opts)

        # Check IPs:
        try:
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
            if self.user.previous_ip == self.current_ip:
                log_msg = 'Current IP: %s (no change)' % self.user.previous_ip
                logger.info(log_msg)
            else:
                self.user.previous_ip = self.current_ip
                self.domains_api_call()
                log_msg = 'Newly recorded IP: %s' % self.user.previous_ip
                logger.info(log_msg)
                self.user.save_user()
        except AttributeError:
            setattr(self.user, 'previous_ip', self.current_ip)
            self.user.save_user()
            self.domains_api_call()

<<<<<<< HEAD
    @staticmethod
    def get_ip():
        try:
            current_ip = get('https://api.ipify.org').text
            return current_ip
        except ReqConError:
            logger.warning('Connection Error')
            return
=======
        # Send outbox emails:
        if self.user.outbox:
            for msg in self.user.outbox:
                self.user.send_notification(outbox_msg=msg)
                logger.info('Outbox message sent')

    def get_ip(self):

        """Gets current external IP from ipify.org"""

        try:
            current_ip = get('https://api.ipify.org').text
            return current_ip
        except ReqConError as e:
            logger.warning('Connection Error. Could not reach ipify.org')
            self.user.send_notification(ip=self.current_ip, msg_type='error', error=e)
            sys.exit(2)
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0

    def domains_api_call(self):

        """Attempt to change the Dynamic DNS rules via the Google Domains API and handle response codes"""

        try:
            req = post(f'{self.user.req_url}&myip={self.current_ip}')
<<<<<<< HEAD
            response = req.text
            print(response)
=======
            response = req.content.decode('utf-8')
>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0
            log_msg = 'Google Domains API response: %s' % response
            logger.info(log_msg)

            # Successful request:
            _response = response.split(' ')
            if 'good' in _response or 'nochg' in _response:
                self.user.send_notification(self.current_ip)

            # Unsuccessful requests:
            elif response in {'nohost', 'notfqdn'}:
                msg = "The hostname does not exist, is not a fully qualified domain" \
                      " or does not have Dynamic DNS enabled. The script will not be " \
                      "able to run until you fix this. See https://support.google.com/domains/answer/6147083?hl=en-CA" \
                      " for API documentation"
                logger.warning(msg)
                if input("Recreate the API profile? (Y/n):").lower() != 'n':
                    self.user.set_credentials(update=True)
                    self.domains_api_call()
                else:
                    self.user.send_notification(self.current_ip, 'error', msg)
            else:
                logger.warning("Could not authenticate with these credentials")
                if input("Recreate the API profile? (Y/n):").lower() != 'n':
                    self.user.set_credentials(update=True)
                    self.domains_api_call()
                else:
                    self.user.delete_user()
                    logger.warning('API authentication failed, user profile deleted')
                    sys.exit(2)
        except ReqConError as e:  # Local connection related errors
            log_msg = 'Connection Error: %s' % e
            logger.warning(log_msg)
            self.user.send_notification(self.current_ip, 'error', e)

<<<<<<< HEAD
=======
    def arg_parse(self, opts):

        """Parses command line options: e.g. "python -m domains_api --help" """

        for opt, arg in opts:
            if opt in {'-i', '--ip'}:
                print('''
            [Domains API] Current external IP: %s
                ''' % self.get_ip())
            elif opt in {'-h', '--help'}:
                print(
                    """

        domains-api help manual (command line options):
        ```````````````````````````````````````````````````````````````````````````````````````
        You will need your autogenerated Dynamic DNS keys from
        https://domains.google.com/registrar/example.com/dns
        to create a user profile.

        python -m domains_api                    || -run the script normally without arguments
        python -m domains_api -h --help          || -show this help manual
        python -m domains_api -i --ip            || -show current external IP address
        python -m domains_api -c --credentials   || -change API credentials
        python -m domains_api -e --email         || -email set up wizard > use to delete email credentials (choose 'n')
        python -m domains_api -n --notifications || -toggle email notification settings > will not delete email address
        python -m domains_api -d --delete_user   || -delete current user profile
        python -m domains_api -u user.file       || (or "--user_load path/to/user.file") -load user from pickle file**
                                                 || **this will overwrite any current user profile without warning!
                                                 || **Backup "./.domains.user" file to store multiple profiles.
    """
                )
            elif opt in {'-c', '--credentials'}:
                self.user.set_credentials(update=True)
                self.domains_api_call()
                logger.info('***API credentials changed***')
                self.user.save_user()
            elif opt in {'-d', '--delete'}:
                User.delete_user()
                logger.info('***User deleted***')
                print('>>>Run the script without options to create a new user, or '
                      '"python3 -m domains_api -u path/to/pickle" to load one from file')
            elif opt in {'-e', '--email'}:
                self.user.set_email()
                self.user.save_user()
                logger.info('***Notification settings changed***')
            elif opt in {'-n', '--notifications'}:
                n_options = {'Y': '[all changes]', 'e': '[errors only]', 'n': '[none]'}
                options_iter = cycle(n_options.keys())
                for option in options_iter:
                    if self.user.notifications == option:
                        break
                self.user.notifications = next(options_iter)
                self.user.save_user()
                log_msg = '***Notification settings changed to %s***' % n_options[self.user.notifications]
                logger.info(log_msg)
                if self.user.notifications in ('Y', 'e') and not self.user.gmail_address:
                    logger.info('No email user set, running email set up wizard...')
                    self.user.set_email()
                    self.user.save_user()
            elif opt in {'-u', '--user_load'}:
                try:
                    self.user = User.load_user(pickle_file=arg)
                    self.user.save_user()
                    logger.info('***User loaded***')
                except FileNotFoundError as e:
                    logger.warning(e)
                    sys.exit(2)
            sys.exit()

>>>>>>> 449f7839a91f29ecc891fa06e3d37407d1cdccf0

if __name__ == "__main__":
    IPChanger(sys.argv[1:])
