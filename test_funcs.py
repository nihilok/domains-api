from ipchecker import User

user = User()


def change_previous_ip():
    user.previous_ip = '42'
    user.save_user()


if __name__ == "__main__":
    change_previous_ip()