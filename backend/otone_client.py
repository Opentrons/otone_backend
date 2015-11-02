#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 15:11:09 2015

@author: Randy

This is the main module of the OTOne Python backend code. When started, it creates 
a publisher (:class:`publisher.Publisher`) and a subscriber (:class:`subscriber.Subscriber`)
for handling all communication with a WAMP router and then tries to make a connection 
(:meth:`otone_client.make_a_connection`) with the Crossbar.io WAMP router. Once that 
connection is established, it instantiates and configures various objects with 
:meth:`otone_client.instantiate_objects`:
 
 head: :class:`head.Head` - Represents the robot head and creates a connection with Smoothieboard
 
 deck: :class:`deck.Deck` - Represents the robot deck

 runner: :class:`protocol_runner.ProtocolRunner` - Runs protocol jobs

 the_sk: :class:`script_keeper.ScriptKeeper` - Handles shell scripts


"""

#import RobotLib
import json, asyncio, sys, time, collections, os, sys, shutil

from head import Head
from deck import Deck

from subscriber import Subscriber
from publisher import Publisher

from file_io import FileIO
from ingredients import Ingredients

from protocol_runner import ProtocolRunner

import script_keeper as sk
from script_keeper import ScriptKeeper


debug = True
verbose = False

#VARIABLES

#declare globol objects here
head = None
deck = None
runner = None
subscriber = None
publisher = None
def_start_protocol = None
client_status = False
crossbar_status = False

if debug == True: FileIO.log('starting up')
#for testing purposes, read in a protocol.json file
path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)
dir_par_path = os.path.dirname(dir_path)
dir_par_par_path = os.path.dirname(dir_par_path)
fname_default_protocol = os.path.join(dir_path,'data/sample_user_protocol.json')
fname_default_containers = os.path.join(dir_path, 'data/containers.json')
fname_default_calibrations = os.path.join(dir_path, 'data/pipette_calibrations.json')
fname_data = os.path.join(dir_par_par_path,'otone_data')
fname_data_containers = os.path.join(dir_par_par_path,'otone_data/containers.json')
fname_data_calibrations = os.path.join(dir_par_par_path, 'otone_data/pipette_calibrations.json')
print('dir_path: ', dir_path)
print('dir_par_path: ', dir_par_path)
print('dir_par_part_path: ', dir_par_par_path)
print('fname_data: ', fname_data)
print('fname_default_containers: ', fname_default_containers)
print('fname_data_containers: ', fname_data_containers)


if not os.path.isdir(fname_data):
    os.makedirs(fname_data)
#if not os.path.exists(fname_data_containers):
open(fname_data_containers,"w+")
shutil.copy(fname_default_containers, fname_data_containers)

if not os.path.exists(fname_data_calibrations):
    open(fname_data_calibrations,"w+")
    shutil.copy(fname_default_calibrations, fname_data_calibrations)

prot_dict = FileIO.get_dict_from_json(fname_default_protocol)



#Import and setup autobahn WAMP peer
from autobahn.asyncio import wamp, websocket

class WampComponent(wamp.ApplicationSession):
    """WAMP application session for OTOne (Overrides protocol.ApplicationSession - WAMP endpoint session)
    """

    def onConnect(self):
        """Callback fired when the transport this session will run over has been established.
        """
        self.join(u"ot_realm")

    @asyncio.coroutine
    def onJoin(self, details):
        """Callback fired when WAMP session has been established.

        May return a Deferred/Future.

        Starts instatiation of robot objects by calling :meth:`otone_client.instantiate_objects`.
        """
        if debug == True: FileIO.log('otone_client : WampComponent.onJoin called')
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
        
        crossbar_status = True    
        instantiate_objects()
        
        
        def set_client_status(status):
            if debug == True: FileIO.log('otone_client : WampComponent.set_client_status called')
            global client_status
            client_status = status
            self.publish('com.opentrons.robot_ready',True)
        
        FileIO.log('about to publish com.opentrons.robot_ready TRUE')
        self.publish('com.opentrons.robot_ready',True)
        yield from self.subscribe(set_client_status, 'com.opentrons.browser_ready')
        yield from self.subscribe(subscriber.dispatch_message, 'com.opentrons.browser_to_robot')


    def onLeave(self, details):
        """Callback fired when WAMP session has been closed.
        
        :param details: Close information.
        """
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        try:
            self.disconnect()
        except:
            pass
        
    def onDisconnect(self):
        """Callback fired when underlying transport has been closed.
        """
        asyncio.get_event_loop().stop()


def make_a_connection():
    """Attempt to create streaming transport connection and run event loop
    """
    coro = loop.create_connection(transport_factory, '127.0.0.1', 8080)

    transporter, protocoler = loop.run_until_complete(coro)
    #instantiate the subscriber and publisher for communication
    
    loop.run_forever()


def instantiate_objects():
    """After connection has been made, instatiate the various robot objects
    """
    FileIO.log('instantiate_objects called')
    #get default json file
    def_start_protocol = FileIO.get_dict_from_json(os.path.join(dir_path,'data/default_startup_protocol.json'))
    #FileIO.get_dict_from_json('/home/pi/PythonProject/default_startup_protocol.json')


    #instantiate the head 
    head = Head(def_start_protocol['head'], publisher)
    if debug == True:
        FileIO.log('head string: ', str(head))
        FileIO.log('head representation: ', repr(head))
    #use the head data to configure the head
    head_data = {}
    head_data = prot_dict['head']   #extract the head section from prot_dict
    #    head = RobotLib.Head({})        #instantiate an empty head
    #head.configure_head(head_data)  #configure the head from prot_dict data
    if debug == True:
        FileIO.log ("Head configured!")


    #instantiate the script keeper (sk)
    the_sk = ScriptKeeper(publisher)


    #instantiate the deck
    deck = Deck(def_start_protocol['deck'], publisher)
    if debug == True:
        FileIO.log('deck string: ', str(deck))
        FileIO.log('deck representation: ', repr(deck))


    runner = ProtocolRunner(head, publisher)

    
    #use the deck data to configure the deck
    deck_data = {}
    deck_data = prot_dict['deck']   #extract the deck section from prot_dict
    #    deck = RobotLib.Deck({})        #instantiate an empty deck
    deck.configure_deck(deck_data)  #configure the deck from prot_dict data
    if debug == True:
        FileIO.log ("Deck configured!")


    #do something with the Ingredient data
    ingr_data = {}
    ingr_data = prot_dict['ingredients'] #extract the ingredient section from prot_dict
    ingr = Ingredients({}) 
    
    ingr.configure_ingredients(ingr_data) #configure the ingredienets from prot_dict data
    if debug == True:
        FileIO.log('Ingredients imported!')
        FileIO.log('this is a test') 


    publisher.set_head(head)
    publisher.set_runner(runner)
    subscriber.set_deck(deck)
    subscriber.set_head(head)
    subscriber.set_runner(runner)


    @asyncio.coroutine
    def periodically_send_ip_addresses():
        """Coroutine that periodically sends information to browser
        """
        if debug == True and verbose == True: FileIO.log('periodically_send_ip_addresses called')
        while True:
            if debug == True and verbose == True: FileIO.log('periodically_send_ip_addresses again...')
            yield from asyncio.sleep(2)
            stuff = yield from sk.per_data()
            session_factory._myAppSession.publish('com.opentrons.robot_to_browser_ctrl',json.dumps(stuff,sort_keys=True,indent=4,separators=(',',': ')))


    asyncio.Task(periodically_send_ip_addresses())


try:
    session_factory = wamp.ApplicationSessionFactory()
    session_factory.session = WampComponent

    session_factory._myAppSession = None

    url = "ws://127.0.0.1:8080/ws"
    transport_factory = websocket \
            .WampWebSocketClientFactory(session_factory,
                                        url=url,
                                        debug=False,
                                        debug_wamp=False)
    loop = asyncio.get_event_loop()

    subscriber = Subscriber(session_factory, loop)
    publisher = Publisher(session_factory)
    

    while (crossbar_status == False):
        try:
            FileIO.log('trying to make a connection...')
            make_a_connection()
        except KeyboardInterrupt:
            crossbar_status = True
        except:
            #raise
            pass
        finally:
            FileIO.log('error while trying to make a connection, sleeping for 5 seconds')
            time.sleep(5)
except KeyboardInterrupt:
    pass
finally:
    loop.close()




