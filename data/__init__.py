def isSpace(part):
	if part in ['', ' ', '\t']:
		return True
	return False



import os, re, time
from common.util import parseInt, parseFloat
from common import settings

class ParsedLine:
	def __init__(self, inputLine):
		self.line = inputLine
		self.parts = re.split('(\s)', inputLine)
		self.pos = -1
		
	def __len__(self):
		return len(self.parts)
		
	def current(self):
		return self.parts[self.pos]
	
	def getCurrent(self):
		return self.current()
		
	def next(self):
		
		self.pos += 1
		
		while self.pos < len(self.parts) and isSpace(self.parts[self.pos]):
			self.pos += 1
			
		if self.pos >= len(self.parts) or self.current().startswith('#'):
			return None
		
		return self.current()
	

	def set(self, val):
		self.parts[self.pos] = val
		
	def getText(self):
		return ''.join(map(str, self.parts))
	
	def getCom(self):
		if '#' in self.line:
			return self.line.split('#')[-1]
		return ''
	
	
class BBox:
	def __init__(self, params=None):
		self.x = 0
		self.y = 0
		self.width = 0
		self.height = 0
		self.z1 = 0
		self.z2 = 0
		
		self.delete = False # Flag used to not process when rebuilding text
		
		if params is not None:
			self.x, self.y, self.width, self.height = params[0:4]
			
	def getParams(self):
		data = [self.x, self.y, self.width, self.height]
		if self.z1 != 0:
			data.append(self.z1)
		if self.z2 != 0:
			data.append(self.z2)
		return data
	
	def getText(self):
		legacy = settings.get_option('misc/legacy_commands', False)
		if legacy:
			return '\tbbox ' + ' '.join(map(str, self.getParams())) 
		else:
			data = ['\tbbox.position.x ' + str(self.x), '\tbbox.position.y ' + str(self.y),
			'\tbbox.size.x ' + str(self.width), '\tbbox.size.y ' + str(self.height)]
			if self.z1 != 0:
				data.append('\tbbox.size.z.1 ' + str(self.z1))
			if self.z2 != 0:
				data.append('\tbbox.size.z.2 ' + str(self.z2))
			return '\n'.join(data)
		
		
class AttackBox:
	def __init__(self, params=None):
		self.data = {}
		self.data['position.x'] = 0
		self.data['position.y'] = 0
		self.data['size.x'] = 0
		self.data['size.y'] = 0

		self.data['damage.force'] = 0
		#self.data['damage.type'] = 1
		self.data['damage.type'] = None
		self.data['reaction.fall.force'] = None

		self.data['reaction.pause.time'] = None

		self.data['size.z.1'] = None
		self.data['size.z.2'] = None
		
	
		self.delete = False # Flag used to not process when rebuilding text
		

		
		
		
		self.data['block.penetrate'] = None
		
		self.data['effect.hit.flash.disable'] = None
		self.data['effect.hit.flash.sound'] = None
		self.data['effect.hit.flash.model'] = None
		
		self.data['reaction.fall.velocity.x'] = None
		self.data['reaction.fall.velocity.y'] = None
		self.data['reaction.fall.velocity.z'] = None
		
		
		if params is not None:
			self.data['damage.type'] = params[0][6:] # strip attack#
			if self.data['damage.type'] is None or self.data['damage.type'] == '' : self.data['damage.type'] = '1'
			params = params[1:]
			if(len(params) < 11): params.append(None)
			self.data['position.x'], self.data['position.y'], self.data['size.x'], self.data['size.y'], self.data['damage.force'], self.data['reaction.fall.force'], self.data['block.penetrate'], self.data['effect.hit.flash.disable'], self.data['reaction.pause.time'], self.data['size.z.1'], self.data['size.z.2'] = params
			
		
			
	def getParams(self):
		data = [self.data['damage.type'], self.data['position.x'], self.data['position.y'], self.data['size.x'], self.data['size.y'], self.data['damage.force'], parseInt(self.data['reaction.fall.force']), parseInt(self.data['block.penetrate']), parseInt(self.data['effect.hit.flash.disable']), parseInt(self.data['reaction.pause.time'])]
		#if self.z1 != 0:
		data.append(parseInt(self.data['size.z.1']))
		if self.data['size.z.2'] != None:
			data.append(self.data['size.z.2'])
		return data
	
	def getText(self, legacy=False):
		legacy = settings.get_option('misc/legacy_commands', False)
		if legacy:
			params = self.getParams()
			if params[0] is None:
				params[0] = ''
			data = ['\tattack' + ' '.join(map(str, params))]
			
			dropvLine = None
			if self.data['reaction.fall.velocity.y'] != None:
				dropvLine = '\tdropv ' + str(self.data['reaction.fall.velocity.y'])
			if self.data['reaction.fall.velocity.x'] != None:
				dropvLine += ' ' + str(self.data['reaction.fall.velocity.x'])
			if self.data['reaction.fall.velocity.z'] != None:
				dropvLine += ' ' + str(self.data['reaction.fall.velocity.z'])
				
			if dropvLine is not None : data.append(dropvLine)
		
		else:
			data = []
			for key, value in sorted(self.data.items()):
				#if value != None and value != 0:
				if value != None:
					data.append('\tattack.' + key + ' ' + str(value))
		
			#data = ['\tattack.position.x ' + str(self.x), '\tattack.position.y ' + str(self.y),
			#'\tattack.size.x ' + str(self.width), '\tattack.size.y ' + str(self.height),
			#'\tattack.damage.force  ' + str(self.damage), '\tattack.reaction.fall.force  ' + str(self.fallForce),
			#'\tattack.block.penetrate  ' + str(self.blockPenetrate), '\tattack.effect.hit.flash.disable  ' + str(self.hitFlashDisable),
			#'\tattack.reaction.pause.time  ' + str(self.pauseTime)
			#]
			#if self.z1 != 0:
				#data.append('\tattack.size.z.1 ' + str(self.z1))
			#if self.z2 != 0:
				#data.append('\tattack.size.z.2 ' + str(self.z2))
				
			#if self.fallX != None:
				#data.append('\tattack.reaction.fall.velocity.x ' + str(self.fallX))
			#if self.fallY != None:
				#data.append('\tattack.reaction.fall.velocity.y ' + str(self.fallY))
			#if self.data['reaction.fall.velocity.z'] != None:
				#data.append('\tattack.reaction.fall.velocity.z ' + str(self.fallZ))
			
		return '\n'.join(data)
	
	def loadLegacy(self, command, data):
		if command == 'dropv':
			try:
				self.data['reaction.fall.velocity.y'] = data[0]
				self.data['reaction.fall.velocity.x'] = data[1]
				self.data['reaction.fall.velocity.z'] = data[2]
			except IndexError:
				pass
		if command == 'hitfx':
			try:
				self.data['effect.hit.sound.path'] = data[0]
			except IndexError:
				pass
		if command == 'hitflash':
			try:
				self.data['effect.hit.flash.model'] = data[0]
			except IndexError:
				pass
