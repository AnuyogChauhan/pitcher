
import socket
import sys
from lib.SimpleBroadcast import SimpleBroadcast
from CarBroadcast import CarBroadcast
from CarPacket import CarPacket
from ens import ensclient


class CarBroadcastENS(CarBroadcast):
    def __init__(self, host2='localhost', port2=5000):
        super(CarBroadcastENS, self).__init__(host1=host2, port1=port2)
        #self.identifier = "mec.maintenance-car-pitcher"
        self.identifier = "ashish.pitcher01"
        self.network = "micro-car-network.test-network"
        self.session = None


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

    def newsession(self):
        self.session = self.my_ens_client.connect(self.network)
        if self.session:
            self.setConnection(self.session.conn)
            self.endpoint = ensclient.ENSEndpoint(self.session.binding["endpoint"])
            print("host {0} port {1}".format(self.endpoint.host, self.endpoint.port))
        else:
            print("failed to connect to car-network")

    def closeSession(self):
        #self.session.close()
        self.session = None
        self.setConnection(self.session)


    def close(self):
        if self.my_ens_client is not None:
            self.my_ens_client.close()


if __name__ == "__main__":
    sb = CarBroadcastENS()
    sb.findEndpoints()
    sb.broadcast(CarPacket(1, 2, 3, 4, True))
    sb.closeSession()
    sb.newsession()
    sb.broadcast(CarPacket(51, 2, 3, 4, True))
    sb.close()
    
