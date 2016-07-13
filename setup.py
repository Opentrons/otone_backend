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

    # Create __init__.py file in the top level zope dir so py2exe can import it
    # http://stackoverflow.com/questions/7816799
    import zope
    open(
        os.path.join(zope.__path__[0], '__init__.py'), 'a'
    ).close()


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
			'includes': [],
			'excludes': ["six.moves.urllib.parse"]
		}
	}
)
