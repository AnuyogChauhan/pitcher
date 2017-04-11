
import socket
import sys
from time import sleep
sys.path.append('lib')
sys.path.append('lib/lib')
from SimpleBroadcast import SimpleBroadcast
from CarPacket import CarPacket

class CarBroadcast(SimpleBroadcast):
    def __init__(self, host1='localhost', port1=5002):
        super(CarBroadcast, self).__init__(host1=host1, port1=port1)
        
    def encodeValue(self, value):
        return value.asBytes()

from random import randint
from time import time
if __name__ == "__main__":
    # sb = CarBroadcast(socket.gethostname(),4999)
    # sb = CarBroadcast(host2='slow.secret.equipment')
    sb = CarBroadcast(host2='fast.secret.equipment')
    sb.connect()
    start_time = time()
    for a in range(0,20):
        v1 = abs(randint(0, 3000))
        v2 = abs(randint(0, 100))
        v3 = abs(randint(0, 100))
        print(v2)
        sb.broadcast(CarPacket(v1,v2, v3, a, True))
        sleep(0.01)

    print("total time {0}".format(time()-start_time))
