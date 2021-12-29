import sys

from .ip_changer import DomainsUser, IPChanger


if __name__ == "__main__":

    # # Uncomment to simulate a change of IP:
    # user = User()
    # def change_previous_ip():
    #     user.previous_ip = '42'
    #     user.save_user()
    # change_previous_ip()

    IPChanger(sys.argv[1:])
