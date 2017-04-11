
import os
import socket
import logging
import sys
sys.path.append('lib')

from lib.SimpleServer import SimpleServer
from lib.BroadcastRecipient import BroadcastRecipient
from CarPacket import CarPacket
from CarPacket import WrongSizeException 
from CarRecipient import CarRecipient

from time import sleep

class CarServer(SimpleServer):
    def __init__(self, port2=5002):
        super(CarServer, self).__init__(port1=port2)
        self.port = port2
        self.packetSize = CarPacket.size()
        if os.getenv("USE_REDIS") and not os.getenv("REDIS_SERVICE_HOST"):
            if os.getenv("USE_REDIS").find("TRUE") > -1:
                self.initRedis('localhost', 'car_value')
                
        redis_host = os.getenv('REDIS_SERVICE_HOST')

        if not redis_host:
            logging.error("REDIS_SERVICE_HOST not set")
            sys.exit(1)

        redis_port = 6397
        try:
            redis_port = int(os.getenv('REDIS_SERVICE_PORT'))
        except TypeError:
            logging.error("REDIS_SERVICE_PORT not available")

        if redis_host is None:
            print "REDIS_SERVICE_HOST not available"
            sys.exit(1)

        if os.getenv("USE_REDIS"):
            if os.getenv("USE_REDIS").find("TRUE") > -1:
                self.initRedis(redis_host, 'car_value', redis_port)
                logging.info("attempting to use redis with host %s and port %d watching value %s",redis_host,redis_port,'car_value')
            else:
                logging.error("not using redis, USE_REDIS != TRUE")
        else:
            logging.error("not using redis - USE_REDIS not set")
            
            
    
    def fromBytesToString(self, value):
        if type(value) == bytes:
            a = CarPacket.fromBytes(value)
            s1 = a.simpleString()
            return s1
        if type(value) == str:
            return value
    
    
    def addClient(self, connection, address1):
        if self.listener is None:
            self.clients.append(CarRecipient(connection, address1))
        if self.listener is not None:
            self.listener.addClient(CarRecipient(connection, address1))


if __name__ == "__main__":
    print("starting server")
    print(socket.gethostname())
    server = CarServer()
    #server.initRedis('127.0.0.1', 'car_value') 
    server.serve()
      
