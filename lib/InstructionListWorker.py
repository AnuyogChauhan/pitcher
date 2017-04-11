
import threading
from time import sleep
import time
import sys
import logging
import multiprocessing
from multiprocessing import Value
from multiprocessing import Manager

logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)-15s %(levelname)-8s %(filename)-16s %(lineno)4d %(message)s')

class Instruction(object):
    def __init__(self, instructionObject):
        self.todo = instructionObject
        self.finished = False
        self.errored = False
        self.timeoutSeconds = 1

    def run(self, returnValue):
        logging.debug("todo object "+str(self.todo))
        logging.debug("starting instruction")
        sleep(2)
        logging.debug("finished instruction")
        self.finished = True
        returnValue.value = True
        return self.finished

    def finished(self):
        return self.finished and not self.errored




class InstructionListWorker(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        threading.Thread.__init__(self)
        self._stopper = threading.Event()
        self.instructions = dict()
        self.instructions['default'] = list()
        self.noInstructionSleep = 0.1
        self.returnValue = Value('b', False)

    def run(self):
        while True and not self.stopped():
            instructionsRun = 0
            #logging.debug("in run loop")
            for k in self.instructions.keys():
                hasInstructions = len(self.instructions[k])
                if hasInstructions > 0:
                    logging.debug("found instructions")
                    self.returnValue = Value('b', False)
                    p = multiprocessing.Process(target=self.instructions[k][0].run, args=(self.returnValue,))
                    p.start()
                    logging.debug(time.time())
                    p.join(self.instructions[k][0].timeoutSeconds)
                    logging.debug(self.returnValue.value)
                    if self.returnValue.value is 1:
                        instructionsRun = instructionsRun + 1
                        p.terminate()
                        self.instructions[k].pop(0)
                    else:
                        logging.warning("terminated a timeout")
                        p.terminate()
                        self.instructions[k].pop(0)

            if instructionsRun == 0:
                sleep(self.noInstructionSleep)

    def stop(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.isSet()

    def addInstruction(self, i, listname=None):
        if listname is None:
            self.instructions['default'].append(i)
        else:
            self.instructions[listname].append(i)
        return True

    def remaining(self):
        remainingItems = 0
        for k in self.instructions.keys():
            remainingItems += len(self.instructions[k])

        return remainingItems

    def finished(self):
        return self.remaining() == 0


if __name__ == "__main__":
    ilw = InstructionListWorker()
    ilw.start()
    for i in range(0, 10):
        ilw.addInstruction(Instruction(i))
    
    try:
      while True:
          if(ilw.finished()):
              ilw.stop()
              sys.exit(0)
    except KeyboardInterrupt:
      ilw.stop()
      sys.exit(0)
