from ipchecker import User, IPChanger
import pickle
import gkeepapi
import base64

with open('.user', 'rb') as pickle_file:
    user = pickle.load(pickle_file)

user_pwd = base64.b64decode(user.gmail_password).decode('utf-8')

keep = gkeepapi.Keep()
keep.login(user.gmail_address, user_pwd)


def change_previous_ip():
    user.previous_ip = '42'

    with open('.user.pickle', 'wb') as pickle_file:
        pickle.dump(user, pickle_file)


def read_api_auth_details():
    gnotes = keep.find(query='domains')
    username, password = None, None
    try:
        for note in gnotes:
            note = str(note).split('\n')
            username = note[1]
            password = note[2]
        return username, password
    except IndexError:
        return username, password


def auto_create_api_profile():
    user.domain = 'mjfullstack.com'
    user.DNS_username, user.DNS_password = read_api_auth_details()
    with open('.user', 'wb') as user_pickle:
        pickle.dump(user, user_pickle)
