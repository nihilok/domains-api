from ipchecker import User
from gkeep_funcs import gkeep_login, create_note

user = User()


def change_previous_ip():
    user.previous_ip = '42'
    user.save_user()


def read_api_auth_details():
    keep = gkeep_login()
    g_notes = keep.find(query=user.domain)
    username, password, domain = None, None, None
    try:
        for note in g_notes:
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


def save_keys_to_keep_notes():
    title = user.domain
    text = f'{user.DNS_username}\n{user.DNS_password}'
    note = create_note(title, text, 'domains api')
    return note


if __name__ == "__main__":
    # create_note(input('Title: '), input('Note: '), input('Label: '))
    auto_create_api_profile()