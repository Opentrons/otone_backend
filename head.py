import smoothie_ser2net as openSmoothie
from the_queue import TheQueue
from file_io import FileIO
from pipette import Pipette
import json

debug = False

class Head:
    """Head Class
    
    the Head class is intended to be instantiated to a head object which
    aggregates the subclassed tool objects and the smoothieAPI object.
    It also hold a references to the theQueue and global_handlers objects.
    Appropriate methods are exposed to allow access to the aggregated object's
    functionality.
    """
    
#Special Methods-----------------------
    #def __init__(self, tools, global_handlers, theQueue):
    def __init__(self, tools, global_handlers):
        """initialize Head object
        
        tools = dictionary of the tools on the head
        
        """
        if debug == True: FileIO.log('head.__init__ called')
        self.smoothieAPI = openSmoothie.Smoothie(self)
        self.tools = tools
        self.PIPETTES = {'a':Pipette('a'),'b':Pipette('b')}    #need to create this dict in head setup
        self.ghand = global_handlers
        self.smoothieAPI.set_raw_callback(self.ghand.onRawData)
        self.theQueue = TheQueue(self, global_handlers)
        
        #connect with the smoothie board
        self.smoothieAPI.connect()
        

        self.load_pipette_values()
        
    def __str__(self):
        return "Head"
        
    def __repr__(self):
        return "Head({0!r})".format(self.tools.keys())
        
# the current coordinate position, as reported from 'smoothie.js'
    theState = {'x' : 0,'y' : 0,'z' : 0,'a' : 0,'b' : 0}

    # this function fires when 'smoothie.js' transitions between {stat:0} and {stat:1}
    #SMOOTHIEBOARD.onStateChange = function (state) {
    def on_state_change(self, state):
        if debug == True: FileIO.log('head.on_state_change called')
        
        if state['stat'] == 1 or state['delaying'] == 1:
            self.theQueue.is_busy = True

        elif state['stat'] == 0 and state['delaying'] == 0:
            self.theQueue.is_busy = False
            self.theQueue.currentCommand = None
            if self.theQueue.paused==False:
                self.theQueue.step(False)
    
        self.theState = state
        if debug == True: FileIO.log('\n\n\tHead state:\n\n',self.theState,'\n')

#local functions---------------
    def get_tool_info(self, head_data):
        """function to get the tooltype and axis from head data dict
        
        returns a tuple (tool_type, axis)
        """
        if debug == True: FileIO.log('head.get_tool_info called')
        tool_type = head_data['tool']
        axis = head_data['axis']
        
        return (tool_type, axis)
        
        
        
#Methods-----------------------
    def configure_head(self, head_data):
        """Method to configure the head per Head section of protocol.json file
        
        head_data = dictionary of head data (example below):
            "p200" : {
                "tool" : "pipette",
                "tip-racks" : [{"container" : "p200-rack"}],
                "trash-container" : {"container" : "trash"},
                "tip-depth" : 5,
                "tip-height" : 45,
                "tip-total" : 8,
                "axis" : "a",
                "volume" : 160
            },
            "p1000" : {
                "tool" : "pipette",
                "tip-racks" : [{"container" : "p1000-rack"}],
                "trash-container" : {"container" : "trash"},
                "tip-depth" : 7,
                "tip-height" : 65,
                "tip-total" : 8,
                "axis" : "b",
                "volume" : 800
            }
        """
        if debug == True: FileIO.log('head.configure_head called')
        #delete any previous tools in head
        del self.tools
        self.tools = []
        
        #instantiate a new tool for each name and tool type in the file
        #ToDo - check for data validity before using
        for key in head_data:
            hd = head_data[key]
            #get the tool type to know what kind of tool to instantiate
            tool_info = self.get_tool_info(hd)  #tuple (toolType, axis)
            if tool_info[0] == 'pipette':
                newtool = Pipette(hd['axis'])
            elif tool_info[0] == 'grabber':
                newtool = Grabber(key,*tool_info)
            else:
                #ToDo - add error handling here
                pass
            
            #add tool to the tools list
            self.tools.append(newtool)
        
        #fill the PIPETTES object with tools of the tool type 'pipette'
        for tool in self.tools:
            print('from line 545 in head: ',tool,type(tool))
            if tool.tooltype == 'pipette':
                axis = tool.axis
                self.PIPETTES[axis] = tool
        
    #this came from pipette class in js code
    def create_pipettes(self, axis):
        """Method for creating a dictionary of Pipette objects
        
        """
        if debug == True: FileIO.log('head.create_pipettes called')
        thePipettes = {}
        if len(axis):
            for a in axis:
            #for i in range(0,len(axis)):
                #a = axis(i)
                thePipettes[a] = Pipette(a)
                
        return thePipettes
        
        
    #Command related methods for the head object
    #corresponding to the exposed methods in the Planner.js file
    #from planner.js
    def home(self, axis_dict):   #, callback):
        """
        
        """
        #maps to smoothieAPI.home()
        #function home(axis_dict)        #,callback)
        #print('{} msg received in head, calling home on smoothie'.format(axis_dict))
        if debug == True: FileIO.log('head.home called, args: ',axis_dict)
        
        callback = None     #ToDo: decide what to do with this
        self.smoothieAPI.home(axis_dict)
        
        
    #from planner.js
    def raw(self, string):
        """
        
        """
        if debug == True: FileIO.log('head.raw called')
        #maps to smoothieAPI.raw()
        #function raw(string)
        self.smoothieAPI.raw(string)
        
        
    #from planner.js
    def kill(self):	#, callback):
        """
        
        """
        if debug == True: FileIO.log('head.kill called')
        #maps to smoothieAPI.halt() with extra code
        #function kill (callback)
#        print('{} msg received in head, calling halt on smoothie'.format(data))
        self.smoothieAPI.halt()
        self.theQueue.clear();

    #from planner.js
    def reset(self):	#, callback):
        """
        
        """
        if debug == True: FileIO.log('head.reset called')
        #maps to smoothieAPI.reset() with extra code
        #function reset (callback)
        self.smoothieAPI.reset()
        self.theQueue.clear();
        
        
    #from planner.js
    def get_state(self):
        """
        
        """
        if debug == True: FileIO.log('head.get_state called')
        #maps to smoothieAPI.get_state()
        #function getState ()
        return self.smoothieAPI.get_state()
        
        
        #from planner.js
    def set_speed(self, axis, value):
        if debug == True: FileIO.log('head.set_speed called')
        """
        
        """
        #maps to smoothieAPI.set_speed()
        #function setSpeed(axis, value, callback)
        self.smoothieAPI.set_speed(axis, value)
        
        
        #from planner.js
        #function move (locations)
        #doesn't map to smoothieAPI
    def move(self, locations):
        """

        var locations = [location,location,...]

        var location = {
        'relative' : true || false || undefined (defaults to absolute)
        'x' : 30,
        'y' : 20,
        'z' : 10,
        'a' : 20,
        'b' : 32
        }

        """
        if debug == True: FileIO.log('head.move called')
        if locations:
            if debug == True:
                FileIO.log('\n#####\n')
                FileIO.log(locations)
            self.theQueue.add(locations)
        
    #from planner.js
    #function step (locations)
    #doesn't map to smoothieAPI
    def step(self, locations):
        """
        
        locations = [location,location,...]

        location = {
        'x' : 30,
        'y' : 20,
        'z' : 10,
        'a' : 20,
        'b' : 32
        }
        """
        if debug == True: 
            FileIO.log('head.step called,\n\tlocations:\n\n',locations,'\n')
            # only step with the UI if the queue is currently empty
            FileIO.log('head:\n\tlen(self.theQueue.qlist): ',len(self.theQueue.qlist),'\n')
            FileIO.log('head:\n\tself.theQueue.is_busy?: ',self.theQueue.is_busy,'\n')
        if len(self.theQueue.qlist)==0: # and self.theQueue.is_busy==False:

            if locations is not None:
                if isinstance(locations,list):
#                    for( i = 0; i < locations.length; i++):
                    for i in range(len(locations)):
                        locations[i]['relative']  = True
                        
                elif ('x' in locations) or ('y' in locations) or ('z' in locations) or ('a' in locations) or ('b' in locations):
                    locations['relative']  = True
                    
                self.move(locations)
         
         
    #from planner.js
    #function pipette(group)
    def pipette(self, group):
        """
        group = {
          command : 'pipette',
          axis : 'a' || 'b',
          locations : [location, location, ...]
        }
    
        location = {
          x : number,
          y : number,
          z : number,
          container : string,
          plunger : float || 'blowout' || 'droptip'
        }
    
        # if a container is specified, XYZ coordinates are relative to the container's origin
        # if no container is specified, XYZ coordinates are absolute to the smoothieboard
        """

        if group and 'axis' in group and group['axis'] in self.PIPETTES and 'locations' in group and len(group['locations'])>0:
    
            this_axis = group['axis']  
            current_pipette = self.PIPETTES[this_axis]  
    
            # the array of move commands we are about to build from each location
            # starting with this pipette's initializing move commands
            move_commands = current_pipette.init_sequence()
            if debug == True:
                FileIO.log('\nhead.pipette\n\tcurrent_pipette.init_sequence():\n\n',current_pipette.init_sequence(),'\n')
                FileIO.log('\nhead.pipette\n\tmove_commands:\n\n',move_commands,'\n')
    
            # loop through each location
            # using each pipette's calibrations to test and convert to absolute coordinates
            for i in range(len(group['locations'])) :
    
                thisLocation = group['locations'][i]  
    
                # convert to absolute coordinates for the specifed pipette axis
                if debug == True: FileIO.log('head.pipette:\n\tlocation: ',thisLocation,'\n')
                absCoords = current_pipette.pmap(thisLocation)  
    
                # add the absolute coordinates we just made to our final array
                move_commands.extend(absCoords)  
    
            if len(move_commands):
                move_commands.extend(current_pipette.end_sequence())  
                self.move(move_commands)  
      
    
    #from planner.js
    #ToDo: may want to change "property" to something else
    def calibrate(self, pipette, property_):
        """
        #function calibrate (pipette,property)
        """
        if debug == True: FileIO.log('head.calibrate called')
        #maps to smoothieAPI.get_state() with extra code
        if pipette and self.PIPETTES[pipette]:

#            value  
            state = self.smoothieAPI.getState()  

            # firststop, bottom to delete
            if property_=='top' or property_=='blowout' or property_=='droptip':
                value = state[pipette]  
                self.PIPETTES[pipette].calibrate(property_,value)  

                self.save_pipette_values()  
                return  
            
            else: # 'property' is a string representing a container's name

                if debug == True: FileIO.log('calibrating  container')  
                # calibrate the plate with current smoothie state
                self.PIPETTES[pipette].calibrate_container(property_,state)  

                # RESPONSE NOT BEING USED CURRENTLY
                # return all container's and their origin coordinates
                # this is so the interface can be aware of what and where all save containers are
                #response = {}  

                #for n in self.PIPETTES:
                #    response[n] = self.PIPETTES[n].theContainers  
                
                #self.save_pipette_values()
                #return response
             
    def save_volume(self, data):
        """
        
        """
        if debug == True: FileIO.log('head.save_volume called')
        if(self.PIPETTES[data.axis] and data.volume is not None and data.volume > 0):
            self.PIPETTES[data.axis].volume = data.volume
            
        self.save_pipette_values()
        
        
    #from planner.js
    def save_pipette_values(self):
        if debug == True: FileIO.log('head.save_pipette_values called')
        pipette_values = {}

        for axis in self.PIPETTES:
            pipette_values[axis] = {}
            for k, v in self.PIPETTES[axis].__dict__.items():
                pipette_values[axis][k] = v

            # should include:
            #  'top'
            #  'bottom'
            #  'blowout'
            #  'droptip'
            #  'volume'
            #  'theContainers'

        filetext = json.dumps(pipette_values,sort_keys=True,indent=4,separators=(',',': '))
        if debug == True: FileIO.log('filetext: ', filetext)
        filename = '/home/pi/otone_backend/pipette_calibrations.json'

        # save the pipette's values to a local file, to be loaded when the server restarts
        FileIO.writeFile(filename,filetext,lambda: FileIO.onError('\t\tError saving the file:\r\r'))      


    #from planner.js
    #fs.readFile('./data/pipette_calibrations.json', 'utf8', function (err,data)
    #load_pipette_values()
    def load_pipette_values(self):
        if debug == True: FileIO.log('head.load_pipette_values called')
        old_values = FileIO.get_dict_from_json('/home/pi/otone_backend/pipette_calibrations.json')
        if debug == True: FileIO.log('old_values:\n',old_values,'\n')
        
        if self.PIPETTES is not None and len(self.PIPETTES) > 0:
            for axis in old_values:
                #for n in old_values[axis]:
                for k, v in old_values[axis].items():
                    self.PIPETTES[axis].__dict__[k] = v

                    # should include:
                    #  'resting'
                    #  'top'
                    #  'bottom'
                    #  'blowout'
                    #  'droptip'
                    #  'volume'
                    #  'theContainers'
            
            if debug == True: FileIO.log('self.PIPETTES[',axis,']:\n\n',self.PIPETTES[axis],'\n')
        else:
            if debug == True: FileIO.log('head.load_pipette_values: No pipettes defined in PIPETTES')
            
    #from planner.js
    # an array of new container names to be stored in each pipette
    #ToDo: this method may be redundant
    def create_deck(self, newDeck):
        if debug == True: FileIO.log('head.create_deck called,\nnewDeck:\n\n', newDeck,'\n')
        """an array of new container names to be stored in each pipette
        
        """
        #doesn't map to smoothieAPI
        nameArray = []  

        for containerName in newDeck :
            nameArray.append(containerName) 
        
        response = {}  
        
        for n in self.PIPETTES:
            response[n] = self.PIPETTES[n].create_deck(nameArray)  

        self.save_pipette_values() 
        return response         
            
            
    def get_deck(self):#not sure why newDeck was included before... , newDeck):
        """an array of new container names to be stored in each pipette
        
        """
        if debug == True: FileIO.log('head.get_deck called')
        response = {}
        for axis in self.PIPETTES:
            response[axis] = {}
            if debug == True: FileIO.log('self.PIPETTES[',axis,'].theContainers:\n\n',self.PIPETTES[axis].theContainers)
            for name in self.PIPETTES[axis].theContainers:
                if debug == True: FileIO.log('self.PIPETTES[',axis,'].theContainers[',name,']:\n\n',self.PIPETTES[axis].theContainers[name])
                response[axis][name] = self.PIPETTES[axis].theContainers[name]
  
        self.save_pipette_values()
        return response
        
        
    def get_pipette(self):
        """an array of new container names to be stored in each pipette
        
        """
        if debug == True: FileIO.log('head.get_pipette called')
        response = {}

        for axis in self.PIPETTES:
            response[axis] = {}
            for k, v in self.PIPETTES[axis].__dict__.items():
                response[axis][k] = v
            
            # should include:
            #  'top'
            #  'bottom'
            #  'blowout'
            #  'droptip'
            #  'volume'
              
        return response

    #from planner.js
    #ToDo: may want to change "property" to something else
    def move_pipette(self, axis, property_):
        """
        
        this moves the pipette to one of it's calibrated positions (top, bottom, blowout, droptip)
        and is useful for seeing where its saved positions are while calibrating
        """
        #doesn't map to smoothieAPI
        #function movePipette (axis, property)
        if debug == True:
            FileIO.log('head.move_pipette called,\n\taxis: ',axis,'\n\tproperty_: ',property_)
            FileIO.log('head:\n\tself.PIPETTES[axis].__dict__[',property_,'] = ',self.PIPETTES[axis].__dict__[property_])
        if self.PIPETTES[axis] and property_ in self.PIPETTES[axis].__dict__:
            moveCommand = {}
            moveCommand[axis] = self.PIPETTES[axis].__dict__[property_]
            if debug == True:
                FileIO.log('head.move_pipette:\n\tmoveCommand = ',moveCommand)
                FileIO.log(moveCommand)
            self.move(moveCommand)
            
    
    
    def move_plunger(self, axis, locations):
        """
        
        locations = [loc, loc, etc... ]

        loc = {'plunger' : number}
        """

        if debug == True:
            FileIO.log('head.move_plunger called')
            FileIO.log('!!!!!!!!!!!')
            FileIO.log(locations)

        if(self.PIPETTES[axis]):
            for i in range(len(locations)):
                moveCommand = self.PIPETTES[axis].pmap(locations[i])
                self.move(moveCommand)


    def save_plunger(self, axis, location):
        """

        location = {'plunger' : number }
        """
        if debug == True: FileIO.log('head.save_plunger called')
        # the plunger comes in, specifying the desired percentage
        if self.PIPETTES[axis]:

            # first, get the current smoothie position of this axis
            currentLocation = self.theState[axis]
            
            self.PIPETTES[axis].tune (location.plunger, currentLocation)

            self.savePipetteValues()


    def erase_job(self):
        if debug == True: FileIO.log('head.erase_job called')
        self.theQueue.clear()
