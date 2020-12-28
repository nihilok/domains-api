import base64


def enc_pwd():
    pwd = base64.b64encode(input("What's your password?: ").encode("utf-8"))
    with open('cred.txt', 'wb') as f:
        f.write(pwd)
