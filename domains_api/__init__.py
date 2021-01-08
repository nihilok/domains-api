#!/usr/bin/python3
import os
import sys
import getopt
import base64
import smtplib
from email.errors import MessageError
from email.message import EmailMessage
from getpass import getpass
from itertools import cycle

from requests import get, post
from requests.exceptions import ConnectionError as ReqConError

from domains_api.file_handlers import FileHandlers


def get_ip_only():
    """Gets current external IP from ipify.org"""
    current_ip = get('https://api.ipify.org').text
    return current_ip


class User:

    BASE_URL = '@domains.google.com/nic/update?hostname='

    def __init__(self):


        """Create user instance and save it for future changes to API and for email notifications."""

        self.domain, self.dns_username, self.dns_password, self.req_url = self.set_credentials()
        self.notifications, self.gmail_address, self.gmail_password = self.set_email()
        self.outbox = []


    def set_credentials(self):

        """Set/return attributes for Google Domains credentials"""

        self.domain = input("What's your domain? (example.com / subdomain.example.com): ")
        self.dns_username = input("What's your autogenerated dns username?: ")
        self.dns_password = getpass("What's your autogenerated dns password?: ")
        self.req_url = f'https://{self.dns_username}:{self.dns_password}{self.BASE_URL}{self.domain}'
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

    def send_notification(self, ip=None, msg_type='success', error=None, outbox_msg=None):

        """Notify user via email if IP change is made successfully or if API call fails."""

        if self.notifications != 'n':
            msg = EmailMessage()
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
            try:
                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                server.ehlo()
                server.login(self.gmail_address, base64.b64decode(self.gmail_password).decode('utf-8'))
                server.send_message(msg)
                server.close()
                return True
            except (MessageError, ConnectionError) as e:
                log_msg = 'Email notification not sent: %s' % e
                self.outbox.append(msg)
                return False


class IPChanger:

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
        self.fh = FileHandlers()
        if os.path.isfile(self.fh.user_file):
            self.user = self.fh.load_user(self.fh.user_file)
            self.fh.log('User loaded from pickle', 'debug')
        else:
            self.user = User()
        self.current_ip = self.get_set_ip()

        # Parse command line options:
        try:
            opts, _args = getopt.getopt(argv, self.ARG_STRING, self.ARG_LIST)
        except getopt.GetoptError:
            print('''Usage:
python/python3 -m domains_api --help''')
            sys.exit(2)
        if opts:
            self.arg_parse(opts)

        # Check IPs:
        try:
            if self.user.previous_ip == self.current_ip:
                log_msg = 'Current IP: %s (no change)' % self.user.previous_ip
            else:
                self.user.previous_ip = self.current_ip
                self.domains_api_call()
                log_msg = 'Newly recorded IP: %s' % self.user.previous_ip
                self.fh.save_user(self.user)
            self.fh.log(log_msg, 'info')
        except AttributeError:
            setattr(self.user, 'previous_ip', self.current_ip)
            self.fh.save_user(self.user)
            self.domains_api_call()
        finally:
            if self.fh.op_sys == 'pos' and os.geteuid() == 0:
                self.fh.set_permissions(self.fh.user_file)

        # Send outbox emails:
        if self.user.outbox:
            for msg in self.user.outbox:
                self.user.send_notification(outbox_msg=msg)
                self.fh.log('Outbox message sent', 'info')

    def get_set_ip(self):

        """Gets current external IP from ipify.org and sets self.current_ip"""

        try:
            return get_ip_only()
        except ReqConError as e:
            self.fh.log('Connection Error. Could not reach api.ipify.org', 'warning')
            self.user.send_notification(ip=self.current_ip, msg_type='error', error=e)
            sys.exit(2)

    def domains_api_call(self):

        """Attempt to change the Dynamic DNS rules via the Google Domains API and handle response codes"""

        try:
            req = post(f'{self.user.req_url}&myip={self.current_ip}')
            response = req.text
            log_msg = 'Google Domains API response: %s' % response
            self.fh.log(log_msg, 'info')

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
                self.fh.log(msg, 'warning')
                if input("Recreate the API profile? (Y/n):").lower() != 'n':
                    self.user.set_credentials()
                    self.domains_api_call()
                else:
                    self.user.send_notification(self.current_ip, 'error', msg)
            else:
                self.fh.log("Could not authenticate with these credentials", 'warning')
                if input("Recreate the API profile? (Y/n):").lower() != 'n':
                    self.user.set_credentials()
                    self.domains_api_call()
                else:
                    self.fh.delete_user()
                    self.fh.log('API authentication failed, user profile deleted', 'warning')
                    sys.exit(2)
        except ReqConError as e:  # Local connection related errors
            log_msg = 'Connection Error: %s' % e
            self.fh.log(log_msg, 'warning')
            self.user.send_notification(self.current_ip, 'error', e)

    def arg_parse(self, opts):

        """Parses command line options: e.g. "python -m domains_api --help" """

        for opt, arg in opts:
            if opt in {'-i', '--ip'}:
                print('''
            [Domains API] Current external IP: %s
                ''' % get_ip_only())
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
        python -m domains_api -u user.file       || (or "--user_load path/to/user.file") -load user from pickle file
        python -m domains_api -d --delete_user   || -delete current user profile
                                                 || User files are stored in /site-packages/domains_api/*.user
    """
                )
            elif opt in {'-c', '--credentials'}:
                self.user.set_credentials(update=True)
                self.domains_api_call()
                self.fh.log('***API credentials changed***', 'info')
                self.fh.save_user(self.user)
            elif opt in {'-d', '--delete'}:
                self.fh.delete_user()
                self.fh.log('***User deleted***', 'info')
                print('>>>Run the script without options to create a new user, or '
                      '"python3 -m domains_api -u path/to/pickle" to load one from file')
            elif opt in {'-e', '--email'}:
                self.user.set_email()
                self.fh.save_user(self.user)
                self.fh.log('***Notification settings changed***', 'info')
            elif opt in {'-n', '--notifications'}:
                n_options = {'Y': '[all changes]', 'e': '[errors only]', 'n': '[none]'}
                options_iter = cycle(n_options.keys())
                for option in options_iter:
                    if self.user.notifications == option:
                        break
                self.user.notifications = next(options_iter)
                self.fh.save_user(self.user)
                log_msg = '***Notification settings changed to %s***' % n_options[self.user.notifications]
                self.fh.log(log_msg, 'info')
                if self.user.notifications in {'Y', 'e'} and not self.user.gmail_address:
                    self.fh.log('No email user set, running email set up wizard...', 'info')
                    self.user.set_email()
                    self.fh.save_user(self.user)
            elif opt in {'-u', '--user_load'}:
                try:
                    self.user = self.fh.load_user(self.fh.user_file)
                    self.fh.save_user(self.user)
                    self.fh.log('***User loaded***', 'info')
                except FileNotFoundError as e:
                    self.fh.log(e, 'warning')
                    sys.exit(2)
            sys.exit()


if __name__ == "__main__":
    IPChanger(sys.argv[1:])
