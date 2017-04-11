
import socket
from time import time
from time import sleep
import logging

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')


class ClientDisconnectedException(Exception):
    pass

class SimpleClient(object):
    def __init__(self, host1='localhost', port1=5004):
        self.host = host1
        self.port = port1
        self.lastMessageTimes = list()
        self.warningTime = 0.001
        self.numberOfBytesToRead = 36 
        self.messageNumber = 0
        self.conn = None
        self.connected = False
        self.reconnectTime = 2


    def subscribe(self, connection=None):
        while True:
            if connection is None and self.conn is None and not self.connected:
                logging.info("connection is None, self.conn is None, and not connected")
                self.conn = socket.socket()
                try:
                    self.conn.connect((self.host, self.port))
                    self.connected = True
                except Exception:
                    logging.warning("connection destroyed, sleeping")
                    sleep(self.reconnectTime)
                    self.connected = False
                    break
            elif self.conn is None:
                self.conn = connection
                self.connected = True
            try:
                if self.conn is None:
                    break
                logging.info('sending connection attempt')
                self.conn.sendall(b'CLIENT')
                while True:
                    data = self.conn.recv(self.numberOfBytesToRead)
                    if not data:
                        self.conn.close
                        self.conn = None
                        self.connected = False
                        break
                    elif data:
                        self.connected = True
                        
                    self.lastMessageTimes.append(time())
                    if len(self.lastMessageTimes) > 10:
                        if(time() - self.lastMessageTimes[0] < self.warningTime and self.conn is None):
                            logging.debug("last message times {0}".format(self.lastMessageTimes))
                            raise ClientDisconnectedException()
                        self.lastMessageTimes.pop(0)
                    self.useValue(self.decodeValue(data))

            except ClientDisconnectedException:
                self.connected = False
                self.conn = None 
                logging.warning("connection destroyed, sleeping")
                sleep(self.reconnectTime)
                break
            logging.warning("reconnection attempt")
            
    def setConnection(self, connection):
        self.conn = connection
        self.connected = True

    """
        used for test cases
    """
    def getOne(self,connection = None):
        if connection is None:
            self.conn = socket.socket()
            self.conn.connect((self.host, self.port))
        else:
            self.conn = connection
        self.conn.send(b'C')
        return self.conn.recv(self.numberOfBytesToRead)

    def decodeValue(self, value):
        return value

    def useValue(self, value):
        self.messageNumber += 1
        logging.debug("{0} {1}".format(self.messageNumber,self.decodeValue(value)))

if __name__ == "__main__":
    sc = SimpleClient(host1=socket.gethostname())
    sc.subscribe()
