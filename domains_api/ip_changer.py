import sys

from getpass import getpass

from requests import post
from requests.exceptions import ConnectionError as ReqConError

from .ip_checker import BaseUser, IPChecker, fh


class DomainsUser(BaseUser):
    BASE_URL = '@domains.google.com/nic/update?hostname='

    def __init__(self):
        super().__init__()
        self.ref = self.domain
        self.domain, self.dns_username, self.dns_password, self.req_url = self.set_domains_credentials()

    def set_domains_credentials(self):
        """Set/return attributes for Google Domains credentials"""
        self.domain = input("What's your domain? (example.com / subdomain.example.com): ")
        self.dns_username = input("What's your autogenerated dns username?: ")
        self.dns_password = getpass("What's your autogenerated dns password?: ")
        self.req_url = f'https://{self.dns_username}:{self.dns_password}{self.BASE_URL}{self.domain}'
        return self.domain, self.dns_username, self.dns_password, self.req_url


class IPChanger(IPChecker):
    def __init__(self, argv=None, user_type=DomainsUser):
        super().__init__(argv, user_type)
        if self.changed:
            self.domains_api_call()

    def check_ip(self):
        super().check_ip()
        if self.changed:
            self.domains_api_call()

    def domains_api_call(self):
        """Attempt to change the Dynamic DNS rules via the Google Domains API and handle response codes"""
        try:
            req = post(f'{self.user.req_url}&myip={self.current_ip}')
            response = req.text
            log_msg = 'Google Domains API response: %s' % response
            fh.log(log_msg, 'info')

            # Successful request:
            _response = response.split(' ')
            if 'good' in _response:
                self.user.send_notification(self.current_ip)
            elif 'nochg' in _response:
                return

            # Unsuccessful requests:
            elif response in {'nohost', 'notfqdn'}:
                msg = "The hostname does not exist, is not a fully qualified domain" \
                      " or does not have Dynamic DNS enabled. The script will not be " \
                      "able to run until you fix this. See https://support.google.com/domains/answer/6147083?hl=en-CA" \
                      " for API documentation"
                fh.log(msg, 'warning')
                if input("Recreate the API profile? (Y/n):").lower() != 'n':
                    self.user.set_credentials()
                    self.domains_api_call()
                else:
                    self.user.send_notification(self.current_ip, 'error', msg)
            else:
                fh.log("Could not authenticate with these credentials", 'warning')
                if input("Recreate the API profile? (Y/n):").lower() != 'n':
                    self.user.set_credentials()
                    self.domains_api_call()
                else:
                    fh.delete_user()
                    fh.log('API authentication failed, user profile deleted', 'warning')
        # Local connection related errors
        except (ConnectionError, ReqConError) as e:
            log_msg = 'Connection Error: %s' % e
            fh.log(log_msg, 'warning')
            self.user.send_notification(msg_type='error', error=e)

if __name__ == "__main__":
    IPChanger(sys.argv[1:])
