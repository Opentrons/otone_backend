# setup.py
from distutils.core import setup
import glob
import os
import sys

try:
    import py2exe
except:
    pass


script_tag = '[otone_backend build] '


# Add the backend dir to the sys path so that py2exe can package it
sys.path.append(
    (os.path.dirname(__file__) or os.getcwd()) + "\\backend"
)


def get_py2exe_packages():
    return ['twisted','zope.interface']

def build_exe(args=None):
    try:
	setup(
	    console=["backend/otone_client.py"],
	    data_files=[
		('data', glob.glob('backend\\data\\*')),
		("Microsoft.VC90.CRT", glob.glob("msvcm90\*.*")),
		("", ["C:\\Windows\\System32\\msvcr100.dll"])
	    ],
	    options={
		'py2exe': {
		    'packages': get_py2exe_packages(),
		    'includes': [],
		    'excludes': ["six.moves.urllib.parse"]
		}
	    },
	    script_args=args
	)
    except:
	print('failed but moving on..')

def main():
    print(script_tag + "Building otone_backend using py2exe.")
    if len(sys.argv) <= 1:
        build_exe(["py2exe"])
    else:
        build_exe()


if __name__ == '__main__':
    main()
