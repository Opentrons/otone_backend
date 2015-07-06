from file_io import FileIO
import json, collections, asyncio

debug = False

class InstructionQueue:
    """InstructionQueue class
    
    class to hold protocol instructions and start a job.
    
    The robot_protocol file is an array of instructions.  
    
    An instruction is an array of groups + a specified tool which executes 
        the group.
        
    A group can be defined as the lifecycle of a tip.  Each group holds
        a single command.
        
    A command is one of the following:
        Transfer; Consolodate; Distribute; Mix
        
    The instructionQueue iteratively selects an instruction in the
        robot_protocol array and passes it to theQueue object along with the
        specified tool(pipette).  The theQueue object iteratively processes 
        the groups in the instruction until theQueue is empty, which triggers
        the InstructionQueue to select the next instruction.  All protocol
        processing stops when the instructionQueue is empty.
        
    """
#Special Methods
    def __init__(self, head, global_handlers):
        """initialize Instruction Queue object
        
        """
        if debug == True: FileIO.log('instruction_queue.__init__ called')
        self.head = head
        self.isRunning = False
        self.infinity_data = None
        self.ghand = global_handlers
        
    def __str__(self):
        return "InstructionQueue"
        
#attributes
    instructionArray = []

        
#Methods
    def start_job(self, instructions, should_home):
        """method to start the ProtocolRunner job
        
        """
        if debug == True: FileIO.log('instruction_queue.start_job called,\ninstructions:\n\n',instructions,'\n')
        if instructions and len(instructions):
            self.head.erase_job()
            self.instructionArray = instructions
            if debug == True: FileIO.log('instruction_queue:\n\tnew instructions:\n\n',self.instructionArray,'\n')

            if self.infinity_data is None or should_home == True:
                self.head.home({'x':True,'y':True,'z':True,'a':True,'b':True})
                self.isRunning = True

                def set_xyz_speed_to_3000():
                    if debug == True: FileIO.log('set_xyz_speed_to_3000 called')
                    self.head.set_speed('xyz',3000)

                loopy = asyncio.get_event_loop()
                loopy.call_later(2, set_xyz_speed_to_3000)

            else:
                self.ins_step()  #changed name to distinguish from theQueue step function
    
    def start_infinity_job(self, infinity_instructions):
        if debug == True: FileIO.log('instruction_queue.start_infinity_job called')
        if infinity_instructions and len(infinity_instructions):
            self.infinity_data = json.dumps(infinity_instructions,sort_keys=True,indent=4,separators=(',',': '))
            self.start_job(infinity_instructions, True)

    def erase_job(self):
        """method to eraser the ProtocolRunner job
        
        """
        if debug == True: FileIO.log('instruction_queue.erase_job called')
        self.head.erase_job()
        self.isRunning = False;
        self.instructionArray = []
        
#    def step(self)  #changed name to distinguish from theQueue step function
    def ins_step(self):
        """method to increment to the next step in the ProtocolRunner job
        
        """
        if debug == True:
            FileIO.log('instruction_queue.ins_step called,\nlen(self.instructionArray): ',len(self.instructionArray),'\n')
            FileIO.log('instruction_queue self.instructionArray:\n\n',self.instructionArray,'\n')
        if len(self.instructionArray)>0:
            #pop the first item in the instructionArray list
            #this_instruction = self.instructionArray.splice(0,1)[0]
            this_instruction = self.instructionArray.pop(0)
            if this_instruction and this_instruction['tool'] == 'pipette':
                self.send_instruction(this_instruction)
        elif self.isRunning == True:
            if self.infinity_data is not None:
                if debug == True: FileIO.log('ins_step self.infinity_data: ********************************\n\n',self.infinity_data,'\n')
                self.start_job(json.loads(self.infinity_data, object_pairs_hook=collections.OrderedDict),False)
            else:
                self.erase_job()
                self.head.home({'x':True,'y':True,'z':True,'a':True,'b':True})
                self.ghand.finished()

  
    def send_instruction(self,instruction):
        """method to execute a step (pipette call) in the ProtocolRunner job
        
        """
        if debug == True: FileIO.log('instruction_queue.send_instruction called,\n\tinstruction:\n\n', \
            json.dumps(instruction,sort_keys=True,indent=4,separators=(',',': ')),'\n')
        if 'groups' in instruction and len(instruction['groups']):
            for m in instruction['groups']:
                this_group = m
                if this_group['command'] == 'pipette':
                    self.head.pipette(this_group)
                    
