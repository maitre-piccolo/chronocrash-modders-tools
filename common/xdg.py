import os, sys
#import glib

#config_home = glib.get_user_config_dir()
#config_home = os.path.join(config_home, APPNAME)

#data_home = glib.get_user_data_dir()

#data_home = os.path.join(data_home, APPNAME)

#data_thumbnails = os.path.join(data_home, 'thumbnails')

#data_dir = '~/workspace/bullseye/trunk/'
#data_dir = os.path.dirname(os.path.dirname(__file__)) + os.sep
APPNAME = 'ob-utils'

home = os.environ.get("XDG_HOME", os.path.expanduser("~"))
#print(sys.platform)
if sys.platform == "linux2" or sys.platform == 'linux': # for Linux using the X Server
	config_home = os.path.join(os.environ.get("XDG_CONFIG_HOME", os.path.join(home, ".config")), APPNAME)
	data_home = os.path.join(os.environ.get("XDG_DATA_HOME", os.path.join(home, ".local", "share")), APPNAME)
elif sys.platform == "win32": # for Windows
	home = os.environ.get("USERPROFILE", os.path.expanduser("~"))
	#config_home = os.path.join(home, ".bullseye")
	#data_home = os.path.join(home, ".bullseye")
	config_home = os.path.join(home, APPNAME)
	config_home = data_home = os.path.join(os.environ.get("APPDATA", "Application Data"), APPNAME)
elif sys.platform == "darwin": # for MacOS
	config_home = os.path.join(home, APPNAME)


data_thumbnails = os.path.join(data_home, 'thumbnails')

data_dir = os.path.dirname(os.path.dirname(__file__)) + os.sep
if sys.platform == "win32":
	data_dir = os.path.dirname(os.path.dirname(data_dir)) + os.sep

def get_home_dir():
	return home

def get_data_dir():
	return data_dir

def get_data_home():
	return data_home

def get_config_dir():
	return config_home

def get_thumbnail_dir(subdir):
	dir = os.path.join(data_thumbnails, subdir)
	return dir


def make_missing_dirs():
	"""

	"""
	dirs = (config_home, data_home, os.path.join(data_home, 'sessions'), os.path.join(data_home, 'images'))
	for dir in dirs:
		if not os.path.exists(dir):
			os.makedirs(dir)


make_missing_dirs()
