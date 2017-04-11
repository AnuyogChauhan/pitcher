
import socket
try:
    import redis
except ImportError:
    print("redis not available, not imported") 
import logging
import threading
import sys
from random import randint
from BroadcastRecipient import BroadcastRecipient
from time import sleep

logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')

debug = False 

class Listener(threading.Thread):
    def __init__(self, hostname, port1, channel):
        threading.Thread.__init__(self)
        self.redis = redis.StrictRedis(host=hostname, port=port1, db=0)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe(channel)
        self.clients = list()
    
    def addClient(self, client):
        logging.info("added client to redis listener")
        self.clients.append(client)
    
    def work(self, message):
        sent = False
        if type(message) is dict:
            try:
                toPublish = message['data']
                for client in self.clients:
                    client.publish(toPublish)
                sent = True
            except KeyError:
                logging.debug("no data element")

        if sent is False:
            logging.error("message contents: {0}".format(message))
    
    def run(self):
        for item in self.pubsub.listen():
            logging.info("item caught {0}".format(item))
            self.work(item)


class SimpleServer(object):
    def __init__(self, port1=50041):
        self.s = socket.socket()
        self.host = socket.gethostname()
        self.port = port1
        self.clients = list()
        self.watchKey = None
        self.redisConnection = None
        self.useRedis = False
        self.listener = None
        self.packetSize = 1024
        self.pretendSleepTime = 30000  # 30 ms
        self.pretendSleepVariance = 2000  # 2ms
        self.pretendToSleep = False 

    def initRedis(self, hostname, watch, port1=6379):
        self.useRedis = True
        self.redisConnection = redis.StrictRedis(host=hostname, port=port1, db=0)
        self.watchKey = watch
        self.listener = Listener(hostname, port1, watch)
        self.listener.start()

    def addClient(self, connection, address1 ):
        if self.listener is None:
            if debug:
                logging.info("client added to client list")
                logging.info(connection.getpeername())
                logging.info(connection.getsockname())
            self.clients.append(BroadcastRecipient(connection, address1))
        if self.listener is not None:
            if debug:
                logging.info("client added to listener")
            self.listener.addClient(BroadcastRecipient(connection, address1))

    def clientsDisconnected(self):
        anyDisconnected = False
        for c in self.clients:
            anyDisconnected = anyDisconnected or not c.connected
        return anyDisconnected

    def fromBytesToString(self, value):
        return value.decode('utf-8')

    def pruneClientList(self):
        while self.clientsDisconnected():
            count = 0
            disconnected = None
            for c in self.clients:
                if c.connected is False:
                    disconnected = count
                count = count + 1

            if disconnected is not None:
                del self.clients[disconnected]

    def serve(self):
        self.s.bind((self.host, self.port))
        try:
            while True:
                self.s.listen(1)
                c, addr = self.s.accept()
                CLIENT_AS_BYTES = "CLIENT".encode('utf-8')
                data = c.recv(self.packetSize)

                if not data: break
                if debug:
                    print("got message {0}".format(data))
                if not data == CLIENT_AS_BYTES:
                    if(not self.useRedis):
                        self.pruneClientList()

                        if self.pretendToSleep is True:
                            variance = randint(-1 * self.pretendSleepVariance, self.pretendSleepVariance)
                            tosleep = (float(self.pretendSleepTime) + float(variance))/1000
                            logging.info(tosleep)
                            sleep(tosleep / 1000.0)
                        
                        for client in self.clients:
                            if debug:
                                print("publishing to client {0}".format(client))
                            client.publish(data)
                    elif(self.watchKey):
                        #logging.info("publishing {0} to key {1} via redis {2}".format(instruction,self.watchKey,self.redisConnection))
                        if type(data) is bytes:
                            data = self.fromBytesToString(data)
                        self.redisConnection.publish(self.watchKey, data)

                if data == CLIENT_AS_BYTES:
                    self.addClient(c, addr)
                       
        except KeyboardInterrupt:
            for client in self.clients:
                client.s.close()
            logging.info("exiting")
            self.s.close()
            
    def close(self):
        for client in self.clients:
            client.close()
        logging.info("exiting")
        self.s.close()
        sys.exit(0)

if __name__ == "__main__":
    logging.info("starting server")
    s = SimpleServer(5004)
    try:
      s.serve()
    except KeyboardInterrupt:
      s.close()
      
