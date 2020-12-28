import time

from requests import get
import smtplib
from email.message import EmailMessage
import base64


GMAIL_USER = 'mjfullstack@gmail.com'

with open('cred.txt', 'r') as f:
    GMAIL_PASSWORD = base64.b64decode(f.readlines()[0]).decode('utf-8')

IP = get('https://api.ipify.org').text
print('Public IP address is: {}'.format(IP))


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
    except Exception as e:
        print(f'Something went wrong...:{e}')


def check_ip():
    # Check previous IP
    with open('ip.txt', 'r') as rf:
        line = rf.readlines()
        if not line:
            first_run = True
        elif line[0] == IP:
            first_run = False
            change = False
        else:
            print(f'New IP: {IP}')
            print(f'Old IP: {line[0]}')
            first_run = False
            change = True

    if first_run or change:
        # Write new IP
        with open('ip.txt', 'w') as wf:
            if first_run:
                wf.write(IP)
                print('First IP recorded')
            elif change:
                wf.write(IP)
                send_notification(IP)
                print('IP has changed; new IP recorded; notification sent')
        check_ip()
    print('Check completed.')
    time.sleep(21600)
    check_ip()


if __name__ == '__main__':
    check_ip()
