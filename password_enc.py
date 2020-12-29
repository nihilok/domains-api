import base64
import logging
from getpass import getpass

logger = logging.getLogger(__name__)


def enc_pwd():
    pwd = base64.b64encode(getpass("What's your email password?: ").encode("utf-8"))
    with open('cred.txt', 'wb') as f:
        f.write(pwd)
    logger.info('Password stored')


if __name__ == '__main__':
    enc_pwd()
