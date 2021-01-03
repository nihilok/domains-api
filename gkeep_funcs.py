from ipchecker import User
from gkeepapi import Keep
import base64


user = User()
keep = Keep()


def gkeep_login():
    keep.login(user.gmail_address, base64.b64decode(user.gmail_password).decode('utf-8'))


def create_note(title='Test', text='Test note'):
    gkeep_login()
    note = keep.createNote(title, text)
    keep.sync()
    return note


