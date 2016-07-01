from instruction_queue import InstructionQueue

import logging

class ProtocolRunner:
    """Run and manage the running protocol job

    :note: The only thing this object currently does is hold the InstructionQueue (:class:`instruction_queue`) object, but
    it will do more in the future
    """

    def __init__(self, head, publisher):
        """Initialize ProtocolRunner object
        """
        self.ot_logger = logging.getLogger('ot_logger.protocol_runner')
        self.ot_logger.info('protocol_runner.__init__ called')
        #intantiate the two queue objects
        self.insQueue = InstructionQueue(head, publisher)


    def __str__(self):
        return "ProtocolRunner"
        
    
