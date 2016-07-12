# setup.py
from distutils.core import setup
import glob
import os
import sys

import py2exe

sys.path.append(
	(os.path.dirname(__file__) or os.getcwd()) + "\\backend"
)

print(sys.path)
includes = [
	'head',
]

packages = [
	'twisted',
	'zope.interface',
]
setup(
	console=["backend/otone_client.py"],
	data_files=[
		('data', glob.glob('backend\\data\\*'))
	],
	options={
		'py2exe': {
			'packages': packages,
			'includes': includes,
			'excludes': ["six.moves.urllib.parse"]
		}
	}
)
