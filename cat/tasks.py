
from .models import *


def get_stand():
    env = TestEnvironment()
    env.acquire()


def release_stand(rec_hash):
    env = TestEnvironment()
    env.release(hash=rec_hash)


def auto_release_stand():
    env = TestEnvironment()
    env.auto_release()
