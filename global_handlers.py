from file_io import FileIO
import json

debug = False

class GlobalHandlers:
    """Class GlobalHandlers to centralize event handlers using global objects
    
    later maybe replaced with WAMP
    """
    
#Special Methods
    def __init__(self, session):
        """initialize FileIO object
        
        """
        if debug == True: FileIO.log('global_handlers.__init__ called')
        self.head = None
        self.runner = None
        self.caller = session
        
    def __str__(self):
        return "GlobalHandlers"

    def setHead(self, head):
        if debug == True: FileIO.log('global_handlers.setHead called')
        self.head = head

    def setRunner(self, runner):
        if debug == True: FileIO.log('global_handlers.setRunner called')
        self.runner = runner
        
#Handlers
    def onSmoothieConnect(self):
        if debug == True: FileIO.log('global_handlers.onSmoothieConnect called')
        msg = {
            'type': 'status',
            'data':{'string':'Connected to the Smoothieboard','color':'green'}
        }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))

    def onSmoothieDisconnect(self):
        if debug == True: FileIO.log('global_handlers.onSmoothieDisconnect called')
        msg = {
            'type': 'status',
            'data':{'string':'Smoothieboard Disconnected','color':'red'}
        }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        #try to reconnect
        self.head.smoothieAPI.connect()#self.onSmoothieConnect, self.onSmoothieDisconnect)
        
#Event handlers-----------------
    #originally in app.js
    
    def onStart(self):  #called from planner/theQueue
        if debug == True: FileIO.log('global_handlers.onStart called')
        msg = {
            'type': 'status',
            'data':{'string':'Robot is moving','color':'orange'}
        }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        
    def onRawData(self,string):     #called from smoothie/createSerialConnection
        if debug == True: FileIO.log('global_handlers.onRawData called')
        msg = {
            'type': 'smoothie',
            'data':{'string':string}
        }
        try:
            self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        except:
            FileIO.log("error trying to publish in onRawData")

    def onLimitHit(self,axis):
        if debug == True: FileIO.log('global_handlers.onLimitHit called')
        msg = {
            'type': 'limit',
            'data': axis
        }
        try:
            self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        except:
            FileIO.log("error trying to publish in onRawData")
        
    def onFinish(self):     #called from planner/theQueue
        if debug == True: FileIO.log('global_handlers.onFinish called')
        msg = {
            'type': 'status',
            'data':{'string':'Robot stopped','color':'black'}
        }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))
        self.runner.insQueue.ins_step() #changed name 


#OTHER DATA NEEDING TO GO BACK TO UI
    def finished(self):
        if debug == True: FileIO.log('global_handlers.finished called')
        msg = {
            'type':'finished'
        }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))

    def sendMessage(self,type_,damsg):
        if debug == True: FileIO.log('global_handlers.sendMessage called')
        if damsg is not None:
            msg = {
                'type':type_,
                'data':damsg
            }
        else:
            msg = {
                'type':type_
            }
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg))

    def sendCtrlMessage(self,type_,damsg):
        if debug == True: FileIO.log('global_handlers.sendCtrlMessage called')
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

