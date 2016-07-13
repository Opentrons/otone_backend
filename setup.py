# setup.py
from distutils.core import setup
import glob
import os
import sys

try:
    import py2exe
except:
    pass


if sys.argv[1] == "py2exe":
    # Add the backend dir to the sys path so that py2exe can package it
    sys.path.append(
        (os.path.dirname(__file__) or os.getcwd()) + "\\backend"
    )


packages = [
	'twisted',
	'zope.interface',
]


setup(
	console=["backend/otone_client.py"],
	data_files=[
		('data', glob.glob('backend\\data\\*')),
        ("Microsoft.VC90.CRT", glob.glob("msvcm90\*.*")),
        ("", ["C:\\Windows\\System32\\msvcr100.dll"])
	],
	options={
		'py2exe': {
			'packages': packages,
			'includes': [],
			'excludes': ["six.moves.urllib.parse"]
		}
	}
)
