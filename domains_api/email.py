import smtplib

from domains_api.encrypter import encrypter

def send_emails(message: str, outbox):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.ehlo()
    server.login(
    self.gmail_address, encrypter.decrypt(self.gmail_app_password).decode()
    )

    box = self.outbox
    for m in box:
    server.send_message(m)
    self.outbox.remove(m)

    if msg is not None:
        server.send_message(msg)
    server.close()
    return True                              
