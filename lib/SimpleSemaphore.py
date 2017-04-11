
import os
from os import path


class SimpleSemaphore(object):
    def __init__(self, word):
        self.filename = "/tmp/{0}".format(word)

    def turnOn(self):
        times = None
        fhandle = open(self.filename, 'a')
        try:
            os.utime(self.filename, times)
        finally:
            fhandle.close()

    def status(self):
        return path.isfile(self.filename)

    def turnOff(self):
        os.remove(self.filename)


if __name__ == "__main__":
    v = SimpleSemaphore("test")
    print(v.status())
    v.turnOn()
    print(v.status())
    v.turnOff()
    print(v.status())
