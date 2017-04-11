

from InstructionListWorker import InstructionListWorker
from InstructionListWorker import Instruction
from Logger import Logger
import logging
import sys

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)-15s %(levelname)-8s %(filename)-16s $(lineno)4d %(message)s")

class LoggingEvent(Instruction):
    def __init__(self, instructionObject):
        self.todo = instructionObject
        self.logger = Logger()
        self.finished = False
        self.errored = False
        self.timeoutSeconds = 1
        logging.debug("initialized! ")

    def run(self, returnValue):
        logging.debug("run! "+str(self.todo))
        if len(self.todo.keys()) > 0:
            if len(self.todo.keys()) == 1 and 'tag' in self.todo.keys():
                self.logger.log(self.todo['tag'])
            else:
                tag1 = 'default'
                if 'tag' in self.todo.keys():
                    tag1 = self.todo['tag']
                    del self.todo['tag']
                
                self.logger.log(tag=tag1, blob=self.todo)
        returnValue.value = True
        self.finished = True
        return self.finished




class BackgroundLogging(InstructionListWorker):
    def __init__(self, *args, **kwargs):
        super(BackgroundLogging, self).__init__(*args, **kwargs)
        self.noInstructionSleep = 1.0
        self.timeoutSeconds = 2

    def addLog(self, logevent):
        data = dict()
        data['tag'] = 'No Tag'
        if type(logevent) is str:
            data['tag'] = logevent
        elif type(logevent) is dict:
            data = logevent

        self.instructions['default'].append(LoggingEvent(data))
            

if __name__ == "__main__":
    bgl = BackgroundLogging()
    bgl.start()

    for i in range(0, 10):
        bgl.addLog('hello')

    try:
        while True:
            if bgl.finished():
                bgl.stop()
                sys.exit(0)
    except KeyboardInterrupt:
        bgl.stop()
        sys.exit(0)
