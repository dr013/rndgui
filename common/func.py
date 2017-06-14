from binascii import hexlify
import os


def create_hash():
    """This function generate 10 character long hash"""
    return hexlify(os.urandom(5))
