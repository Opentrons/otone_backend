#!/usr/bin/env python3

import asyncio, json 
from file_io import FileIO
import script_keeper as sk

debug = False
io_debug = False

class Smoothie(object):
    """Smoothie class 

    The Smoothie class is instantiated into a smoothie object
    to communicate with the smoothieboard. A "nested" asyncio.Protocol subclass, CB_Factory, 
    is used with asyncio's create_connection function to create a streaming transport 
    connection to host and port 0.0.0.0:3333, which in turn is connected to the smoothieboard
    via ser2net. CB_Factory contains three callbacks:

    - connection_made
    - data_received
    - connection_lost


    CB_Factory Callbacks:

    - connection_made     causes the machine to home and is not currently set to call an external 
    callback

    - data_receieved      parses data receieved into command lines and calls the smoothieHandler 
    function for each command line and that in turn calls the onRawData and onStateChange external
    callbacks

    - connection_lost     is not currently set to an external callback

    
    External Callbacks:

    - onRawData

    - onStateChange

    The smoothie object also contains an index of smoothieboard commands in the form of a 
    dictionary object called _dict, and a dictionary object called theState to hold information about the state
    of the robot.
    """

    _dict = {
        'absoluteMove' : "G90\r\nG0",
        'relativeMove' : "G91\r\nG0",
        'home' : "G28",
        'setupFeedback' : "M62",
        'off' : "M112",
        'on' : "M999",
        'speed_xyz' : "G0F",
        'speed_a' : "G0a",
        'speed_b' : "G0b",
        'reset' : 'reset'
    }

    theState = {
        'x': 0,
        'y': 0,
        'z': 0,
        'a': 0,
        'b': 0,
        'c': 0,
        'stat': 1,
        'delaying': 0,
        'homing': {
            'x': False,
            'y': False,
            'z': False,
            'a': False,
            'b': False,
            'c': False
        }
    }

    old_msg = ""
    
    def __init__(self, outer):
        self.my_transport = None
        self.outer = outer
        self.raw_callback = None
        self.my_loop = asyncio.get_event_loop()

    class CB_Factory(asyncio.Protocol):
        proc_data = ""
        old_data = None

        def __init__(self, outer):
            if debug == True: FileIO.log('smoothie_ser2net:\n\tCB_Factory.__init__ called')
            self.outer = outer
        
        def connection_made(self, transport):
            """callback when a connection is made"""
            if debug == True:
                FileIO.log("smoothie_ser2net:\n\tCB_Factory: connection received!")

            self.transport = transport
            self.outer.my_transport = transport
            loop = asyncio.get_event_loop()
            loop.call_later(2, self.outer.onSuccessConnecting)#, self.outer)


        def data_received(self, data):
            """callback when data is received from smoothieboard"""
            if debug==True or io_debug==True:
                if self.old_data != data:            
                    FileIO.log('smoothie_ser2net:\n\tCBFactory.data_received: '+data.decode(),'\n')
                    self.old_data = data
            
            self.proc_data = self.proc_data + data.decode()
            deli = "\n"
            sub_data = self.proc_data[:self.proc_data.rfind("\n")]
            self.proc_data = self.proc_data[self.proc_data.rfind("\n")+1:]
            list_data = [e+deli for e in sub_data.split(deli)]
            for ds in list_data:
                self.outer.smoothieHandler(ds,data)  #self.outer
            

        def connection_lost(self, exc):
            """callback when connection is lost"""
            if debug == True:
                FileIO.log("smoothie_ser2net:\n\tCBFactory: connection lost!")
            
            self.outer.my_transport = None
            proc_data = ""
            self.outer.onDisconnect()#self.outer)

    def set_raw_callback(self, callback):
        """connects the external callback for raw data"""
        self.raw_callback = callback

    def connect(self):
        self.my_loop = asyncio.get_event_loop()
        callbacker = self.CB_Factory(self)
        asyncio.async(self.my_loop.create_connection(lambda: callbacker, host='0.0.0.0', port=3333))


    def onSuccessConnecting(self):
        """smoothie callback for when a connection is made"""
        if debug == True:
            FileIO.log('smoothie_ser2net.onSuccessConnecting called')
        #print(type(self._dict['setupFeedback']))
        thestring = self._dict['setupFeedback']
        if debug == True:
            print(thestring)
        self.send(thestring)#self  self._dict['setupFeedback'])
        #if debug!=True:
        self.home(dict())
        sk.write_led(17,0)
        #sk.set_connection_status(99)
            #pass
        self.onConnect(self.theState) #self


    def send(self, string):
        """sends data to the smoothieboard using a transport"""
        if debug == True:
            FileIO.log('smoothie_ser2net.send called,\n\tstring: ',string,'\n')
        self.onRawData('--> '+string)  #self
        if self.my_transport is not None:
            strong = string + "\r\n"
            self.my_transport.write(strong.encode())


    def smoothieHandler(self, msg, data_):
        """handle lines of data from smoothieboard"""
        ok_print = False
        if debug == True:
            if self.old_msg != msg:
                ok_print = True
                FileIO.log('smoothie_ser2net.smoothieHandler called,\n\tmsg: ',msg,'\n')
        self.onRawData(msg)   #self

        #print('msg type: ',type(msg))
        #print('msg.find?: ',msg.find('{'))
        if msg.find('{')>=0:
            try:
                data = json.loads(msg)
            except:
                FileIO.log('json.loads(msg) error:\n\nmsg is...\n\n',msg,'\n\noriginal message was...\n\n',data_,'\n')
            didStateChange = False
            stillHoming = False
            if ok_print:
                if debug == True: FileIO.log('smoothie_ser2net:\n\ttheState: ',self.theState,'\n')
            for key, value in data.items():
                if ok_print:
                    if key in self.theState:
                        if debug == True: FileIO.log('smoothie_ser2net:\n\ttheState[',key,'] = ',self.theState[key],'\n')
                if key == 'stat' and self.theState[key] != value:
                    didStateChange = True

                self.theState[key] = value
                if ok_print:
                    if debug == True:
                        FileIO.log('smoothie_ser2net:\n\tkey:   ',key)
                        FileIO.log('smoothie_ser2net:\n\tvalue: ',value,'\n')
                #print('homing[key]: ',self.theState['homing'][key])
                if key!='stat' and key!='homing' and key!='delaying':
                    if key.isalnum() and value == 0 and self.theState['homing'][key]==True:
                        self.theState['homing'][key] = False

                        for h_key, h_value in self.theState['homing'].items():
                            if h_value == True:
                                stillHoming = True

                        if stillHoming==False:
                            didStateChange = True

            if didStateChange == True:
                self.onStateChange(self.theState)

            self.prevMsg = msg
            if ok_print:
                if debug == True: FileIO.log('smoothie_ser2net:\n\tdidStateChange?: ',didStateChange,'\n')


    def getState(self):
        temp_state = dict(self.theState)
        return temp_state


    def move(self, coords_list):
        if debug == True: FileIO.log('smoothie_ser2net.move called,\ncoords_list: ',coords_list,'\n')
        
        absolMov = True
        if isinstance(coords_list, dict):
            header = self._dict['absoluteMove']
            if 'relative' in coords_list:
                if coords_list['relative']==True:
                    absolMove = False
                    header = self._dict['relativeMove']
        
            cmd = header

            for n, value in coords_list.items():
                if debug == True:
                    FileIO.log('smoothie_ser2net:\n\tn:     ',n)
                    FileIO.log('smoothie_ser2net:\n\tvalue: ',value,'\n')
                    FileIO.log('smoothie_ser2net:\n\tvalue type: ', type(value),'\n')
                if n.upper()=='X' or n.upper()=='Y' or n.upper()=='Z' or n.upper()=='A' or n.upper()=='B':
                    axis = n.upper()
                    cmd = cmd + axis

                    if absolMove == true:
                        try:
                            if float(value)<0:
                                value = 0
                        except:
                            pass

                    cmd = cmd + str(value)
                    if debug == True: FileIO.log('smoothie_ser2net:\n\tcmd: ',cmd,'\n')
                    

                if debug == True: FileIO.log('smoothie_ser2net:\n\tmy_transport not none? ',self.my_transport is not None)

            if self.my_transport is not None:
                self.send(cmd)


    def delay(self, milli_seconds):
        float_milli_seconds = float(milli_seconds)    
        if float_milli_seconds >= 0:
            self.my_loop.call_later(float(float(milli_seconds)/1000.0), self.delay_state)
            self.theState['delaying'] = 1
            self.onStateChange(self.theState)


    def delay_state(self):
        self.theState['delaying'] = 0
        self.onStateChange(self.theState)


    def home(self, axis_dict):
        #axis_dict = json.loads(axisJSON)
        if debug == True:
            FileIO.log('smoothie_ser2net.home called,\n\taxis_dict: ', axis_dict,'\n')
        if axis_dict is None or len(axis_dict)==0:
            axis_dict = {'a':True, 'b':True, 'x':True, 'y':True, 'z':True}

        self.halt() #self
        
        homeCommand = ''
        homingX = False
        
        if 'a' in axis_dict or 'A' in axis_dict:
            homeCommand += self._dict['home']
            homeCommand += 'A'
            self.theState['homing']['a'] = True

        if 'b' in axis_dict or 'B' in axis_dict:
            homeCommand += self._dict['home']
            homeCommand += 'B'
            self.theState['homing']['b'] = True

        if 'z' in axis_dict or 'Z' in axis_dict:
            homeCommand += self._dict['home']
            homeCommand += 'Z'
            self.theState['homing']['z'] = True

        if 'x' in axis_dict or 'X' in axis_dict:
            homeCommand += self._dict['home']
            homeCommand += 'X'
            self.theState['homing']['x'] = True
            homingX = True

        if 'y' in axis_dict or 'Y' in axis_dict:
            if homingX == False:
                homeCommand += self._dict['home']
            homeCommand += 'Y'
            self.theState['homing']['y'] = True

        if len(homeCommand)>=3:
            homeCommand += '\r\n'
            self.send(homeCommand)


    def halt(self):
        """halt robot"""
        if self.my_transport is not None:
            onOffString = self._dict['off'] + '\r\n' + self._dict['on']
            self.send(onOffString)    #self


    def reset(self):
        """reset robot"""
        if self.my_transport is not None:
            resetString = _dict['reset']
            self.send(self, resetString)


    def set_speed(self, axis, value):
        """set the speed for a given axis"""
        if debug == True: FileIO.log('smoothie_ser2net.set_speed called,\n\taxis: ',axis,'\n\tvalue: ',value)
        if self.my_transport is not None:
            if isinstance(value,(int, float, complex)) or isinstance(value, str):
                if axis=='xyz' or axis=='a' or axis == 'b':
                    string = self._dict['speed_'+axis] + str(value)
                    self.send(string)
                else:
                    FileIO.log('smoothie_ser2net.set_speed: axis??? '+axis)
            else:
                FileIO.log('smoothie_ser2net: value is not a number???')
        else:
            FileIO.log('smoothie_ser2net: my_transport is None')


    def raw(self, string):
        """send a raw command to the smoothieboard"""
        if self.my_transport is not None:
            self.send(string)


    #############################################
    #
    #   CALLBACKS
    #
    #############################################

    # FIRST SET EXTERNAL CALLBACKS

    #def setOnDisconnectCB(self, od_cb):
    #    self.od_cb = od_cb

    #def setOnStateChangeCB(self, osc_cb):
    #    self.osc_cb = osc_cb
    # The callback 'hooks'


    def onConnect(self, theState):
        """callback when connection made"""
        if debug == True:
            FileIO.log('smoothie_ser2net.onConnect called')


    def onDisconnect(self):
        """callback when disconnected"""
        if debug == True:
            FileIO.log('smoothie_ser2net.onDisconnect called')
        #if hasattr(self.od_cb, '__call__'):
        #    self.od_cb()

    def onRawData(self, msg):
        """external callback showing raw data lines received"""
        if debug == True:
            if self.old_msg != msg:
                if debug == True: FileIO.log('smoothie_ser2net.onRawData called')
                self.old_msg = msg
        if self.raw_callback != None:
            self.raw_callback(msg)
        

    def onStateChange(self, state):
        """external callback when theState changes"""
        #if debug_flag==True:
        FileIO.log('smoothie_ser2net.onStateChange called,\n\n\tstate:\n\n',state,'\n')
        if hasattr(self.outer,'on_state_change'):
            try:
                self.outer.on_state_change(state)
            except:
                FileIO.log('smoothie_ser2net.onStateChange: problem calling self.outer.on_state_change')
                raise


if __name__ == '__main__':
    smooth = Smoothie()
    smooth.connect()
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()


