import sys

from . import User, IPChanger


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


if __name__ == '__main__':
    IPChanger(sys.argv[1:])

    from gkeep_funcs import gkeep_login