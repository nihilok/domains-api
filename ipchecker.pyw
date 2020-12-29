import os
import time
import logging

from requests import get
import smtplib
from email.message import EmailMessage
import base64

import password_enc

logging.basicConfig(filename='ipchecker.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

GMAIL_USER = 'mjfullstack@gmail.com'
GMAIL_PASSWORD = None


import getpass
USER_NAME = getpass.getuser()

startup_script = r'''f:
cd Coding\ipChecker
c:\Users\%s\AppData\Local\Programs\Python\Python39\pythonw.exe ipchecker.pyw
timeout 2 >nul
exit
''' % USER_NAME


def add_to_startup(file_path=""):
    if file_path == "":
        file_path = os.path.dirname(os.path.realpath(__file__))
    bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % USER_NAME
    if not os.path.isfile(bat_path + '\\' + "ipchecker.bat"):
        with open(bat_path + '\\' + "ipchecker.bat", "w+") as bat_file:
            bat_file.write(startup_script)
        logger.info('IP checker added to Startup folder.')
    else:
        logger.info('IP checker is already in Startup folder.')


def read_pwd():
    global GMAIL_PASSWORD
    with open('cred.txt', 'r') as f:
        pwd = f.read()
        if pwd:
            GMAIL_PASSWORD = base64.b64decode(pwd).decode('utf-8')


read_pwd()

if not GMAIL_PASSWORD:
    password_enc.enc_pwd()
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
    # Check previous IP
    logger.info('Public IP address is: {}'.format(IP))
    with open('ip.txt', 'r') as rf:
        line = rf.readlines()
        if not line:
            first_run = True
        elif line[0] == IP:
            first_run = False
            change = False
        else:
            logger.info(f'Old IP: {line[0]}')
            logger.info(f'New IP: {IP}')
            first_run = False
            change = True

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
        check_ip()
    else:
        logger.info('No change')
    logger.info('Check completed. (Next check in 6 hours...)')
    time.sleep(21600)
    check_ip()


if __name__ == '__main__':
    add_to_startup()
    check_ip()
