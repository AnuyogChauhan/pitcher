
import logging
import socket
import time
import threading
import sys
import liblo
from SimpleClient import SimpleClient

logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')


class LatencyMindedClient(SimpleClient):
    def __init__(self, host2, port2, oscHost, oscPort, oscEndpoint1='/latency'):
        super(LatencyMindedClient, self).__init__(host2, port2)
        self.toAddress = liblo.Address(oscHost, oscPort)
        self.oscEndpoint = oscEndpoint1
        self.timestamps = dict()

    def sendLatency(self, latency, edge):
        liblo.send(self.toAddress, self.oscEndpoint, latency, edge)

    def useValue(self, value):
        logging.debug("got value! {1}  {0}".format(value, self.messageNumber))
        try:
            message_id = value.message_id
            if message_id in self.timestamps.keys():
                millis = int(round(time.time() * 1000)) - LatencyMinder.shiftMillis()
                latency = millis - self.timestamps[message_id]
                self.sendLatency(latency, value.edge)
        except AttributeError:
            logging.error("no message_id or edge attribute")
            logging.error(value)
            pass


class LatencyMinder(object):
    def __init__(self, client, edge_client, latencyListenerHost, latencyListenerPort, endpoint1='/launchtime'):
        self.client = client
        self.edge_client = edge_client
        try:
            self.edge_client.findEndpoints()
        except Exception:
            logging.error("problem finding endpoints for edge client")
            sys.exit(0)

        self.host = latencyListenerHost
        self.port = latencyListenerPort
        self.clientRunnerThread = None
        self.endpoint = endpoint1
        self.osc_server = liblo.Server(self.port)
        self.osc_server.add_method(endpoint1, 'iib', self.launchTime)

    def launchTime(self, path, args):
        message_id, launch_time, edge = args
        logging.debug("message id: {0} launched at {1}, edge {2}".format(message_id, launch_time, edge))
        if edge:
            self.edge_client.timestamps[message_id] = launch_time
        elif not edge:
            self.client.timestamps[message_id] = launch_time
    
    def run(self):
        clientRunnerThread = threading.Thread(target=self.client.subscribe)
        clientRunnerThread.start()
        edgeClientRunnerThread = threading.Thread(target=self.edge_client.subscribe)
        edgeClientRunnerThread.start()
        try:
            while True:
                self.osc_server.recv(10)
        except Exception:
            clientRunnerThread.stop()
            edgeClientRunnerThread.stop()
            sys.exit(0)

    @staticmethod
    def shiftMillis():
        return 1490000000000

if __name__ == "__main__":
    client = LatencyMindedClient(socket.gethostname(), 5004, oscHost='127.0.0.1', oscPort=7003)
    edge_client = LatencyMindedClient(socket.gethostname(), 5004, oscHost='127.0.0.1', oscPort=7003)
    latencyMinder = LatencyMinder(client, edge_client, '127.0.0.1', 7001)
    latencyMinder.run()


