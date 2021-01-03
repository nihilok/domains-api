from ipchecker import User
import gkeepapi
import base64

user = User()
print(user.gmail_address)

keep = gkeepapi.Keep()
keep.login(user.gmail_address, base64.b64decode(user.gmail_password).decode('utf-8'))


def change_previous_ip():
    user.previous_ip = '42'
    user.save_user()


def read_api_auth_details():
    gnotes = keep.find(query=user.domain)
    username, password, domain = None, None, None
    try:
        for note in gnotes:
            note = str(note).split('\n')
            domain = note[0]
            username = note[1]
            password = note[2]
        return username, password, domain
    except IndexError:
        return username, password, domain


def auto_create_api_profile():
    user.DNS_username, user.DNS_password, user.domain = read_api_auth_details()
    user.save_user()

if __name__ == "__main__":
    pass