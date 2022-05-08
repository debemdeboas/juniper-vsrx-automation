# Adapted from https://stackoverflow.com/a/33727932/9918829

from passlib.hash import md5_crypt
from getpass import getpass

pswd = getpass('Password: ')
print('Your MD5-hashed password is', md5_crypt.hash(pswd))
