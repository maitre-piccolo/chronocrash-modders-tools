# -*- coding: utf-8 -*-
# Inspired by Exaile :)
from configparser import (
    RawConfigParser,
    NoSectionError,
    NoOptionError
)
from common import xdg
import os
import logging
import threading

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


TYPE_MAPPING = {
    'I': int,
    'S': str,
    'F': float,
    'B': bool,
    'L': list,
    'D': dict
}

MANAGER = None


class SettingsManager(RawConfigParser):
	"""
		@attr dirty : tells if there is change that are not written on disk
		@attr saving : tells if there is a write-access opened
	"""
	
	VERSION = 0.1
	
	def __init__(self, location=None):
		RawConfigParser.__init__(self)
		self.location = location
		self._saving = False
		self._dirty = False

		if location is not None:
			try:
				self.read(self.location) or \
				self.read(self.location + ".new") or \
				self.read(self.location + ".old")
			except:
				pass
			
		#self.saveTimer = threading.Timer(180, self._timeout_save)
		#self.saveTimer.start()
		#if location is not None:
			#glib.timeout_add_seconds(180, self._timeout_save)
	
	
	def _timeout_save(self):
		logger.debug("Requesting save from timeout...")
			
		self.save()
		
		self.saveTimer = threading.Timer(180, self._timeout_save)
		self.saveTimer.start()
	
		return True
		
	def set_option(self, option, value):
		"""
		Set an option (in section/key syntax) to the specified value.

		:param option: the full path to an option
		:type option: string
		:param value: the value the option should be assigned
		"""
		value = self._val_to_str(value)
		splitvals = option.split('/')
		section, key = "/".join(splitvals[:-1]), splitvals[-1]

		try:
			self.set(section, key, value)
		except NoSectionError:
			self.add_section(section)
			self.set(section, key, value)

		self._dirty = True

		section = section.replace('/', '_')

		#event.log_event('option_set', self, option)
		#event.log_event('%s_option_set' % section, self, option)

	def get_option(self, option, default=None):
		"""
		Get the value of an option (in section/key syntax), returning
		default if the key does not exist yet.

		:returns: the option value or default
		:rtype: any
		"""
		splitvals = option.split('/')
		section, key = "/".join(splitvals[:-1]), splitvals[-1]

		try:
			value = self.get(section, key)
			value = self._str_to_val(value)
		except NoSectionError:
			value = default
		except NoOptionError:
			value = default

		return value
		
	
	def save(self):
		"""
		Save the settings to disk
		"""
		
		if self.location is None:
			logger.debug("Save requested but not saving settings, location is None")
			return
		
		if self._saving or not self._dirty:
			return

		self._saving = True
		
		self.set_option('general/version', self.VERSION)

		logger.debug("Saving settings...")

		with open(self.location + ".new", 'w') as f:
			self.write(f)

			try:
				# make it readable by current user only, to protect private data
				os.fchmod(f.fileno(), 384)
			except:
				pass # fail gracefully, eg if on windows

			f.flush()

		try:
			os.rename(self.location, self.location + ".old")
		except:
			pass # if it doesn'texist we don't care

		os.rename(self.location + ".new", self.location)

		try:
			os.remove(self.location + ".old")
		except:
			pass

		self._saving = False
		self._dirty = False
		
		
		
		
	def _val_to_str(self, value):
		"""
		Turns a value of some type into a string so it
		can be a configuration value.
		"""
		for k, v in TYPE_MAPPING.items():
			if v == type(value):
				if v == list:
					return k + ": " + repr(value)
				else:
					return k + ": " + str(value)

		raise ValueError(_("We don't know how to store that "
			"kind of setting: "), type(value))

	def _str_to_val(self, value):
		"""
		Convert setting strings back to normal values.
		"""
		try:
			kind, value = value.split(': ', 1)
		except ValueError:
			return ''

		# Lists and dictionaries are special case
		if kind in ('L', 'D'):
			return eval(value)

		if kind in TYPE_MAPPING.keys():
			if kind == 'B':
				if value != 'True':
					return False

			value = TYPE_MAPPING[kind](value)

			return value
		else:
			raise ValueError(_("An Unknown type of setting was found!"))






MANAGER = SettingsManager(os.path.join(xdg.get_config_dir(), "settings.ini" ))

get_option = MANAGER.get_option
set_option = MANAGER.set_option