
import sys
import os
import optparse
import logging

from lib.SimpleServer import SimpleServer
from lib.BroadcastRecipient import BroadcastRecipient
from CarPacket import CarPacket
from CarRecipient import CarRecipient
from CarServer import CarServer


logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')

class CarServerENS(CarServer):
    def __init__(self, port3=5002):
        super(CarServerENS, self).__init__(port2=port3)
        self.port = port3
        self.packetSize = CarPacket.size()



if __name__ == "__main__":
    print "starting server"
    parser = optparse.OptionParser(
            formatter=optparse.TitledHelpFormatter(),
            usage=globals()['__doc__'],
            version='$Id: py.tpl 332 2008-10-21 22:24:52Z root $')

    parser.add_option ('-v', '--verbose', action='store_true',default=False, help='verbose output')
    (options, args) = parser.parse_args()
    port = 5000
    if(len(args) > 0):
        port = int(args[0])
    server = CarServerENS(port)
    server.serve()
