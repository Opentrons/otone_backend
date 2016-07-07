import collections
import datetime
import json
import logging


logger = logging.getLogger('app.file_io')


class FileIO:
    """
    
    The FileIO class is intended to provide standard static methods for use
    by other classes in the application.
    """
    

#Special Methods
    def __init__(self):
        """Initialize FileIO object
        
        """
        #ToDo: read in a config file containing paths to folders for
        #protocol files, log files, labware files, calibration files, etc.
        pass
        
    def __str__(self):
        return "FileIO"
        
        
#static methods
    @staticmethod
    def writeFile(filename,filetext,onError):
        logger.debug('file_io.writeFile called, filetext: {}'.format(filetext))
        try:
            out_file = None
            out_file = open(filename, "w")
            out_file.write(filetext)
        except:
            raise
            if hasattr(onError,'__call__'):
                onError()
    
    @staticmethod
    def onError(msg,data=None):
        pass
    
    @staticmethod
    def readfile(filename, encoding, onError):
        pass
    
    @staticmethod
    def get_dict_from_json(fname):
        logger = logging.getLogger('logger.file_io')
        try:
            in_file = None
            in_file = open(fname,"r")   # Open the file
            prot_dict = json.load(in_file,object_pairs_hook=collections.OrderedDict)   #create dictionary from file
            logger.debug("FileIO: json file: '{0}' imported!".format(fname))
        except EnvironmentError as err:
            logger.error('Error reading json file: {}'.format(err))
            raise

        finally:
            if in_file is not None:
                in_file.close()  # Close the file
                return prot_dict
            else:
                return None
        
        
