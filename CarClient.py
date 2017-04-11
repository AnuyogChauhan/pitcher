
import socket
from time import time, sleep
import threading
import os
import sys
sys.path.append('lib')
sys.path.append('lib/lib')
import logging
from CarPacket import WrongSizeException
from carcalc import calcActualSpeed
#from pythonosc import osc_message_builder
#from pythonosc import udp_client
import liblo
from uuid import uuid4
try:
    import serial
except ImportError:
    print("serial library not imported")

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')
sys.path.append('./')
sys.path.append('lib')
sys.path.append('lib/lib')

from SimpleClient import SimpleClient
from CarPacket import CarPacket

device_location = '/dev/xbee'

if len(sys.argv) > 1:
    device_location = sys.argv[1]
    logging.debug(device_location)

class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

class CarClient(SimpleClient):
    def __init__(self, host2='localhost', port2=5002):
        super(CarClient, self).__init__(host2, port2)
        #self.carsReady = False
	self.carsReady = True
        self.ser = None
        self.theta = 2
        self.isDriving = False
        self.lastWrite = int(time())
        self.numberOfBytesToRead = CarPacket.size()

#        self.screen_client = udp_client.UDPClient('127.0.0.1', 7002)
	self.screen_client2 = liblo.Address('127.0.0.1', 7002)

        try:
            self.ser = serial.Serial(device_location, 9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=None)
        except NameError:
            logging.error("serial not available")
        except serial.serialutil.SerialException:
            logging.error("serial not available")

        logging.info("initialized")

    def decodeValue(self, value):
        logging.debug(value)
        try:
            if type(value) == bytes:
                logging.debug("it was bytes!")
                return CarPacket.fromBytes(value)
            elif type(value) == str:
                logging.debug("it was a string!")
                return CarPacket.fromSimpleString(value.decode('utf-8'))

        except WrongSizeException:
            logging.error("wrong size exception")
            return CarPacket.fromSimpleString(value.decode('utf-8'))
        except Exception:
            logging.error("unknown exception")
            return None
        logging.error("uncaught")
        return None

    def fromBytesToString(self, value):
        logging.debug(" bytes to string invoked {0}".format(value))
        a = CarPacket.fromBytes(value)
        s1 = a.simpleString()
        return s1

    def useValue(self, message):
        logging.debug(message.toString())
        try:
            if self.carsReady:
                if message.analog > 50:
                    self.isDriving = True
                    targetLaptime = int((950 - message.analog) * 1.5 + 2000)
                    kph = int((message.analog-50) * 42 / 950 + 169) 
                    if message.edge:
                        dist = min(6.8, round(message.analog / 950 * self.theta * 2 + 3, 1))
                        msg = '+' + str(targetLaptime) + '/' + str(dist) + '&'
                    else:
                        dist = max(6.8, round(message.analog / 950 * self.theta * 2 + 3, 1))
                        msg = '+' + str(targetLaptime) + '/' + str(dist)
                    #self.screen_client.send(buildMessage('/cardata', kph, dist, message.edge))
		    liblo.send(self.screen_client2, '/cardata', kph, dist, message.edge)
                else:
                    self.isDriving = False
                    #self.screen_client.send(buildMessage('/cardata', 0, 0, message.edge))
		    liblo.send(self.screen_client2, '/cardata', 0, 0, message.edge)
                    msg = '+S'

            else:
                self.isDriving = False
                msg = '+S'
                #paused = osc_message_builder.OscMessageBuilder(address='/paused')
                #self.screen_client.send(paused.build())
		liblo.send(self.screen_client2, "/paused")

            msg += '\n'

            if self.ser is not None:
                logging.debug(msg)
                self.ser.write(msg.encode('utf-8'))

        except Exception as e:
            logging.error("error handling received packet or writing serial %s" %(e))
            raise Exception()

def buildMessage(address1, speed, dist, edge):
    builder = osc_message_builder.OscMessageBuilder(address=address1)
    builder.add_arg(speed, builder.ARG_TYPE_INT)
    builder.add_arg(dist, builder.ARG_TYPE_FLOAT)
    if edge:
        builder.add_arg(edge, builder.ARG_TYPE_TRUE)
    else:
        builder.add_arg(edge, builder.ARG_TYPE_FALSE)

    return builder.build()

if __name__ == "__main__":
    # sc = CarClient(host2='frogsf-dt3',port2=4999)
    sc = CarClient(host2='fast.secret.equipment',port2=5002)
    #sc = CarClient(socket.gethostname(), 4999)
    #sc = CarClient(host2='slow.secret.equipment', port2=5002)
    sc.subscribe()
