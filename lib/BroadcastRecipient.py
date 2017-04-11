
import socket
import logging


logging.basicConfig(level=logging.INFO,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')

class BroadcastRecipient:
    def __init__(self, socket1=None, address1=None):
        self.s = socket1
        self.address = address1
        self.connected = True

    def processBeforePublish(self, instruction):
        return instruction

    def publish(self, instruction):
        instructionToSend = self.processBeforePublish(instruction)
        if self.connected:
            try:
                if type(instructionToSend) is bytes:
                    self.s.sendall(instructionToSend)
                elif type(instructionToSend) is str:
                    self.s.sendall(instructionToSend.encode('utf-8'))
                elif type(instructionToSend) is dict:
                    for k in instructionToSend.keys():
                        logging.info("key: {0} value: {1}".format(k,instructionToSend[k]))
                else:
                    logging.error("unknown instruction type {0}".format(instruction))
            except socket.error:
                self.connected = False
                self.close()
                logging.info("became disconnected")
            except Exception:
                self.connected = False
                self.close()
                logging.info("became disconnected")

    def close(self):
        try:
            self.s.shutdown(socket.SHUT_WR)
        except socket.error:
            self.connected = False
            logging.info("socket closed")
        except OSError:
            logging.info("socket closed")


