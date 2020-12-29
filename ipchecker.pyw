import os
import subprocess
import logging
import time
import smtplib
import base64
from requests import get
from email.message import EmailMessage

from ipchanger import auto_edit_forwarding

logging.basicConfig(filename='ipchecker.log', level=logging.INFO,
                    format='%(asctime)s|%(levelname)s|%(message)s')
logger = logging.getLogger(__name__)

GMAIL_USER = 'mjfullstack@gmail.com'
GMAIL_PASSWORD = None
FILE_PATH = os.path.dirname(os.path.realpath(__file__))

import getpass
USER_NAME = getpass.getuser()

startup_script = r'''f:
cd Coding\ipChecker
pythonw ipchecker.pyw
exit
'''


def add_to_startup():
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    if not os.path.isfile(bat_path + '\\' + "ipchecker.bat"):
        with open(bat_path + '\\' + "ipchecker.bat", "w+") as bat_file:
            bat_file.write(startup_script)
        logger.info('IP checker added to Startup folder.')
    else:
        logger.info('IP checker is already in Startup folder.')


def read_pwd():
    global GMAIL_PASSWORD
    if os.path.isfile(FILE_PATH + '\\' + "cred.txt"):
        with open('cred.txt', 'r') as f:
            pwd = f.read()
            if pwd:
                GMAIL_PASSWORD = base64.b64decode(pwd).decode('utf-8')
                logging.info('Password read successfully')
    else:
        logger.warning('No encoded email password stored. Running script to create one...')
        subprocess.call(r'start /wait python password_enc.py', shell=True)
        time.sleep(3)
        read_pwd()


IP = get('https://api.ipify.org').text


def send_notification(new_ip):
    msg = EmailMessage()
    msg.set_content(f'IP has changed!\nNew IP: {new_ip}')
    msg['Subject'] = 'IP CHANGED!'
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_USER
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.close()
        logger.info(f'Email notification sent to {GMAIL_USER}')
    except Exception as e:
        logger.warning(f'Something went wrong:{e}')


def check_ip():
    logger.info('Public IP address is: {}'.format(IP))
    # Check for ip.txt
    if os.path.isfile(FILE_PATH + '\\' + "ip.txt"):
        # Check previous IP
        with open('ip.txt', 'r') as rf:
            line = rf.readlines()
            if not line:
                first_run = True
            elif line[0] == IP:
                first_run = False
                change = False
                logger.info('IP has not changed')
            else:
                logger.info(f'Old IP: {line[0]}')
                logger.info(f'New IP: {IP}')
                first_run = False
                change = True
    else:
        first_run = True
    if first_run or change:
        # Write new IP
        with open('ip.txt', 'w') as wf:
            if first_run:
                wf.write(IP)
                logger.info('First IP recorded')
            elif change:
                wf.write(IP)
                send_notification(IP)
                logger.info('IP has changed; new IP recorded')
                try:
                    logging.info(auto_edit_forwarding(IP))
                except Exception as e:
                    logging.warning(f'IP not changed at domains.google.com: {e}')
    logger.info('Check completed. (Next check in 6 hours...)')
    time.sleep(21600)
    check_ip()


if __name__ == '__main__':
    add_to_startup()
    read_pwd()
    check_ip()
