#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 15:11:09 2015

@author: Randy
"""

#import RobotLib
from head import Head
from deck import Deck
from protocol_runner import ProtocolRunner
from global_handlers import GlobalHandlers
from file_io import FileIO
from ingredients import Ingredients
from dispatcher import Dispatcher

import json, asyncio, sys, time, collections
import script_keeper as sk



debug = True

#VARIABLES

#declare globol objects here
head = None
deck = None
runner = None
dispatcher = None
global_handlers = None
def_start_protocol = None
client_status = False
crossbar_status = False

if debug == True: FileIO.log('starting up')
#for testing purposes, read in a protocol.json file
fname='/home/pi/otone_backend/sample_user_protocol.json'
prot_dict = FileIO.get_dict_from_json(fname)


#Import and setup autobahn WAMP peer
from autobahn.asyncio import wamp, websocket

class WampComponent(wamp.ApplicationSession):

    def onConnect(self):
        self.join(u"ot_realm")

    @asyncio.coroutine
    def onJoin(self, details):
        if debug == True: FileIO.log('OTOne_Client : WampComponent.onJoin called')
        if not self.factory._myAppSession:
            self.factory._myAppSession = self
        
        crossbar_status = True    
        instantiate_objects()
        
        
        def set_client_status(status):
            if debug == True: FileIO.log('OTOne_Client : WampComponent.set_client_status called')
            client_status = status
            self.publish('com.opentrons.robot_ready',True)
        
        self.publish('com.opentrons.robot_ready',True)
        yield from self.subscribe(set_client_status, 'com.opentrons.browser_ready')
        yield from self.subscribe(dispatcher.dispatch_message, 'com.opentrons.browser_to_robot')
        
    def onLeave(self, details):
        if self.factory._myAppSession == self:
            self.factory._myAppSession = None
        self.disconnect()
        
    def onDisconnect(self):
        asyncio.get_event_loop().stop()


def make_a_connection():

    coro = loop.create_connection(transport_factory, '127.0.0.1', 8080)

    transporter, protocoler = loop.run_until_complete(coro)
    #instantiate the dispatcher and global_handlers for communication
    

    loop.run_forever()

def instantiate_objects():
    FileIO.log('instantiate_objects called')
    #get default json file
    def_start_protocol = FileIO.get_dict_from_json('/home/pi/otone_backend/default_startup_protocol.json')
    #RobotLib.FileIO.get_dict_from_json('/home/pi/PythonProject/default_startup_protocol.json')

    #instantiate the head 
    head = Head(def_start_protocol['head'], global_handlers)
    if debug == True:
        FileIO.log('head string: ', str(head))
        FileIO.log('head representation: ', repr(head))

    #instantiate the deck
    deck = Deck(def_start_protocol['deck'])
    #RobotLib.Deck(def_start_protocol['deck'])
    if debug == True:
        FileIO.log('deck string: ', str(deck))
        FileIO.log('deck representation: ', repr(deck))

    runner = ProtocolRunner(head, global_handlers)


    #use the head data to configure the head
    head_data = {}
    head_data = prot_dict['head']   #extract the head section from prot_dict
    #    head = RobotLib.Head({})        #instantiate an empty head
    #head.configure_head(head_data)  #configure the head from prot_dict data
    if debug == True:
        FileIO.log ("Head configured!")

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
    #RobotLib.Ingredients({})     #instantiate an empty ingredients object
    ingr.configure_ingredients(ingr_data) #configure the ingredienets from prot_dict data
    if debug == True:
        FileIO.log('Ingredients imported!')

        FileIO.log('this is a test') 
    #RobotLib.FileIO.log('this is a test')

    global_handlers.setHead(head)
    global_handlers.setRunner(runner)
    dispatcher.setHead(head)
    dispatcher.setRunner(runner)


    @asyncio.coroutine
    def periodically_send_ip_addresses():
        FileIO.log('periodically_send_ip_addresses called')
        while True:
            FileIO.log('periodically_send_ip_addresses again...')
            yield from asyncio.sleep(10)
            #stuff = loop.run_until_complete(sk.per_data())
            stuff = yield from sk.per_data()
            session_factory._myAppSession.publish('com.opentrons.robot_to_browser_ctrl',json.dumps(stuff,sort_keys=True,indent=4,separators=(',',': ')))
            
            #session_factory._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(sk.get_wifi_ip_address(),sort_keys=True,indent=4,separators=(',',': ')))
            #session_factory._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(sk.get_eth_ip_address(),sort_keys=True,indent=4,separators=(',',': ')))
            #session_factory._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(sk.get_iwconfig_essid(),sort_keys=True,indent=4,separators=(',',': ')))
            #session_factory._myAppSession.publish('com.opentrons.robot_to_browser',json.dumps(sk.connection(),sort_keys=True,indent=4,separators=(',',': ')))


    

    @asyncio.coroutine
    def get_wifi_ip_address():
        FileIO.log('OTOne_Client.py -> get_wifi_ip_address called')
        return sk.get_wifi_ip_address()

    @asyncio.coroutine
    def get_eth_ip_address():
        FileIO.log('OTOne_Client.py -> get_eth_ip_address called')
        return sk.get_eth_ip_address()


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

    dispatcher = Dispatcher(session_factory, loop)
    global_handlers = GlobalHandlers(session_factory)
    

    while (crossbar_status == False):
        try:
            FileIO.log('trying to make a connection...')
            make_a_connection()
            # NOT SURE IF time.sleep(10) IS EVER CALLED BECAUSE IF loop.run_forever() SUCCEEDS, DOES IT EVEN GET HERE? 
            # IF IT FAILS, DOES IT EVEN GET HERE?
            time.sleep(10)  
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




