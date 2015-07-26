import json, collections, subprocess, asyncio
from autobahn.asyncio.wamp import ApplicationSessionFactory
from file_io import FileIO
import script_keeper as sk

debug = True

class Dispatcher():
    """Dispatcher Class
    
    The Dispatcher class is intended to be intantiated into a dispatcher object
    to route commands from the GUI and ProtocolRunner to the appropriate object
    for robot actions.
    The dispatcher object holds references to all the relevant objects such
    as the head, queue objects etc.
    """
    
#Special Methods
    def __init__(self, session,loop):
        """initialize Dispatcher object
        
        """
        if debug == True: FileIO.log('dispatcher.__init__ called')
        self.head = None
        self.runner = None
        self.caller = session
        self.loop = loop
        
    def __str__(self):
        return "Dispatcher"


#instantiate/activate the dispatcher/router dictionary
#create Dispatcher dictionary object which is the equivalent of the
#previous socketHandlers object in js code
    dispatcher = {'home' : lambda self, data: self.home(data),
              'stop' : lambda self, data: self.head.theQueue.kill(data),
              'reset' : lambda self: self.reset(),
              'move' : lambda self, data: self.head.move(data),
              'step' : lambda self, data: self.head.step(data),
              'calibrate' : lambda self, data: self.calibrate(data),  #needs xtra code
              'saveVolume' : lambda self, data: self.head.save_volume(data),
              'movePipette' : lambda self, data: self.move_pipette(data),#needs xtra code
              'movePlunger' : lambda self, data: self.move_plunger(data),
              'speed' : lambda self, data: self.speed(data),          #needs xtra code
              'createDeck' : lambda self, data: self.create_deck(data),#needs xtra code
              'instructions' : lambda self, data: self.instructions(data),#needs xtra code
              'infinity' : lambda self, data: self.infinity(data),
              'pauseJob' : lambda self: self.head.theQueue.pause_job(),
              'resumeJob' : lambda self: self.head.theQueue.resume_job(),
              'eraseJob' : lambda self: self.runner.insQueue.erase_job(),
              'raw' : lambda self, data: self.head.raw(data),
              
              'update' : lambda self, data: self.update(data),

              'wifimode' : lambda self, data: self.wifi_mode(data),
              'wifiscan' : lambda self, data: self.wifi_scan(data),
              'hostname' : lambda self, data: self.change_hostname(data),
              'poweroff' : lambda self: self.poweroff(),
              'reboot' : lambda self: self.reboot(),
              'shareinet': lambda self: self.share_inet()
              }
    def home(self, data):
        if debug == True: FileIO.log('dispatcher.home called')
        self.runner.insQueue.infinity_data = None
        self.runner.insQueue.erase_job()
        self.head.home(data)

    def reset(self):
        if debug == True: FileIO.log('dispatcher.reset called')
        self.runner.insQueue.infinity_data = None
        self.head.theQueue.reset()

    def setHead(self, head):
        if debug == True: FileIO.log('dispatcher.setHead called')
        self.head = head

    def setRunner(self, runner):
        if debug == True: FileIO.log('dispatcher.setRunner called')
        self.runner = runner

    def dispatch_message(self, message):
        if debug == True: FileIO.log('dispatcher.dispatch_message called,\nmessage: ',message,'\n')
        #print('message type: ',type(message))
        try:
            dictum = collections.OrderedDict(json.loads(message.strip(), object_pairs_hook=collections.OrderedDict))
            if debug == True: FileIO.log('\tdictum[type]: ',dictum['type'])
            if 'data' in dictum:
                if debug == True: FileIO.log('\tdictum[data]:\n\n',json.dumps(dictum['data'],sort_keys=True,indent=4,separators=(',',': ')),'\n')
                self.dispatch(dictum['type'],dictum['data'])
            else:
                self.dispatch(dictum['type'],None)
        except:
            if debug == True: FileIO.log('*** error in dispatcher.dispatch_message ***')
            raise

    def dispatch(self, type_, data):
        if debug == True: FileIO.log('dispatcher.dispatch called,\n\n\ttype_: ',type_,'\n\tdata:',data,'\n')
        if data is not None:
            self.dispatcher[type_](self,data)
        else:
            self.dispatcher[type_](self)

          
    def calibrate(self, data):
        if debug == True: FileIO.log('dispatcher.calibrate called,\nargs: ', data,'\n')
        get_calibration = False
        if 'axis' in data and 'property' in data:
            axis = data['axis']
            property_ = data['property']
            self.head.calibrate (axis, property_)
            get_calibration = True
        elif data == '':
            get_calibration = True
        
        if get_calibration == True:
            mssg = {
                'type' : 'containerLocations',
                'data' : self.head.get_deck()
            }
            #print('self.caller.dir()... ',dir(self.caller.session))
            if debug == True: FileIO.log('\tdispatcher.calibrate pre-call...\n\t\tself.caller._myAppSession.publish():\n\t\t\t',json.dumps(mssg,sort_keys=True,indent=4,separators=(',',': ')),'\n')
            self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(mssg,sort_keys=True,indent=4,separators=(',',': ')))
            #self.caller._myAppSession.makeCall(json.dumps(mssg))
            msg2 = {
                'type' : 'pipetteValues',
                'data' : self.head.get_pipette()
            }

            if debug == True: FileIO.log('\tdispatcher.calibrate pre-call...\n\t\tself.caller._myAppSession.publish():\n\t\t\t',json.dumps(msg2,sort_keys=True,indent=4,separators=(',',': ')),'\n')
            self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg2,sort_keys=True,indent=4,separators=(',',': ')))
            #self.caller._myAppSession.makeCall(self.caller.session,msg2)
        
    def move_pipette(self, data):
        if debug == True: FileIO.log('dispatcher.move_pipette called')
        axis = data['axis']
        property_ = data['property']
        self.head.move_pipette(axis, property_)
        
    def move_plunger(self, data):
        if debug == True: FileIO.log('dispatcher.move_plunger called,\ndata:\n\t',data,'\n')
        self.head.move_plunger(data['axis'], data['locations'])
        
    def save_plunger(self, data):
        if debug == True: FileIO.log('dispatcher.save_plunger called')
        self.head.save_plunger(data['axis'], data['location']);
        
    def speed(self, data):
        if debug == True: FileIO.log('dispatcher.speed called,\ndata:\n\t',data,'\n')
        axis = data['axis']
        value = data['value']
        if axis=='ab':
            self.head.set_speed('a', value)
            self.head.set_speed('b', value)
        else:
            self.head.set_speed(axis, value)

    def create_deck(self, data):
        if debug == True: FileIO.log('dispatcher.create_deck called, args: ', data,'\n')
        msg = {
            'type' : 'containerLocations',
            'data' : self.head.create_deck(data)
        }
        if debug == True: FileIO.log('pre-call self.caller._myAppSession.publish() ',json.dumps(msg,sort_keys=True,indent=4,separators=(',',': ')),'\n')
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(msg,sort_keys=True,indent=4,separators=(',',': ')))
        
    def instructions(self, data):
        if debug == True: FileIO.log('dispatcher.instructions called')
        if data and len(data):
            self.runner.insQueue.start_job (data, False)

    def infinity(self, data):
        if debug == True: FileIO.log('dispatcher.infinity called')
        if data and len(data):
            self.runner.insQueue.start_infinity_job (data)

    def wifi_mode(self, data):
        sk.wifi_mode(data)

    def wifi_scan(self, data):
        ws = collections.OrderedDict(sk.wifi_scan(data))
        self.caller._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(ws,sort_keys=True,indent=4,separators=(',',': ')))

    def change_hostname(self, data):
        sk.change_hostname(data)

    def poweroff(self):
        sk.poweroff()

    def reboot(self):
        sk.reboot()

    @asyncio.coroutine
    def update(self, data):
        FileIO.log('dispatcher.update called')
        if data == "all":
            fut = self.loop.create_task(sk.cool_update('data',total=61))
            yield from asyncio.wait_for(fut,10)
            fut = self.loop.create_task(sk.cool_update('scripts',start=10,total=61))
            yield from asyncio.wait_for(fut,10)
            fut = self.loop.create_task(sk.cool_update('backend',start=20,total=61))
            yield from asyncio.wait_for(fut,10)
            fut = self.loop.create_task(sk.cool_update('central',start=30,total=61))
            yield from asyncio.wait_for(fut,10)
            fut = self.loop.create_task(sk.cool_update('frontend',start=40,total=61))
            yield from asyncio.wait_for(fut,10)
            fut = self.loop.create_task(sk.cool_update('firmware',start=50,total=61,action='START'))
            yield from asyncio.wait_for(fut,10)
        else:
            fut = self.loop.create_task(sk.cool_update(data,action='START'))
            yield from asyncio.wait_for(fut,10)
        #sk.update(data)

    def share_inet(self):
        sk.share_inet()
    