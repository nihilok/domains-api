import sys

from .ip_changer import DomainsUser, IPChanger


if __name__ == "__main__":

    IPChanger(sys.argv[1:])
