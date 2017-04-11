
import sys
import socket
from lib.SimpleClient import SimpleClient
from CarClient import CarClient
from CarPacket import CarPacket
from ens import ensclient


class CarClientENS(CarClient):
    def __init__(self, host2='localhost', port2=5000):
        super(CarClientENS, self).__init__(host2, port2)
        self.identifier = "ashish.catcher01"
        #self.identifier = "ashish.car-network-catcher01"
        self.network = "micro-car-network.test-network"
        self.numberOfBytesToRead = CarPacket.size()
        self.session = None
        self.my_ens_client = None

    def findEndpoints(self):
        self.my_ens_client = ensclient.ENSClient(self.identifier)
        if self.my_ens_client.init():
            self.session = self.my_ens_client.connect(self.network)
            if self.session:
                self.setConnection(self.session.conn)
                self.endpoint = ensclient.ENSEndpoint(self.session.binding["endpoint"])
                print("host {0} port {1}".format(self.endpoint.host, self.endpoint.port))
            else:
                print("failed to connect to ar-network")

        else:
            print("failed to initialize")
            sys.exit(1)

    def close(self):
        if self.my_ens_client is not None:
            self.my_ens_client.close()



if __name__ == "__main__":
    sc = CarClientENS()
    sc.findEndpoints()
    sc.subscribe()
