import os
import serial

if os.name == 'nt':
    from serial.tools.list_ports_windows import comports
elif os.name == 'posix':
    from serial.tools.list_ports_posix import comports
else:
    raise ImportError("Sorry: no implementation for your platform ('{}') available".format(os.name))


class SmoothieUSBUtil(object):
    def __init__(self):
        pass

    def find_smoothie(self):
        iterator = sorted(comports())

        for n, (port, name, desc) in enumerate(iterator, 1):
            # parse the USB serial port's description string
            port_data = self.parse_port_descriptors(port, name, desc)
            # all smoothieboards have a 'name' attribute
            if port_data.get('pid')=='6015':
                return port_data

    def parse_port_descriptors(self, portname, name, desc):
        result = {
            'portname' : portname,
            'name' : name
        }
        if desc:
            # split the description by the spaces
            desc = desc.split()
            for d in desc:
                # if a portion of the description has a '=', we use it
                tlist = d.split('=')
                if len(tlist)==2:
                    # split by ':' incase its the 'VID:PID=1D50:6015' portion
                    keys = [tlist[0]] if ':' not in tlist[0] else tlist[0].split(':')
                    vals = [tlist[1]] if ':' not in tlist[1] else tlist[1].split(':')
                    for i in range(len(keys)):
                        if i<len(vals):
                            # save the key and value pair to this port's descriptor
                            tkey = keys[i].lower()
                            result[tkey] = vals[i]
        return result


if __name__ == '__main__':
    su = SmoothieUSBUtil()

    iterator = sorted(comports())
    for n, (port, name, desc) in enumerate(iterator, 1):
        print('port descriptions:\n\n\t',su.parse_port_descriptors(port, name, desc))

    print('\n'*4)
    print('find_smoothie:',su.find_smoothie())

    

