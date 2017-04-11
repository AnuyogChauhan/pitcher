
import socket
import sys
from time import sleep
from time import time

class SimpleBroadcast(object):
    def __init__(self, host1='localhost', port1=5004, is_process1=False):
        self.host = host1
        self.port = port1
        self.conn = None
        
    def connect(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.connect((self.host, self.port))

    def encodeValue(self,value):
        valueToSend = b''
        
        if type(value) is bytes:
            valueToSend = value
        elif type(value) is str:
            valueToSend = value.encode('utf-8')
        elif type(value) is int:
            valueToSend = '{0}'.format(value).encode('utf-8')
            
        return valueToSend

    def broadcast(self,value,connection=None):
        valueToSend = self.encodeValue(value)

        # this method is for testing
        if connection is None and self.conn is None:
            s = socket.socket()
            s.connect((self.host, self.port))
            s.sendall(valueToSend)
            s.close
        # this method should be used most
        elif self.conn is not None:
            try:
              self.conn.sendall(valueToSend)
            except socket.error:
              print("problem sending!!!!")
        elif connection != None:
            connection.send(valueToSend)
                        
    def setConnection(self, connection):
        self.conn = connection
        
    def close(self):
        if self.conn is not None:
            self.conn.close


import uuid
        
if __name__ == "__main__":
    sb = SimpleBroadcast(host1=socket.gethostname(),is_process1=False)
    start = time()
    sendingTime = 0.0
    for a in range(0,20):
      current = time()
      sb.broadcast(str(uuid.uuid4()))
      sleep(0.01)
      sendingTime += time() - current
    print("total sending time {0}".format(sendingTime))
    print("total time: {0}".format(time()-start))
    sb.close()
    
    
