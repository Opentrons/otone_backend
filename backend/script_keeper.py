#!/usr/bin/python3

import subprocess, collections, json, asyncio, os
from file_io import FileIO

debug = True
updated = False
verbose = False



class ScriptKeeper:
    """The ScriptKeeper class handles all things shell script

    The ScriptKeeper class is intended to be instantiated to a ScriptKeeper object 
    useful for aggregating all things shell script related.

    ot_config file aggregates useful information for reference

    :todo:
    Formalize format and keywords of data returning from shell otone_scripts (:meth:`read_progress`)
    """
    
    #Special Methods-----------------------
    #def __init__(self, tools, global_handlers, theQueue):
    def __init__(self, publisher):
        """Initialize ScriptKeeper object
        """
        if debug == True: FileIO.log('script_keeper.__init__ called')
        global pubber
        global updated
        global path
        global dir_path
        pubber = publisher
        updated = False
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        #get path one directory up from dir_path
        #otone_scripts_path 
        

    def __str__(self):
        return "ScriptKeeper"


#change_wifi_connection_mode = os.path.join(dir_path, ...traverse down to otone_scripts
#list_wicd_networks = os.path.join(dir_path, ...traverse down to otone_scripts
#set_hostname = os.path.join(dir_path, ...traverse down to otone_scripts
#get_ifconfig_wlan0_ip = os.path.join(dir_path, ...traverse down to otone_scripts
#get_ifconfig_eth0_ip = os.path.join(dir_path, ...traverse down to otone_scripts
#get_iwconfig_essid = os.path.join(dir_path, ...traverse down to otone_scripts
#write_led = os.path.join(dir_path, ...traverse down to otone_scripts
#start = os.path.join(dir_path, ...traverse down to otone_scripts
#connection = os.path.join(dir_path, ...traverse down to otone_scripts
#share_inet = os.path.join(dir_path, ...traverse down to otone_scripts
#set_ot_config_connection_status = os.path.join(dir_path, ...traverse down to otone_scripts


def change_wifi_mode(data):
    """Change wifi mode (NONE, AP(access point), WIFI(wifi network))
    """
    if debug == True: FileIO.log('script_keeper.change_wifi_mode called')
    if data and len(data):
        if str(data['mode'])=='AP':
            subprocess.call([os.path.join(dir_path,'../../otone_scripts/change_wifi_connection_mode.sh'), str(data['mode'])])
        if str(data['mode'])=='WIFI':
            subprocess.call([os.path.join(dir_path,'../../otone_scripts/change_wifi_connection_mode.sh'), str(data['mode']),str(data['ssid']),str(data['pswd'])])
        if str(data['mode'])=='NONE':
            subprocess.call([os.path.join(dir_path,'../../otone_scripts/change_wifi_connection_mode.sh'), str(data['mode'])])

def scan_wifi_networks(data):
    """Scan wifi networks
    """
    if debug == True: FileIO.log('script_keeper.scan_wifi_networks called')
    return_dict = collections.OrderedDict({
        'type':'networks','data':subprocess.check_output(os.path.join(dir_path,"../../otone_scripts/list_wicd_networks.sh"), shell=True, universal_newlines=True).splitlines()
    })
    if debug == True and verbose == True: FileIO.log('wifi_scan data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def change_hostname(data):
    """Change the hostname
    """
    if debug == True: FileIO.log('script_keeper.change_hostname called')
    if data and len(data):
        subprocess.call(['sudo',os.path.join(dir_path,'../../otone_scripts/set_hostname.sh'),str(data)])
	
def get_wifi_ip_address():
    """Get wifi interface's ip address
    """
    if debug == True: FileIO.log('script_keeper.get_wifi_ip_address called')
    return_dict = collections.OrderedDict({
        'type': 'wifi_ip','data':subprocess.check_output(os.path.join(dir_path,"../../otone_scripts/get_ifconfig_wlan0_ip.sh"), shell=True, universal_newlines=True).replace('\n','')
    })
    if debug == True and verbose == True: FileIO.log('wifi_ip data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def get_eth_ip_address():
    """Get ethernet interface's ip address
    """
    if debug == True: FileIO.log('script_keeper.get_eth_ip_address called')
    return_dict = collections.OrderedDict({
        'type':'eth_ip','data':subprocess.check_output(os.path.join(dir_path,"../../otone_scripts/get_ifconfig_eth0_ip.sh"), shell=True, universal_newlines=True).replace('\n','')
    })
    if debug == True and verbose == True: FileIO.log('eth_ip data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def get_iwconfig_essid():
    """Get ESSID from iwconfig
    """
    if debug == True: FileIO.log('script_keeper.get_iwconfig_essid called')
    return_dict = collections.OrderedDict({
        'type':'wifi_essid','data':subprocess.check_output(os.path.join(dir_path,"../../otone_scripts/get_iwconfig_essid.sh"), shell=True, universal_newlines=True).replace('\n','')
    })
    if debug == True and verbose == True: FileIO.log('wifi_essid data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def write_led(num, val):
    """Turn an LED on or off.

    Not currently implemented. This is in anticipation of having LED indicators
    """
    if debug == True: FileIO.log('script_keeper.write_led called')
    subprocess.call([os.path.join(dir_path,'../../otone_scripts/write_led.sh'),str(num),str(val)])

def set_connection_status(num):
    """Set the connection-status in otconfig
    """
    if debug == True: FileIO.log('script_keeper.set_connection_status called')
    subprocess.call([os.path.join(dir_path,'../../otone_scripts/set_ot_config_connection_status.sh'),str(num)])

def poweroff():
    """Send the poweroff command
    """
    if debug == True: FileIO.log('script_keeper.poweroff called')
    subprocess.call(['sudo','poweroff'])

def reboot():
    """Send the reboot command
    """
    if debug == True: FileIO.log('script_keeper.reboot called')
    subprocess.call(['sudo', 'reboot'])

def restart():
    """Restart the Crossbar WAMP router and Python backend.

    By default, does not change networking configuration.
    """
    if debug == True: FileIO.log('script_keeper.restart called')
    subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh'), 'NOCHANGE'])


def connection():
    """Check internet connection
    
    :returns: string -- 'offline' or 'online'
    """
    if debug == True: FileIO.log('script_keeper.connection called')
    return_dict = collections.OrderedDict({
        'type':'internet','data':subprocess.check_output(os.path.join(dir_path,"../../otone_scripts/connection.sh"), shell=True, universal_newlines=True).replace('\n','')
    })
    if debug == True and verbose == True: FileIO.log('internet: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

@asyncio.coroutine
def share_inet():
    """Triggers ethernet interface (eth0) to try to obtain ip address via dhcp by taking it down, and then 
    bringing it up
    """
    if debug == True: FileIO.log('script_keeper.share_inet called')
    cmd = os.path.join(dir_path,'../../otone_scripts/share_inet.sh')

    create_share = asyncio.create_subprocess_exec(cmd,stdout=asyncio.subprocess.PIPE)

    criterion = True
    while criterion == True:
        proc_share = yield from create_share
        stdout_, stderr_ = yield from proc_share.communicate()

        if stdout_ is not None:
            stdout_str = stdout_.decode("utf-8")
            if debug == True and verbose == True: FileIO.log('share_inet.stdout... '+stdout_str)
            read_progress(stdout_str)
        else:
            if debug == True and verbose == True: FileIO.log('share_inet.stdout... None')
        if stderr_ is not None:
            if debug == True and verbose == True: FileIO.log('share_inet.stderr...'+stderr_.decode("utf-8"))
        else:
            if debug == True and verbose == True: FileIO.log('share_inet.stderr... None')
        if proc_share.returncode is not None:
            criterion = False
    return

    #subprocess.call(['sudo','ifdown','eth0'])
    #subprocess.call(['sudo','ifup','eth0'])

@asyncio.coroutine
def per_data():
    """Fetch data to be sent periodically to browser
    """
    if debug == True and verbose == True: FileIO.log('script_keeper.per_data called')
    create_internet = asyncio.create_subprocess_exec(os.path.join(dir_path,'../../otone_scripts/connection.sh'),stdout=asyncio.subprocess.PIPE)
    create_wifi_ip = asyncio.create_subprocess_exec(os.path.join(dir_path,'../../otone_scripts/get_ifconfig_wlan0_ip.sh'),stdout=asyncio.subprocess.PIPE)
    create_eth_ip = asyncio.create_subprocess_exec(os.path.join(dir_path,'../../otone_scripts/get_ifconfig_eth0_ip.sh'),stdout=asyncio.subprocess.PIPE)
    create_wifi_essid = asyncio.create_subprocess_exec(os.path.join(dir_path,'../../otone_scripts/get_iwconfig_essid.sh'),stdout=asyncio.subprocess.PIPE)
    
    proc_internet = yield from create_internet
    proc_wifi_ip = yield from create_wifi_ip
    proc_eth_ip = yield from create_eth_ip
    proc_wifi_essid = yield from create_wifi_essid

    internet = yield from proc_internet.stdout.readline()
    wifi_ip = yield from proc_wifi_ip.stdout.readline()
    eth_ip = yield from proc_eth_ip.stdout.readline()
    wifi_essid = yield from proc_wifi_essid.stdout.readline()

    line_internet = internet.decode('utf-8').rstrip()
    line_wifi_ip = wifi_ip.decode('utf-8').rstrip()
    line_eth_ip = eth_ip.decode('utf-8').rstrip()
    line_wifi_essid = wifi_essid.decode('utf-8').rstrip()

    yield from proc_internet.wait()
    yield from proc_wifi_ip.wait()
    yield from proc_eth_ip.wait()
    yield from proc_wifi_essid.wait()

    return_dict = collections.OrderedDict({
        'type':'per_data',
        'data': {
            'internet':line_internet,
            'wifi_ip':line_wifi_ip,
            'eth_ip':line_eth_ip,
            'wifi_essid':line_wifi_essid
        }
    })
    return return_dict


@asyncio.coroutine
def cool_update(data,start=1,total='',action='',option='NOCHANGE'):
    """Update a given area of codebase by repo and then take a given action
    """
    if debug == True: FileIO.log('script_keeper.cool_update called')
    cmd = os.path.join(dir_path,'../../otone_scripts/update_something.sh')
    arg1 = '--repo='+str(data)
    arg2 = '--start='+str(start)
    arg3 = '--total='+str(total)
    arg4 = '--action='+str(action)
    arg5 = '--option='+str(option)
    FileIO.log('arg1: ',arg1)
    FileIO.log('arg2: ',arg2)
    FileIO.log('arg3: ',arg3)
    FileIO.log('arg4: ',arg4)
    FileIO.log('arg5: ',arg5)
    create_update = asyncio.create_subprocess_exec(cmd, \
        arg1,  arg2, arg3, arg4, arg5, \
        stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
    criterion = True
    while criterion == True:
        proc_update = yield from create_update
        stdout_, stderr_ = yield from proc_update.communicate()

        if stdout_ is not None:
            stdout_str = stdout_.decode("utf-8")
            FileIO.log('stdout... '+stdout_str)
            read_progress(stdout_str)
        else:
            FileIO.log('stdout... None')
        if stderr_ is not None:
            FileIO.log('stderr...'+stderr_.decode("utf-8"))
        else:
            FileIO.log('stderr... None')
        if proc_update.returncode is not None:
            criterion = False
    return


def update(updatee):
    """Old update command
    """
    if debug == True: FileIO.log('script_keeper.update called')
    if updatee != "all":
        if updatee == "piconfigs":
            subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_configs.sh')])
            subprocess.call(["sleep", "30"])
            subprocess.call(["sudo", "reboot"])
        else:
            subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),str(updatee)])
            subprocess.call(["sleep", "30"])
            subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh')])
    else:
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),'otone_frontend'])
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),'otone_backend'])
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),'data'])
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),'central'])
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),'otone_backend'])
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/update_something.sh'),'otone_scripts'])
        #subprocess.call(['sudo','reboot'])
        subprocess.call(["sleep", "30"])
        subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh')])



proc_data = ""

def read_progress(string):
    """Read data coming back from shell scripts and process accordingly

    The data coming back follows a certain format that is not set in stone. It could be
    changed to json and the keywords are yet to be formalized.

    :todo:
    Formalize format and keywords of data returning from shell otone_scripts
    """
    if debug == True: FileIO.log('read_progress called')
    deli = "\n"
    global proc_data
    proc_data = proc_data + string
    sub_data = proc_data[:proc_data.rfind("\n")]
    proc_data = proc_data[proc_data.rfind("\n")+1:]
    list_data = [e+deli for e in sub_data.split(deli)]
    for ds in list_data:
        if ds.startswith('!ot!'):
            ds=ds[4:] #!ot!

            if ds.startswith('!pct'):
                ds=ds[4:] #!pct
                pubber.send_message('progress',ds)

            elif ds.startswith('!update'):
                ds=ds[7:] #!update
                if ds.startswith('!success'):
                    global updated
                    updated = True
                    ds=ds[8:] #!success
                    msg = ""
                    if ds.startswith('!msg'):
                        ds=ds[5:] #!msg:
                        msg = ds
                    pubber.send_message('success',msg)
                elif ds.startswith('!failure'):
                    ds=ds[8:]
                    msg = ""
                    if ds.startswith('!msg'):
                        ds=ds[5:]
                        msg = ds
                    if msg == "":
                        msg = 'failed'
                    pubber.send_message('failure',msg)

            elif ds.startswith('!share'):
                ds=ds[6:]
                if ds.startswith('!success'):
                    ds=ds[8:] #!success
                    msg = ""
                    if ds.startswith('!msg'):
                        ds=ds[5:] #!msg:
                        msg = ds
                    pubber.send_message('success',msg)
                elif ds.startswith('!failure'):
                    ds=ds[8:]
                    msg = ""
                    if ds.startswith('!msg'):
                        ds=ds[5:]
                        msg = ds
                    if msg == "":
                        msg = 'failed'
                    pubber.send_message('failure',msg)

            elif ds.startswith('!start'):
                ds=ds[6:]
                if ds.startswith('!NOCHANGE'):
                    subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh'),'NOCHANGE'])
                elif ds.startswith('!NONE'):
                    subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh'),'NONE'])
                elif ds.startswith('!AP'):
                    subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh'),'AP'])
                else:
                    subprocess.call([os.path.join(dir_path,'../../otone_scripts/start.sh'),'NOCHANGE'])
            elif ds.startswith('!reboot'):
                ds=ds[6:]
                subprocess.call(['sudo','reboot'])

#            self.proc_data = self.proc_data + data.decode()
#            deli = "\n"
#            sub_data = self.proc_data[:self.proc_data.rfind("\n")]
#            self.proc_data = self.proc_data[self.proc_data.rfind("\n")+1:]
#            list_data = [e+deli for e in sub_data.split(deli)]
#            for ds in list_data:
#                self.outer.smoothie_handler(ds,data) 






