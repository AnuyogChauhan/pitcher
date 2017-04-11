
import os
import socket
import sys
sys.path.append('lib')
sys.path.append('lib/lib')

from lib.BroadcastRecipient import BroadcastRecipient
from CarPacket import CarPacket
from CarPacket import WrongSizeException
from carcalc import calcSpeed, calcDist
from random import randint
import logging

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')

class CarRecipient(BroadcastRecipient):
    def __init__(self, socket2, address2):
        self.s = socket2
        self.address = address2
        self.connected = True

    def processBeforePublish(self, instruction):
        car_packet = None
        if type(instruction) == bytes:
            try:
                car_packet = CarPacket.fromBytes(instruction)
            except WrongSizeException:
                car_packet = CarPacket.fromSimpleString(instruction.decode('utf-8'))
        elif type(instruction) == str:
            car_packet = CarPacket.fromSimpleString(instruction)

        if car_packet is not None:
            car_packet.speed = int(calcSpeed(car_packet.analog))
            car_packet.dist = int(calcDist(car_packet.analog))
            logging.debug(car_packet.toString())
            return car_packet.asBytes()
        else:
            return None

if __name__ == "__main__":
    cr = CarRecipient()
    cp = CarPacket(randint(0, 1000), randint(0, 100), randint(0, 100), 100, True)
    cr.processBeforePublish(cp)
