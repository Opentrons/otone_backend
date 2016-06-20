import json

from file_io import FileIO


debug = True
verbose = False

class Publisher:
    """Publisher to centralize publishing data and callbacks
    
    later maybe replaced with WAMP
    """


#Special Methods
    def __init__(self, session):
        """Initialize Publisher object
        
        """
        if debug == True: FileIO.log('publisher.__init__ called')
        self.head = None
        self.runner = None
        self.caller = session


    def __str__(self):
        return "Publisher"


    def set_head(self, head):
        """Set the Publisher's Head
        """
        if debug == True: FileIO.log('publisher.set_head called')
        self.head = head


    def set_runner(self, runner):
        """Set the Publisher's ProtocolRunner
        """
        if debug == True: FileIO.log('publisher.set_runner called')
        self.runner = runner


#Handlers
    def on_smoothie_connect(self):
        """Publish that Smoothieboard is connected
        """
        if debug == True: FileIO.log('publisher.on_smoothie_connect called')
        self.send_message('status',{'string':'Connected to the Smoothieboard','color':'green'})
        #msg = {
        #    'type': 'status',
        #    'data':{'string':'Connected to the Smoothieboard','color':'green'}
        #}
        #self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))

    def on_smoothie_disconnect(self):
        """Publish that Smoothieboard is disconnected and try to reconnect
        """
        if debug == True: FileIO.log('publisher.on_smoothie_disconnect called')
        self.send_message('status',{'string':'Smoothieboard Disconnected','color':'red'})
        #msg = {
        #    'type': 'status',
        #    'data':{'string':'Smoothieboard Disconnected','color':'red'}
        #}
        #self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        #try to reconnect
        self.head.smoothieAPI.connect()#self.onSmoothieConnect, self.onSmoothieDisconnect)
        
#Event handlers-----------------
    #originally in app.js
    
    def on_start(self):  #called from planner/theQueue
        """Publish that theQueue started a command
        """
        if debug == True: FileIO.log('publisher.on_start called')
        self.send_message('status',{'string':'Robot is moving','color':'orange'})
        #msg = {
        #    'type': 'status',
        #    'data':{'string':'Robot is moving','color':'orange'}
        #}
        #self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))


    def on_raw_data(self,string):     #called from smoothie/createSerialConnection
        """
        Publish raw data from Smoothieboard
        """
        if debug == True and verbose == True: FileIO.log('publisher.on_raw_data called')
        self.send_message('smoothie',{'string':string})
        #msg = {
        #    'type': 'smoothie',
        #    'data':{'string':string}
        #}
        #try:
        #    self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        #except:
        #    FileIO.log("error trying to publish in onRawData")


    def on_position_data(self,string):
        """
        Publish position data from Smoothieboard
        """
        if debug == True and verbose == True: FileIO.log('publisher.on_position_data called')
        self.send_message('position',{'string':string})


    def on_limit_hit(self,axis):
        """Publish that a limit switch was hit
        """
        if debug == True: FileIO.log('publisher.on_limit_hit called')
        self.send_message('limit',axis)
        #msg = {
        #    'type': 'limit',
        #    'data': axis
        #}
        #try:
        #    self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        #except:
        #    FileIO.log("error trying to publish in onRawData")
        
    def on_finish(self):     #called from planner/theQueue
        """Publish status and move on to next instruction step
        """
        if debug == True: FileIO.log('publisher.on_finish called')
        self.send_message('status',{'string':'Robot stopped','color':'black'})
        #msg = {
        #    'type': 'status',
        #    'data':{'string':'Robot stopped','color':'black'}
        #}
        #self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        try:
            self.runner.insQueue.ins_step() #changed name 
        except AttributeError as ae:
            print(ae)


    def show_delay(self, time_left):
        self.send_message('delay',time_left)


#OTHER DATA NEEDING TO GO BACK TO UI
    def finished(self):
        """Publish that instruction queue finished
        """
        if debug == True: FileIO.log('publisher.finished called')
        self.send_message('finished',None)
        #msg = {
        #    'type':'finished'
        #}
        #self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))

    def send_message(self,type_,damsg):
        """Send a message
        """
        if debug == True and verbose == True: FileIO.log('publisher.send_message called')
        if damsg is not None:
            msg = {
                'type':type_,
                'data':damsg
            }
        else:
            msg = {
                'type':type_
            }
        try:
            self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        except:
            FileIO.log("error trying to send_message")


    def send_ctrl_message(self,type_,damsg):
        """Send a Control Message (Similar to Control Transfer in USB), not implemented yet
        """
        if debug == True: FileIO.log('publisher.send_ctrl_message called')
        if damsg is not None:
            msg = {
                'type':type_,
                'data':damsg
            }
        else:
            msg = {
                'type':type_
            }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser_ctrl',json.dumps(msg))

