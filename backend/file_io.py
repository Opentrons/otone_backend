import json
import datetime, collections

class FileIO:
    """Provides static methods for file i/o and logging
    
    The FileIO class is intended to provide standard static methods for use
    by other classes in the application.
    """
    

#Special Methods
    def __init__(self):
        """Initialize FileIO object
        
        """
        #ToDo: read in a config file containing paths to folders for
        #protocol files, log files, labware files, calibration files, etc.
        
    def __str__(self):
        return "FileIO"
        
        
#static methods
    @staticmethod
    def writeFile(filename,filetext,onError):
        FileIO.log('file_io.writeFile called, filetext: ',filetext)
        try:
            out_file = None
            out_file = open(filename, "w")
            out_file.write(filetext)
        except:
            raise
            if hasattr(onError,'__call__'):
                onError()
    
    @staticmethod
    def log(*msg):
        tstamp = datetime.datetime.now()
        try:
            logfile = None
            logfile = open('logfile.txt',"a")
            print(tstamp, '-', "".join([str(m) for m in msg]))
            #print(tstamp, '-', "".join([str(m) for m in msg]), file = logfile)
        except EnvironmentError as err:
            print('Error appending log file: {0}'.format(err))
        finally:
            if logfile is not None:
                logfile.close()
    
    @staticmethod
    def onError(msg,data=None):
        pass
    
    @staticmethod
    def readfile(filename, encoding, onError):
        pass
    
    @staticmethod
    def get_dict_from_json(fname):
        try:
            in_file = None
            in_file = open(fname,"r")   # Open the file
            prot_dict = json.load(in_file,object_pairs_hook=collections.OrderedDict)   #create dictionary from file
            print ("FileIO: json file: '{0}' imported!".format(fname))
        except EnvironmentError as err:
            print('Error reading json file: ',err)
            raise

        finally:
            if in_file is not None:
                in_file.close()  # Close the file
                return prot_dict
            else:
                return None
        
        
