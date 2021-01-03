import sys

from . import User, IPChanger

if __name__ == '__main__':
    IPChanger(sys.argv[1:])