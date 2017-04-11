import struct
from random import randint
from parse import parse
import logging

logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')

class WrongSizeException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)


class CarPacket(object):
    def __init__(self, value1, speed1, dist1, message_id1, edge1, version1=0):
        self.analog = int(value1)
        self.speed = int(speed1)
        self.distance = int(dist1)
        self.message_id = int(message_id1)
        self.edge = bool(edge1)
        self.version = int(version1)

    def asBytes(self):
        analog_bytes = struct.pack(">I", self.analog)
        edge_byte = struct.pack(">B", self.edge)
        
        try:
            speed_bytes = struct.pack(">I", self.speed)
        except Exception:
            speed_bytes = struct.pack(">I", 0)
            
        distance_bytes = struct.pack(">I", self.distance)
        
        message_bytes = struct.pack(">I", self.message_id)
        
        version_byte = struct.pack(">B", self.version)
        all_bytes = analog_bytes
        all_bytes += speed_bytes
        all_bytes += distance_bytes
        all_bytes += message_bytes
        all_bytes += edge_byte
        all_bytes += version_byte
        return all_bytes

    def simpleString(self):
        fmtstring = CarPacket.format_string()
        return fmtstring.format(self.analog, self.speed, self.distance, self.message_id, self.edge, self.version)

    def toString(self):
        return "[CarPacket] value: {0}, message_id: {1}, edge: {2}, speed: {3}, distance: {4}, v {5}".format(self.analog,
                                                                self.message_id,
                                                                self.edge,
                                                                self.speed,
                                                                self.distance,
                                                                self.version)

    @staticmethod
    def size():
        a = CarPacket(10, 10, 10, 10, True)
        return len(a.asBytes())

    @staticmethod
    def format_string():
        return "{0}:{1}:{2}:{3}:{4}:{5}"

    @staticmethod
    def fromBytes(value):
        cps = CarPacket.size()

        if len(value) != cps and len(value) % cps != 0:
            raise WrongSizeException()

        if len(value) > cps and len(value) % cps == 0:
            value = value[0:cps-1]

        analog = struct.unpack(">I", value[0:4])[0]
        speed = struct.unpack(">I", value[4:8])[0]
        distance = struct.unpack(">I", value[8:12])[0]
        messageid = struct.unpack(">I", value[12:16])[0]
        edge = bool(struct.unpack(">b", value[16:17])[0])
        version = int(struct.unpack(">b", value[17:18])[0])
        return CarPacket(int(analog), int(speed), int(distance), int(messageid), bool(edge), int(version))

    @staticmethod
    def fromSimpleString(value):
        fmtstring = CarPacket.format_string()
        v = parse(fmtstring, value)
        return CarPacket(v[0], v[1], v[2], v[3], v[4], v[5])



if __name__ == "__main__":
    v = 3001
    e = True
    s = randint(0, 100)
    d = randint(0, 100)
    m = randint(0, 100)
    p = CarPacket(v, s, d, m, e)
    print(p.toString())
    p1 = p.asBytes()
    p2 = CarPacket.fromBytes(p1)
    print(p2.toString())
    print("size of packet is {0} bytes".format(CarPacket.size()))
    s1 = p2.simpleString()
    print(s1)
    print(CarPacket.fromSimpleString(s1).toString())




