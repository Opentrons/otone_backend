from file_io import FileIO

debug = False


#converted from js dict in Planner.js into a python class
class TheQueue:
    """TheQueue class-converted from js dict in Planner.js into a python class
    
    class to hold the array of groups contained in a protocol instruction
    and process them iteratively.
    
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
        
    The theQueue object holds the groups contained in the instruction in a
        FIFO array called qlist.  When a '{stat:0}' is received from the 
        smoothieAPI object, theQueue pops off the next group in qlist, passing 
        the command to the smoothieAPI.
    """
    # 'theQueue' keeps an array of all coordinate messages meant for 'smoothie.js'
    # and places them in a first-in-first-out array
    # when a '{stat:0}' is recieved from 'smoothie.js', theQueue increments to the next in line
    
#Special Methods
    def __init__(self, head, global_handlers):
        """initialize TheQueue object
        
        """
        if debug == True: FileIO.log('the_queue.__init__ called')
        self.head = head
        self.paused = False
        self.is_busy = False
        self.current_command = None    #note: could be a function or string?
        self.just_started = False
        self.ghand = global_handlers
        self.qlist = list()

        
    def __str__(self):
        return "TheQueue"
        
        
#local functions-----------------------
    # this is called when the smoothieboard has successfully received a messages
    # but not yet completed the command
    def sent_successfully(self):
        if debug == True: FileIO.log('the_queue.send_successfully called')
        if self.just_started and self.ghand.onStart and type(self.ghand.onStart) == 'function':
            self.ghand.onStart()

#Fields            
    
    
#Methods
    def pause(self):
        if debug == True: FileIO.log('the_queue.pause called')
        if len(self.qlist):
            self.paused = True
            
    def resume(self):
        if debug == True: FileIO.log('the_queue.resume called')
        self.paused = False
        self.step(False)
        
    def add(self,commands):
        if debug == True: FileIO.log('the_queue.add called,\ncommands:\n',commands,'\n')
        if commands and self.paused==False:
            # test to see if the queue is currently empty
#            self.just_started = False   #is this needed?
            if len(self.qlist)==0:
                self.just_started = True
                if debug == True: FileIO.log('the_queue.add:\n\tbefore self.qlist: ',self.qlist,'\n')
            # add new commands to the end of the queue
            FileIO.log('type(commands): '+str(type(commands)))
            if isinstance(commands, list):
                self.qlist.extend(commands)
            elif isinstance(commands, dict):
                self.qlist.append(commands)
            if debug == True: FileIO.log('the_queue.add:\n\tafter self.qlist: ',self.qlist,'\n')
    
            self.step(self.just_started) # attempt to increment the queue

    def step(self,just_started):
        if debug == True: FileIO.log('the_queue.step called,\njust_started: ',just_started,'\n')
        if self.is_busy==False:
            if debug == True: FileIO.log('\tthe_queue len(self.qlist): ',len(self.qlist))
            if len(self.qlist)>0:
                # pull out the first in line from the queue
#                self.current_command = self.qlist.splice(0,1)[0];
                self.current_command = self.qlist.pop(0)
                self.is_busy = True;
                if debug == True: FileIO.log('\n\n\tthe_queue.current_command:\n\n',self.current_command,'\n')

                # 'wait' for someone to click a button on interface. Not there yet.
                if 'wait' in self.current_command:
#                    self.smoothieAPI.wait(self.current_command.wait, self.sent_successfully);  # WAIT
                    self.head.smoothieAPI.wait(self.current_command['wait'], self.sent_successfully)  # WAIT
                
                elif 'delay' in self.current_command:
                    self.head.smoothieAPI.delay(self.current_command['delay'])#, self.sent_successfully)

                elif 'home' in self.current_command:
#                    self.smoothieAPI.home(self.current_command.home, self.sent_successfully);  # HOME
                    self.head.smoothieAPI.home(self.current_command['home'])#, self.sent_successfully)  # HOME
                elif 'speed' in self.current_command:
                    self.head.smoothieAPI.set_speed(self.current_command['axis'],self.current_command['speed'])
                else:
#                    self.smoothieAPI.move(self.current_command, self.sent_successfully );      # MOVE
                    self.head.smoothieAPI.move(self.current_command)	#, self.sent_successfully );      # MOVE

            else:
                if self.ghand.onFinish and hasattr(self.ghand.onFinish,'__call__'):
                    self.ghand.onFinish()
                    
    def clear(self):
        if debug == True: FileIO.log('the_queue.clear called')
        self.qlist = list()
        self.is_busy = False
        self.paused = False
        self.current_command = None   #note: could be a function or string?
        
        
    #from planner.js
    def pause_job(self):
        """
        
        """
        if debug == True: FileIO.log('the_queue.pause_job called')
        #doesn't map to smoothieAPI
        #function pauseJob()
        self.pause()
        
    #from planner.js
    def resume_job(self):
        """
        
        """
        if debug == True: FileIO.log('the_queue.resume_job called')
        #doesn't map to smoothieAPI
        #function resumeJob()
        self.resume()
    
    #from planner.js
    def erase_job(self, data):
        """
        
        """
        if debug == True: FileIO.log('the_queue.erase_job called')
        #doesn't map to smoothieAPI
        #function eraseJob(){
        self.clear() 
        
        
    #new to eliminate theQueue ref in head
    def kill(self):
        """
        
        """
        if debug == True: FileIO.log('the_queue.kill called')
        self.head.kill()
        self.clear()

    #new to eliminate theQueue ref in head
    def reset(self):
        """
        
        """
        if debug == True: FileIO.log('the_queue.reset called')
        self.head.reset()
        self.clear()  
        
