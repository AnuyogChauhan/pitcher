
import socket
from time import time
from time import sleep


class ClientDisconnectedException(Exception):
    pass

class SimpleClient(object):
    def __init__(self, host1='localhost', port1=5004):
        self.host = host1
        self.port = port1
        self.lastMessageTimes = list()
        self.warningTime = 0.001
        self.numberOfBytesToRead = 1024
        self.messageNumber = 0
        self.conn = None
        self.connected = False
        self.reconnectTime = 2


    def subscribe(self, connection=None):
        while True:
            if connection is None and self.conn is None and not self.connected:
                self.conn = socket.socket()
                try:
                    self.conn.connect((self.host, self.port))
                    self.connected = True
                except ConnectionRefusedError:
                    print("connection destroyed, sleeping")
                    sleep(self.reconnectTime)
                    self.connected = False
                    break
            elif self.conn is None:
                self.conn = connection
                self.connected = True
            try:
                if self.conn is None:
                    break
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
                    if(len(self.lastMessageTimes) > 10):
                        if(time() - self.lastMessageTimes[0] < self.warningTime):
                            self.conn = None
                            raise ClientDisconnectedException()
                        self.lastMessageTimes.pop(0)

                    self.useValue(self.decodeValue(data))
            except ClientDisconnectedException:
                if self.conn is not None:
                    self.conn.close
                self.connected = False
                self.conn = None 
                print("connection destroyed, sleeping")
                sleep(self.reconnectTime)
                break
            print("reconnection attempt")
            
    def setConnection(self, connection):
        self.conn = connection

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
        print("{0} {1}".format(self.messageNumber,self.decodeValue(value)))

if __name__ == "__main__":
    sc = SimpleClient(host1=socket.gethostname())
    sc.subscribe()
