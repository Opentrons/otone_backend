# setup.py
import glob
from distutils.core import setup
import py2exe
import os


import sys

sys.path.append(os.path.dirname(__file__) + "\\backend")
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
