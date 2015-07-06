from instruction_queue import InstructionQueue
from file_io import FileIO

debug = False

class ProtocolRunner:
    """ProtocolRunner class to run and manager the running job
    """
    
    def __init__(self, head, global_handlers):
        """initialize ProtocolRunner object
        
        """
        if debug == True: FileIO.log('protocol_runner.__init__ called')
        #intantiate the two queue objects
        self.insQueue = InstructionQueue(head, global_handlers)
        
        
    def __str__(self):
        return "ProtocolRunner"
        
    
