#!/usr/bin/env python3

import asyncio, json, math
from file_io import FileIO
import script_keeper as sk

debug = True
io_debug = False
verbose = False

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

    - data_receieved      parses data receieved into command lines and calls the smoothie_handler 
    function for each command line and that in turn calls the on_raw_data and on_state_change external
    callbacks

    - connection_lost     is not currently set to an external callback

    
    External Callbacks:

    - on_raw_data

    - on_state_change

    - on_limit_hit

    The smoothie object also contains an index of smoothieboard commands in the form of a 
    dictionary object called _dict, and a dictionary object called theState to hold information about the state
    of the robot.

    :todo:
    1. Show an example coords_list in documentation (:meth:`move`)
    2. (see also below)

    :See also:
    :download:`../../backend/OTONE_DATAFLOW.pdf`
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
        'speed_c' : "G0c",
        'reset' : 'reset'
    }

    theState = {
        'x': 0,
        'y': 0,
        'z': 0,
        'a': 0,
        'b': 0,
        'c': 0,
        'direction': {
            'x': 0,
            'y': 0,
            'z': 0,
            'a': 0,
            'b': 0,
            'c': 0
        },
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
        self.position_callback = None
        self.limit_hit_callback = None
        self.move_callback = None
        self.delay_callback = None
        self.my_loop = asyncio.get_event_loop()
        self.smoothieQueue = list()
        self.already_trying = False
        self.ack_msg_rcvd = "ok"
        self.state_ready = 0
        self.delay_handler = None
        self.delay_start = 0
        self.delay_end = 0

    class CB_Factory(asyncio.Protocol):
        proc_data = ""
        old_data = None

        def __init__(self, outer):
            if debug == True: FileIO.log('smoothie_ser2net:\n\tCB_Factory.__init__ called')
            self.outer = outer
        
        def connection_made(self, transport):
            """Callback when a connection is made
            """
            if debug == True: FileIO.log("smoothie_ser2net:\n\tCB_Factory.connection_made called")

            self.transport = transport
            self.outer.my_transport = transport
            loop = asyncio.get_event_loop()
            loop.call_later(2, self.outer.on_success_connecting)#, self.outer)


        def data_received(self, data):
            """Callback when data is received from Smoothieboard
            """
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
                self.outer.smoothie_handler(ds,data)  #self.outer
            

        def connection_lost(self, exc):
            """Callback when connection is lost
            """
            if debug == True:
                FileIO.log("smoothie_ser2net:\n\tCBFactory.connection_lost called")
            
            self.outer.my_transport = None
            proc_data = ""
            self.outer.on_disconnect()#self.outer)

    def set_raw_callback(self, callback):
        """connects the external callback for raw data
        """
        if debug == True: FileIO.log('smoothie_ser2net.set_raw_callback called')
        self.raw_callback = callback


    def set_position_callback(self, callback):
        """connects the external callback for position data
        """
        if debug == True: FileIO.log('smoothie_ser2net.set_position_callback called')
        self.position_callback = callback


    def set_limit_hit_callback(self, callback):
        """Connect the external callback for limit hit data
        """
        if debug == True: FileIO.log('smoothie_ser2net.set_limit_hit_callback called')
        self.limit_hit_callback = callback

    def set_move_callback(self, callback):
        """Connect the external callback for move call
        """
        if debug == True: FileIO.log('smoothie_ser2net.set_move_callback called')
        self.move_callback = callback

    def set_delay_callback(self, callback):
        self.delay_callback = callback

    def connect(self):
        """Make a connection to Smoothieboard using :class:`CB_Factory`
        """
        if debug == True: FileIO.log('smoothie_ser2net.connect called')
        self.my_loop = asyncio.get_event_loop()
        callbacker = self.CB_Factory(self)
        asyncio.async(self.my_loop.create_connection(lambda: callbacker, host='0.0.0.0', port=3333))


    def on_success_connecting(self):
        """Smoothie callback for when a connection is made

        Sends startup commands to engage automatic feedback from Smoothieboard, :meth:`home`, 
        and call :meth:`on_connect` callback
        """
        if debug == True: FileIO.log('smoothie_ser2net.on_success_connecting called')
        #print(type(self._dict['setupFeedback']))
        thestring = self._dict['setupFeedback']
        if debug == True and verbose == True: print(thestring)
        #self.try_add(thestring)
        self.send(thestring)#self  self._dict['setupFeedback'])
        #if debug!=True:
        self.home(dict())
        sk.write_led(17,0)
        #sk.set_connection_status(99)
            #pass
        self.on_connect(self.theState) #self


    def send(self, string):
        """sends data to the smoothieboard using a transport
        """
        if debug == True:
            FileIO.log('smoothie_ser2net.send called')
            if verbose == True: FileIO.log('\n\tstring: ',string,'\n')
        self.on_raw_data('--> '+string)  #self
        if self.my_transport is not None:
            strong = string + "\r\n"
            self.my_transport.write(strong.encode())


    def smoothie_handler(self, msg, data_):
        """Handle lines of data from Smoothieboard
        """
        ok_print = False
        if debug == True:
            if self.old_msg != msg:
                ok_print = True
                FileIO.log('smoothie_ser2net.smoothie_handler called')
                if verbose == True: FileIO.log('\n\tmsg: ',msg,'\n')
        self.on_raw_data(msg)   #self

        #print('msg type: ',type(msg))
        #print('msg.find?: ',msg.find('{'))
        if self.ack_msg_rcvd in msg:
            self.already_trying = False
            FileIO.log('ok... self.already_trying: ',self.already_trying)
        if msg.find('{')>=0:
            msg = msg[msg.index('{'):]
            try:
                data = json.loads(msg)
            except:
                FileIO.log('json.loads(msg) error:\n\nmsg is...\n\n',msg,'\n\noriginal message was...\n\n',data_,'\n')
            didStateChange = False
            stillHoming = False
            if ok_print:
                if debug == True and verbose == True: FileIO.log('smoothie_ser2net(1):\n\ttheState: ',self.theState,'\n')
            for key, value in data.items():
                if key == "!!":
                    self.already_trying = False
                    self.try_step()
                if ok_print:
                    if key in self.theState:
                        if debug == True and verbose == True: FileIO.log('smoothie_ser2net:\n\ttheState[',key,'] = ',self.theState[key],'\n')
                if key == 'stat' and self.theState[key] != value:
                    didStateChange = True
                    self.already_trying = False

                if key in self.theState:
                    if key.upper()=='X' or key.upper()=='Y':
                        self.theState[key] = value + self.theState['direction'][key]
                    else:
                        self.theState[key] = value
                if ok_print:
                    if debug == True and verbose == True:
                        FileIO.log('smoothie_ser2net:\n\tkey:   ',key)
                        FileIO.log('smoothie_ser2net:\n\tvalue: ',value,'\n')
                #print('homing[key]: ',self.theState['homing'][key])
                if key!='stat' and key!='homing' and key!='delaying':
                    if key.isalnum() and value == 0 and self.theState['homing'][key]==True:
                        if debug == True and verbose == True:
                            FileIO.log('smoothie_ser2net:\n\tchanging key [',key,'] homing to False')
                        self.theState['homing'][key] = False
                        self.theState['direction'][key] = 0
                        for h_key, h_value in self.theState['homing'].items():
                            if h_value == True:
                                stillHoming = True

                        if stillHoming==False:
                            didStateChange = True

                if key == 'limit':
                    self.on_limit_hit(value)


            if 'x' in data or 'y' in data or 'z' in data or 'a' in data or 'b' in data or 'c' in data:
                pos = {}
                pos['x']=self.theState['x']
                pos['y']=self.theState['y']
                pos['z']=self.theState['z']
                pos['a']=self.theState['a']
                pos['b']=self.theState['b']
                pos['c']=self.theState['c']
                self.on_position_data(pos)

            if didStateChange == True or self.theState['stat']==self.state_ready and self.already_trying == False:
                if len(self.smoothieQueue)>0:
                    self.try_step()
                else:
                    if didStateChange == True:
                        self.on_state_change(self.theState)


            self.prevMsg = msg
            if ok_print:
                if debug == True: FileIO.log('smoothie_ser2net:\n\tdidStateChange?: ',didStateChange,'\n')


    def get_state(self):
        """Returns the robot state

        example state:

        theState = {
        'x': 0,
        'y': 0,
        'z': 0,
        'a': 0,
        'b': 0,
        'c': 0,
        'stat': 1,
        'direction': {
            'x': 0,
            'y': 0,
            'z': 0,
            'a': 0,
            'b': 0,
            'c': 0
        },
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

        """
        if debug == True: FileIO.log('smoothie_ser2net.get_state called')
        temp_state = dict(self.theState)
        return temp_state


    def try_add(self, cmd):
        """Add a command to the smoothieQueue
        """
        FileIO.log('smoothie_ser2net.try_add called')
        self.smoothieQueue.append(cmd)
        #if len(self.smoothieQueue) == 1:
        self.try_step()


    def move(self, coords_list):
        """Move according to coords_list

        :todo:
        1. Show an example coords_list in documentation
        """
        if debug == True: 
            FileIO.log('smoothie_ser2net.move called')
            if verbose == True: FileIO.log('\ncoords_list: ',coords_list,'\n')
        
        absolMov = True
        if isinstance(coords_list, dict):
            header = self._dict['absoluteMove']
            if 'relative' in coords_list:
                if coords_list['relative']==True:
                    absolMov = False
                    header = self._dict['relativeMove']
        
            cmd = header

            for n, value in coords_list.items():
                if debug == True and verbose == True:
                    FileIO.log('smoothie_ser2net:\n\tn:     ',n)
                    FileIO.log('smoothie_ser2net:\n\tvalue: ',value,'\n')
                    FileIO.log('smoothie_ser2net:\n\tvalue type: ', type(value),'\n')
                if n.upper()=='X' or n.upper()=='Y' or n.upper()=='Z' or n.upper()=='A' or n.upper()=='B':
                    axis = n.upper()
                    cmd = cmd + axis

                    if absolMov == True:
                        try:
                            if float(value)<0:
                                value = 0
                            #SWITCH DIRECTION STUFF HERE
                            if axis=='X' or axis=='Y':
                                tvalue = float(self.theState[n])
                                if value < tvalue and self.theState['direction'][n]==0:
                                    self.theState['direction'][n] = 0.5
                                elif value > tvalue and self.theState['direction'][n]>0:
                                    self.theState['direction'][n] = 0
                                value = value - self.theState['direction'][n]
                        except:
                            pass
                    else:
                        if axis=='X' or axis=='Y':
                            if value < 0 and self.theState['direction'][n]==0:
                                self.theState['direction'][n] = 0.5
                                value = value - self.theState['direction'][n]
                            elif value > 0 and self.theState['direction'][n]>0:
                                value = value + self.theState['direction'][n]
                                self.theState['direction'][n] = 0
                    cmd = cmd + str(value)
                    if debug == True and verbose == True: FileIO.log('smoothie_ser2net:\n\tcmd: ',cmd,'\n')

                if debug == True and verbose == True: FileIO.log('smoothie_ser2net:\n\tmy_transport not none? ',self.my_transport is not None)

            self.try_add(cmd)
            
#            if self.my_transport is not None:
#                self.move_callback()
#                self.send(cmd)


    def try_step(self):
        """Try to step the smoothieQueue
        """
        if debug == True: 
            FileIO.log('smoothie_ser2net.try_step called')
            FileIO.log('self.already_trying: ',self.already_trying)
            FileIO.log("self.theState['stat']: ",self.theState['stat'])
            FileIO.log("self.theState['delaying']: ",self.theState['delaying'])
        if self.theState['stat'] == 0 and self.theState['delaying'] == 0 and self.already_trying == False:
            self.already_trying = True
            cmd = self.smoothieQueue.pop(0)
            self.send(cmd)
        


    def delay(self, seconds):
        """Delay for given number of milli_seconds
        """
        if debug == True: FileIO.log('smoothie_ser2net.delay called')
        #print('seconds: ', seconds)
        try:
            float_seconds = float(seconds)
        except:
            print('*** error floating seconds ***')
            float_seconds = 0
        finally:
            if float_seconds >= 0:
                self.start = self.my_loop.time()
                self.end = self.start + float_seconds
                self.theState['delaying'] = 1
                self.on_state_change(self.theState)
                self.delay_handler = self.my_loop.call_at(self.end, self.delay_state)
                self.delay_message()


    def delay_message(self):
        time_left = math.floor(self.end - self.my_loop.time())
        if time_left >= 0:
            if self.delay_callback is not None:
                self.delay_callback(time_left)
                self.my_loop.call_later(1,self.delay_message)


    def delay_state(self):
        """Sets theState object's delaying value to 0, and then calls :meth:`on_state_change`.
        Used by :meth:`delay` for timing end of a delay
        """
        if debug == True: FileIO.log('smoothie_ser2net.delay_state called')
        self.theState['delaying'] = 0
        self.on_state_change(self.theState)


    def home(self, axis_dict):
        """Home robots according to axis_dict argument

        If axis_dict is empty, homes all in the order ABZ, XY, to clear the deck before moving in XY plane
        """
        #axis_dict = json.loads(axisJSON)
        if debug == True:
            FileIO.log('smoothie_ser2net.home called')
            if verbose == True: FileIO.log('\n\taxis_dict: ', axis_dict,'\n')
        if axis_dict is None or len(axis_dict)==0:
            axis_dict = {'a':True, 'b':True, 'x':True, 'y':True, 'z':True}

        self.halt() #self
        
        homeCommand = ''
        homingX = False
        homingABZ = False
        
        if 'a' in axis_dict or 'A' in axis_dict:
            homeCommand += self._dict['home']
            homeCommand += 'A'
            self.theState['homing']['a'] = True
            homingABZ = True

        if 'b' in axis_dict or 'B' in axis_dict:
            if homingABZ == False:
                homeCommand += self._dict['home']
            homeCommand += 'B'
            self.theState['homing']['b'] = True
            homingABZ = True

        if 'z' in axis_dict or 'Z' in axis_dict:
            if homingABZ == False:
                homeCommand += self._dict['home']
            homeCommand += 'Z'
            self.theState['homing']['z'] = True
            homingABZ = True

        if homingABZ == True:
            homeCommand += '\r\n'
            self.try_add(homeCommand)
            homeCommand = ''

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
            self.try_add(homeCommand)


    def halt(self):
        """Halt robot
        """
        if debug == True: FileIO.log('smoothie_ser2net.halt called')
        if self.delay_handler is not None:
            self.delay_handler.cancel()
            self.delay_handler = None
            self.delay_state()
        if self.my_transport is not None:
            #onOffString = self._dict['off'] + '\r\n' + self._dict['on']
            self.try_add(self._dict['off'] + '\r\n')
            self.try_add(self._dict['on'] + '\r\n')
            self.raw(self._dict['on'] + '\r\n') #just in case...
            #self.send(onOffString)    #self


    def reset(self):
        """Reset robot
        """
        if debug == True: FileIO.log('smoothie_ser2net.reset called')
        if self.my_transport is not None:
            resetString = _dict['reset']
            self.send(self, resetString)


    def set_speed(self, axis, value):
        """Set the speed for a given axis
        """
        if debug == True:
            FileIO.log('smoothie_ser2net.set_speed called')
            if verbose == True: FileIO.log('\n\taxis: ',axis,'\n\tvalue: ',value)
        if self.my_transport is not None:
            if isinstance(value,(int, float, complex)) or isinstance(value, str):
                if axis=='xyz' or axis=='a' or axis == 'b' or axis == 'c':
                    string = self._dict['speed_'+axis] + str(value)
                    self.try_add(string)
                    #self.send(string)
                else:
                    FileIO.log('smoothie_ser2net.set_speed: axis??? '+axis)
            else:
                FileIO.log('smoothie_ser2net: value is not a number???')
        else:
            FileIO.log('smoothie_ser2net: my_transport is None')


    def raw(self, string):
        """Send a raw command to the Smoothieboard
        """
        if self.my_transport is not None:
            #self.try_add(string)
            self.send(string)


    #############################################
    #
    #   CALLBACKS
    #
    #############################################

    # FIRST SET EXTERNAL CALLBACKS

    #def set_on_disconnect_cb(self, od_cb):
    #    self.od_cb = od_cb

    #def set_on_ctate_change_cb(self, osc_cb):
    #    self.osc_cb = osc_cb
    # The callback 'hooks'


    def on_connect(self, theState):
        """Callback when connection made

        currently does zilch
        """
        if debug == True:
            FileIO.log('smoothie_ser2net.on_connect called')

    @asyncio.coroutine
    def on_disconnect(self):
        """Callback when disconnected
        """
        if debug == True: FileIO.log('smoothie_ser2net.on_disconnect called')
        while True:
            yield from asyncio.sleep(10)
            try:
                self.connect()
            except:
                FileIO.log('error trying to connect')
        #if hasattr(self.od_cb, '__call__'):
        #    self.od_cb()

    def on_raw_data(self, msg):
        """Calls an external callback to show raw data lines received
        """
        if debug == True:
            if self.old_msg != msg and verbose == False:
                if debug == True: FileIO.log('smoothie_ser2net.on_raw_data called')
                self.old_msg = msg
        if self.raw_callback != None:
            self.raw_callback(msg)


    def on_position_data(self, msg):
        """Calls an external callback to show raw data lines received
        """
        if debug == True: FileIO.log('smoothie_ser2net.on_position_data called')
        if self.position_callback != None:
            self.position_callback(msg)
        

    def on_state_change(self, state):
        """Calls an external callback for when theState changes
        """
        if debug==True:
            FileIO.log('smoothie_ser2net.on_state_change called')
            if verbose == True: FileIO.log('\n\n\tstate:\n\n',state,'\n')
        if hasattr(self.outer,'on_state_change'):
            try:
                self.outer.on_state_change(state)
            except:
                FileIO.log('smoothie_ser2net.on_state_change: problem calling self.outer.on_state_change')
                raise

    def on_limit_hit(self, axis):
        """Calls an external callback for when a limitswitch is hit
        """
        if debug == True:
            FileIO.log('smoothie_ser2net.on_limit_hit called')
            if verbose == True: FileIO.log('\n\n\taxis:\n\n',axis,'\n')
        if self.limit_hit_callback != None:
            self.limit_hit_callback(axis)


if __name__ == '__main__':
    smooth = Smoothie()
    smooth.connect()
    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()
