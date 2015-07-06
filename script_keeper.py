#!/usr/bin/python3

import subprocess, collections, json
from file_io import FileIO


def wifi_mode(data):
    if data and len(data):
        if str(data['mode'])=='AP':
            subprocess.call(['/home/pi/otone_scripts/change_wifi_connection_mode.sh', str(data['mode'])])
        if str(data['mode'])=='WIFI':
            subprocess.call(['/home/pi/otone_scripts/change_wifi_connection_mode.sh', str(data['mode']),str(data['ssid']),str(data['pswd'])])


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
    FileIO.log('eth_ip data: ',json.dumps(return_dict,sort_keys=True,indent=4,separators=(',',': ')))
    return return_dict

def write_led(num, val):
    subprocess.call(['/home/pi/otone_scripts/write_led.sh',str(num),str(val)])

def set_connection_status(num):
    subprocess.call(['/home/pi/otone_scripts/set_ot_config_connection_status.sh',str(num)])

def poweroff():
    subprocess.call(['poweroff'])

def reboot():
    subprocess.call(['sudo', 'reboot'])