#!/usr/bin/python3
import os
import subprocess
import logging
import time
import smtplib
import base64
from requests import get, post
from email.message import EmailMessage

logging.basicConfig(filename='ipchecker.log', level=logging.INFO,
                    format='[%(levelname)s]|%(asctime)s|%(message)s')
logger = logging.getLogger(__name__)

GMAIL_USER = 'mjfullstack@gmail.com'
GMAIL_PASSWORD = None
REQ_URL = 'https://vfLzzIJ7fsF70BSO:qCgyuxax90hqx0Yc@domains.google.com/nic/update?hostname=@.mjfullstack.com&myip='

def read_pwd():
    global GMAIL_PASSWORD
    if os.path.isfile("cred.txt"):
        with open('cred.txt', 'r') as f:
            pwd = f.read()
            if pwd:
                GMAIL_PASSWORD = base64.b64decode(pwd).decode('utf-8')
                logging.info('Password read successfully')
    else:
        logger.warning('No encoded email password stored. Running script to create one...')
        subprocess.call(r'python3 password_enc.py', shell=True)
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
    logger.info('Checking IP...')
    logger.info('Public IP address is: {}'.format(IP))
    # Check for ip.txt and create if doesn't exist or edit if IP changes
    if os.path.isfile("ip.txt"):
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
                logger.info('IP has changed; new IP recorded locally')
                send_notification(IP)
                try:
                    req = post(f'{REQ_URL}{IP}')
                    logging.info(f'Response from domains api: {req.content}')
                except Exception as e:
                    logging.warning(f'Something went wrong: {e}')
    logger.info('Check completed.')


if __name__ == '__main__':
    logger.info('Process started...')
    read_pwd()
    check_ip()
