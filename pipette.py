from tool import Tool
from file_io import FileIO
import math, collections

debug = False

class Pipette(Tool):
    """Pipette Class
    
    Class for holding a pipette's calibrated values, and includes functions
    for mapping locations and such.
    Each pipette instance is created inside the head object, and is either
    motor axis 'a' or 'b'
    
    Calibrated values include:
        Plunger locations(top, bottom, blowout, droptip)
        Container coordinates (XYZ coordinate of each container's origin)
    """

#Special Methods
    #from pipette.js    
    def __init__(self, axis):
        """initialize Tool
        
        toolname = the name of the tool (string)
        tooltype = the type of tool e.g. 1ch pipette, 8ch pipette, etc.(string)
        axis = position of tool on head & associated 
                motor (A, B, C, etc) (string)
        offset = the offset in space from the A tool which is defined to
            have offset = (0,0,0)
        """
        if debug == True: FileIO.log('pipette.__init__ called')
        toolname = axis + '_pipette'
        super().__init__(toolname, 'pipette', axis)
        
        #default parameters to start with
        self.resting = 0  #rest position of plunger when not engaged
        self.top = 0   #just touching the plunger (saved)
        self.bottom = 1  #calculated by pipette object (saved)
        self.blowout = 2  #value saved 2-5 mm before droptip (saved)
        self.droptip = 4  #complete max position of plunger (saved)
        
        #the calibrated plate offsets for this pipette
        
        self.volume = 200  #max volume pipette can hold calculated during calibration (saved in pipette_calibrations.json)
        self.bottom_distance = 2 #distance between blowout and botton
        
        self.theContainers = {} #(saved)


    def __str__(self):
        return "{0.toolname!r}".format(self)
       
       
    def __repr__(self):
        return "Pipette({0.toolname!r},{0.tooltype!r},{0.axis!r})".format(self)
        
        
#Methods
    #from pipette.js        
    def init_sequence(self):
        """
        """
        if debug == True: FileIO.log('pipette.init_sequence called')
        oneCommand = {}
        oneCommand[self.axis] = self.resting #self.bottom
        
        return [oneCommand]
        
    #from pipette.js       
    def end_sequence(self):
        """
        """
        if debug == True: FileIO.log('pipette.end_sequence called')
        oneCommand = {}
        
        return [oneCommand]
        
    #from pipette.js 
    #main function is to translate instructions from rel coordinates to 
    #absolute coords.
    def pmap(self, loc):
        if debug == True:
            FileIO.log('pipette.pmap called')
            FileIO.log('\nMapping...\n\n')
            FileIO.log(loc,'\n\n')
        """function formerly called map, renamed due to python name conflict
        
        loc = {
            x:number, 
            y:number,
            z:number,
            container:string,////
            plunger:float ||'blowout' || 'droptip' || 'resting'
            speed: integer ms (add label for this pipettes axis)
        }
        """
        temploc = collections.OrderedDict()
        should_home_axis = False
        

        for n in loc:
            if n=='plunger':
                  #convert the relative thumb value to it's absolute coordinate
                  if loc[n]=='blowout':
                      temploc[self.axis] = self.blowout
         
                  elif loc[n]=='droptip':
                      temploc[self.axis] = self.droptip
                      should_home_axis = True
                      
                  elif loc[n] == 'resting':
                      temploc[self.axis] = self.resting
              
                  else:
                      #print('loc[n]: ',loc[n])
                      temploc[self.axis] = self.rel_to_abs(float(loc[n]))
                      
            # if there is a container specified, all XYZ values are 
            #relative to self container's origin
            elif n=='container':
                containerName = loc[n]
                if(containerName in self.theContainers):
                    # save the container's coords
                    theContainer = self.theContainers[containerName]
                    temploc['container'] = {
                        'x' : theContainer['x'],
                        'y' : theContainer['y'],
                        'z' : theContainer['z']
                    }
                else:
                    #js console.log('Cannot find container '+containerName)
                    FileIO.log('Cannot find container '+containerName)
            elif n == 'speed':
                temploc['axis'] = self.axis
                temploc[n] = loc[n]
            else:
                temploc[n] = loc[n] # just copy over other coordinates
    
        # then add the container's position to self location
        # only if it has been specified
        #ToDo: probably need to utilize None instead of math.nan here
        #this flips the coord system
        if 'container' in loc:
            if loc['container'] is not None:
                if debug == True: FileIO.log('temploc:\n\n',temploc,'\n\n')
                if 'x' in temploc and 'x' in temploc['container']:
                    if not math.isnan(temploc['x']) and not math.isnan(temploc['container']['x']):
                        # moving right from container.x
                        temploc['x'] = temploc['container']['x'] + temploc['x'] 

                if 'y' in temploc and 'y' in temploc['container']:
                    if not math.isnan(temploc['y']) and not math.isnan(temploc['container']['y']):
                        # moving away (forward) from container.y
                        temploc['y'] = temploc['container']['y'] - temploc['y'] 

                if 'z' in temploc and 'z' in temploc['container']:
                    if not math.isnan(temploc['z']) and not math.isnan(temploc['container']['z']):
                        # moving vertically from container.z when positive
                        temploc['z'] = temploc['container']['z'] - temploc['z'] 

                del temploc['container']

#        # don't let it go less than 0 on any axis
#        for c in temploc:
#            if temploc[c]<0:  temploc[c]=0

        return_value = [temploc]
        
        if should_home_axis:
            top_command = collections.OrderedDict()
            top_command[self.axis] = self.resting
            return_value.append(top_command)

            home_command = collections.OrderedDict()
            home_command[self.axis] = True
            return_value.append({'home': home_command}) #if dip has been dropped
        
#        return temploc
        if debug == True: FileIO.log('return_value:\n\n',return_value,'\n')
        return return_value


    #from pipette.js  
    def calibrate(self, property_, value):
        """
        """
        if debug == True: FileIO.log('pipette.calibrate called')
       #ToDo: probably need to utilize None instead of math.nan here
        if (value != None and (property_=='top' or property_=='blowout' or property_=='droptip')):

            # if it's a top or blowout value, save it
            self.__dict__[property_] = value  
            
            self.bottom = self.blowout - self.bottom_distance

      
    #from pipette.js
    def create_deck(self, containerNameArray):
        """
       
        all container's created while the robot is (regardless of how many jobs it runs)
        will be saved for each pipette, so that it's XYZ origin is remembered until poweroff
        """

        if debug == True: 
            FileIO.log('pipette.create_deck called,\ncontainerNameArray:\n', containerNameArray,'\n')
            FileIO.log('\nBEFORE self.theContainers:\n',self.theContainers,'\n')
        
        
        if containerNameArray and len(containerNameArray)>0:
            #self.theOldContainers = [self.theConold_name for old_name in self.theContainers if old_name in containerNameArray]
            for k in list(self.theContainers.keys()):
                if k not in containerNameArray:
                    del self.theContainers[k]

            #js for i=0  i<containerNameArray.length  i++:
            for i in range(0,len(containerNameArray)):
                if containerNameArray[i] not in list(self.theContainers.keys()):
                    self.theContainers[containerNameArray[i]] = {'x' : None,'y' : None,'z' : None}
                    
        if debug == True: FileIO.log('\nAFTER self.theContainers:\n',self.theContainers,'\n')
        return self.theContainers

    #from pipette.js
    def calibrate_container(self, containerName, coords):
        """
        """
        if debug == True: FileIO.log('pipette.calibrate_container called,\ncontainerName: ',containerName,',\ncoords: ',coords,'\n')
        if containerName and self.theContainers[containerName] and coords:
            FileIO.log('type(coords) = ',type(coords))
            if coords['x'] is not None:
                self.theContainers[containerName]['x'] = coords['x']  
            if coords['y'] is not None:
                self.theContainers[containerName]['y'] = coords['y']  
            if coords['z'] is not None:
                self.theContainers[containerName]['z'] = coords['z']  

                #js console.log('axis '+self.axis+ 'calibrated container '+containerName)  
                #js console.log(self.theContainers[containerName])
            if debug == True: FileIO.log('\naxis ',self.axis, 'calibrated container ',containerName,'\n')  
                

    #from pipette.js        
    def rel_to_abs(self, rel_val):
        """
        """
        if debug == True: FileIO.log('pipette.rel_to_abs called,\n\nrel_val: ',rel_val,'\n')

        if rel_val is not None:
            #FileIO.log('******************')
            #FileIO.log('type(rel_val) = ',type(rel_val))
            #FileIO.log('******************')
            if rel_val < 0: rel_val = 0  
            if rel_val > 1: rel_val = 1  
            diff = self.bottom - self.top  
            absol = (rel_val * diff) + self.top  
            #js if abs % 1 > 0: abs = abs.toFixed(2)
            if absol % 1 > 0: absol = round(absol,2)
            #js return Number(absol) 
            return absol

       