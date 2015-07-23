#!/usr/bin/python3

import subprocess, collections, json, asyncio
from file_io import FileIO

class SK:
    """SK Class
    
    the SK class is intended to be instantiated to a sk object which
    aggregates the scripts.
    """
    
#Special Methods-----------------------
    #def __init__(self, tools, global_handlers, theQueue):
    def __init__(self, global_handlers):
        """initialize SK object
        
        """
        if debug == True: FileIO.log('script_keeper.__init__ called')
        the_ghand = global_handlers
        

    def __str__(self):
        return "SK"



def wifi_mode(data):
    if data and len(data):
        if str(data['mode'])=='AP':
            subprocess.call(['/home/pi/otone_scripts/change_wifi_connection_mode.sh', str(data['mode'])])
        if str(data['mode'])=='WIFI':
            subprocess.call(['/home/pi/otone_scripts/change_wifi_connection_mode.sh', str(data['mode']),str(data['ssid']),str(data['pswd'])])
        if str(data['mode'])=='NONE':
            subprocess.call(['/home/pi/otone_scripts/change_wifi_connection_mode.sh', str(data['mode'])])

def wifi_scan(data):
    return_dict = collections.OrderedDict({
        'type':'networks','data':subprocess.check_output("/home/pi/otone_scripts/list_wicd_networks.sh", shell=True, universal_newlines=True).splitlines()
    })
    FileIO.log('wifi_scan data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def change_hostname(data):
    if data and len(data):
        subprocess.call(['sudo','/home/pi/otone_scripts/set_hostname.sh',str(data)])
	
def get_wifi_ip_address():
    return_dict = collections.OrderedDict({
        'type': 'wifi_ip','data':subprocess.check_output("/home/pi/otone_scripts/get_ifconfig_wlan0_ip.sh", shell=True, universal_newlines=True).replace('\n','')
    })
    FileIO.log('wifi_ip data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def get_eth_ip_address():
    return_dict = collections.OrderedDict({
        'type':'eth_ip','data':subprocess.check_output("/home/pi/otone_scripts/get_ifconfig_eth0_ip.sh", shell=True, universal_newlines=True).replace('\n','')
    })
    FileIO.log('eth_ip data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def get_iwconfig_essid():
    return_dict = collections.OrderedDict({
        'type':'wifi_essid','data':subprocess.check_output("/home/pi/otone_scripts/get_iwconfig_essid.sh", shell=True, universal_newlines=True).replace('\n','')
    })
    FileIO.log('wifi_essid data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def write_led(num, val):
    subprocess.call(['/home/pi/otone_scripts/write_led.sh',str(num),str(val)])

def set_connection_status(num):
    subprocess.call(['/home/pi/otone_scripts/set_ot_config_connection_status.sh',str(num)])

def poweroff():
    subprocess.call(['sudo','poweroff'])

def reboot():
    subprocess.call(['sudo', 'reboot'])


def connection():
    return_dict = collections.OrderedDict({
        'type':'internet','data':subprocess.check_output("/home/pi/otone_scripts/connection.sh", shell=True, universal_newlines=True).replace('\n','')
    })
    FileIO.log('internet: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def share_inet():
    subprocess.call(['sudo','ifdown','eth0'])
    subprocess.call(['sudo','ifup','eth0'])

@asyncio.coroutine
def per_data():
    create_internet = asyncio.create_subprocess_exec('/home/pi/otone_scripts/connection.sh',stdout=asyncio.subprocess.PIPE)
    create_wifi_ip = asyncio.create_subprocess_exec('/home/pi/otone_scripts/get_ifconfig_wlan0_ip.sh',stdout=asyncio.subprocess.PIPE)
    create_eth_ip = asyncio.create_subprocess_exec('/home/pi/otone_scripts/get_ifconfig_eth0_ip.sh',stdout=asyncio.subprocess.PIPE)
    create_wifi_essid = asyncio.create_subprocess_exec('/home/pi/otone_scripts/get_iwconfig_essid.sh',stdout=asyncio.subprocess.PIPE)
    
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
def cool_update(data):
    cmd = '/home/pi/otone_scripts/update_something.sh'
    create_update = asyncio.create_subprocess_exec(cmd,str(data),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
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


def update(updatee):
    if updatee != "all":
        if updatee == "piconfigs":
            subprocess.call(['/home/pi/otone_scripts/update_configs.sh'])
            subprocess.call(["sleep", "30"])
            subprocess.call(["sudo", "reboot"])
        else:
            subprocess.call(['/home/pi/otone_scripts/update_something.sh',str(updatee)])
            subprocess.call(["sleep", "30"])
            subprocess.call(['/home/pi/otone_scripts/start.sh'])
    else:
        subprocess.call(['/home/pi/otone_scripts/update_something.sh','frontend'])
        subprocess.call(['/home/pi/otone_scripts/update_something.sh','backend'])
        subprocess.call(['/home/pi/otone_scripts/update_something.sh','data'])
        subprocess.call(['/home/pi/otone_scripts/update_something.sh','central'])
        subprocess.call(['/home/pi/otone_scripts/update_something.sh','backend'])
        subprocess.call(['/home/pi/otone_scripts/update_something.sh','scripts'])
        #subprocess.call(['sudo','reboot'])
        subprocess.call(["sleep", "30"])
        subprocess.call(['/home/pi/otone_scripts/start.sh'])



def read_progress(string):
    if string.startswith('!ot!'):
        the_ghand.send('progress',string)






