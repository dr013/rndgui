
from .models import *


def getFreeServer():
    env = TestEnvironment()
    env.acquire()


def releaseServer(hash):
    env = TestEnvironment()
    env.release(hash=hash)


def autoRelease():
    env = TestEnvironment()
    env.auto_release()
