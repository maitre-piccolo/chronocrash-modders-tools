import threading
from functools import wraps

import re

def threaded(f):
	"""
		A decorator that will make any function run in a new thread
	"""
	@wraps(f)
	def wrapper(*args, **kwargs):
		t = threading.Thread(target=f, args=args, kwargs=kwargs)
		#t = multiprocessing.Process(target = func, args = args, kwargs = kwargs)
		t.setDaemon(True)
		t.start()
		
	return wrapper


def parseInt(text):
	if type(text) == int: return text
	if text == '' or text == None : return 0
	#tmp = re.search(r'\d+', text)
	nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
	tmp = nums.search(text)
	if tmp == None : return 0
	if('.' in text) : return int(float(tmp.group()))
	return int(tmp.group())

def parseFloat(text):
	if text == '' or text == None : return 0
	#tmp = re.search(r'\d+', text)
	nums = re.compile(r"[+-]?\d+(?:\.\d+)?")
	tmp = nums.search(text)
	if tmp == None : return 0
	return float(tmp.group())
