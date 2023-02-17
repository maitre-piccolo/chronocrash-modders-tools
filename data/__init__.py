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
		# this block will add space before comment if it is not set (correct malpractice)
		for i in range(len(self.parts)):
			
			if((not self.parts[i].startswith('#')) and ('#' in self.parts[i])):
				print(' *** START *** ')
				print(self.parts)
				sec_parts = self.parts[i].split('#')
				del self.parts[i]
				self.parts.insert(i, sec_parts[0])
				self.parts.insert(i+1, sec_parts[1])
				print(' *** NEW *** ')
				print(self.parts)
				break
		self.pos = -1
		
	def __len__(self):
		return len(self.parts)
		
	def current(self):
		return self.parts[self.pos]
	
	def getCurrent(self):
		return self.current()
		
		
	def get(self, i):
		return self.parts[i]
		
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
	
	def getIndent(self):
		pos = 0
		txt = ''
		while pos < len(self):
			el = self.get(pos)
			if(isSpace(el)):
				txt+= el
			else:
				break
			pos+=1
		return txt
		
	
	def getNumberOfParts(self):
		i = 0
		count = 0
		
		while i < len(self.parts):
			if self.parts[i].startswith('#'):
				return count
			if not isSpace(self.parts[i]):
				count += 1
			i+=1
		return count
		
		
	def reset(self):
		self.pos = -1
		
		
class ParsedLineMask(ParsedLine):
	def __init__(self, inputLine):
		self.line = inputLine

		self.parts = re.split('(\s)', inputLine)
		
		self.parts2 = re.split('{', inputLine)
		self.identifier = self.parts2[0].lstrip()
		
		self.pos = -1
	
	
	def next(self):
		
		self.pos += 1
		
		while self.pos < len(self.parts) and isSpace(self.parts[self.pos]):
			self.pos += 1
			
		if self.pos >= len(self.parts):
			return None
		
		return self.current()
		
	
	
class BBox:
	
	FIELDS = ['bbox.position.x', 'bbox.position.y', 'bbox.size.x', 'bbox.size.y', 'bbox.size.z.background', 'bbox.size.z.foreground']
	
	
	def __init__(self, params=None):
		self.x = 0
		self.y = 0
		self.width = 0
		self.height = 0
		self.z1 = 0
		self.z2 = 0
		
		self.delete = False # Flag used to not process when rebuilding text
		
		self.ogLine = None
		self.ogLineX = None
		self.ogLineWidth = None
		self.ogLineHeight = None
		self.ogLineZ1 = None
		self.ogLineZ2 = None
		
		if params is not None:
			if(isinstance(params, ParsedLine)):
				self.ogLine = params
				params = []
				while(self.ogLine.next() != None):
					params.append(parseInt(self.ogLine.current()))
				while len(params) < 4:
					params.append(0)
				# x, y, w, h
			self.x, self.y, self.width, self.height = params[0:4]
			try:
				self.z1 = params[4]
			except:
				pass
				
			try:
				self.z2 = params[5]
			except:
				pass
			
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
			if(self.ogLine == None): # create new line
				return '\tbbox ' + ' '.join(map(str, self.getParams())) 
				
			else: # recreate from original line, keeping indentation, spaces, tabs, etc
			
				params = self.getParams()
				pos = 0 # includes both values and spaces
				indexVal = -1 # only for values (not spaces)
				recreatedLine = ''
				while pos < len(self.ogLine) and indexVal < len(params):
					el = self.ogLine.get(pos)
					#print("elt", el)
					pos += 1
					if(isSpace(el)):
						recreatedLine += el
					elif (el is not None):
						if(indexVal == -1):
							recreatedLine += 'bbox'
						else:
							#print(indexVal)
							recreatedLine += str(params[indexVal])
						indexVal += 1
				while(indexVal < len(params)): # params that were not present in ogLine, typically z1 and z2
					recreatedLine += ' ' + str(params[indexVal])
					indexVal += 1
					
				return recreatedLine
				
		else:
			if(self.ogLineX == None): # create new lines
				data = ['\tbbox.position.x ' + str(self.x), '\tbbox.position.y ' + str(self.y),
				'\tbbox.size.x ' + str(self.width), '\tbbox.size.y ' + str(self.height)]
				if self.z1 != 0:
					data.append('\tbbox.size.z.background ' + str(self.z1))
				if self.z2 != 0:
					data.append('\tbbox.size.z.foreground ' + str(self.z2))
				return '\n'.join(data)
				
			else: # recreate from original lines, keeping indentation, spaces, tabs, etc
				lines = []
				params = self.getParams()
				i = 0
				numberOfParamsProcessed = 0
				for ogLine in [self.ogLineX, self.ogLineY, self.ogLineWidth, self.ogLineHeight, self.ogLineZ1, self.ogLineZ2]:
					if ogLine is None:
						i+=1
						continue
						
					
					pos = 0 # includes both values and spaces
					indexVal = -1 # only for values (not spaces)
					recreatedLine = ''
					while pos < len(ogLine):
						el = ogLine.get(pos)
						#print("elt", el)
						pos += 1
						if(isSpace(el)):
							recreatedLine += el
						elif (el is not None):
							if(indexVal == -1):
								recreatedLine += el # this is the "command" (e.g., bbox.position.x)
							else:
								#print(indexVal)
								recreatedLine += str(params[i])
								numberOfParamsProcessed +=1
							indexVal += 1
							
					lines.append(recreatedLine)
					i+=1
					
				while(numberOfParamsProcessed < len(params)): # params that were not present in ogLine, typically z1 and z2
					recreatedLine = '\t' + BBox.FIELDS[numberOfParamsProcessed] + " " + str(params[numberOfParamsProcessed])
					lines.append(recreatedLine)
					numberOfParamsProcessed+=1
					
				return '\n'.join(lines)
					
		
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
		
		
		self.ogLine = None
		self.ogLines = {}
		
		
		
		self.data['block.penetrate'] = None
		
		self.data['effect.hit.flash.disable'] = None
		self.data['effect.hit.flash.sound'] = None
		self.data['effect.hit.flash.model'] = None
		
		self.data['reaction.fall.velocity.x'] = None
		self.data['reaction.fall.velocity.y'] = None
		self.data['reaction.fall.velocity.z'] = None
		
		self.originalNumbersofParams = 0
		
		
		if params is not None:
			self.originalNumbersofParams = len(params)
			
			command = params[0]
			if(command.startswith('attack')):
				self.data['damage.type'] = params[0][6:] # strip attack#
				if self.data['damage.type'] is None or self.data['damage.type'] == '' : self.data['damage.type'] = '1'
			else:
				self.data['damage.type'] = command
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
			if(self.ogLine == None): # create new line
				params = self.getParams()
				if params[0] is None:
					params[0] = ''
				data = ['\tattack' + ' '.join(map(str, params))]
				
				
				
				
				
				
			else:  # recreate from original lines, keeping indentation, spaces, tabs, etc
				params = self.getParams()[1:]
				#if params[0] is None:
					#params[0] = ''
				pos = 0 # includes both values and spaces
				indexVal = -1 # only for values (not spaces)
				recreatedLine = ''
				while pos < len(self.ogLine):
					el = self.ogLine.get(pos)
					#print("elt", el)
					pos += 1
					if(isSpace(el)):
						recreatedLine += el
					elif (el is not None):
						if(indexVal == -1):
							recreatedLine += el # this is the "command" (e.g., bbox.position.x)
						else:
							#print(indexVal)
							recreatedLine += str(params[indexVal])
						indexVal += 1
				print('recreated line', recreatedLine)
				data = [recreatedLine,]
			
			dropvLine = None
			if self.data['reaction.fall.velocity.y'] != None:
				dropvLine = '\tdropv ' + str(self.data['reaction.fall.velocity.y'])
			if self.data['reaction.fall.velocity.x'] != None:
				dropvLine += ' ' + str(self.data['reaction.fall.velocity.x'])
			if self.data['reaction.fall.velocity.z'] != None:
				dropvLine += ' ' + str(self.data['reaction.fall.velocity.z'])
				
			if dropvLine is not None : data.append(dropvLine)
			
			return '\n'.join(data)
			
			
		else: # *** NON-LEGACY ***
			
			if(len(self.ogLines) == 0): # create new lines
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
					
			else : # recreate from original lines, keeping indentation, spaces, tabs, etc
				lines = []
				
				i = 0
				for key, value in sorted(self.data.items()):
					if(value is None) : continue
					
					ogLine = None
					if(key in self.ogLines):
						ogLine = self.ogLines[key]
					if ogLine is None: # create from value
						if value != None:
							lines.append('\tattack.' + key + ' ' + str(value))
						i+=1
						continue
						
						
					
					pos = 0 # includes both values and spaces
					indexVal = -1 # only for values (not spaces)
					recreatedLine = ''
					while pos < len(ogLine):
						el = ogLine.get(pos)
						#print("elt", el)
						pos += 1
						if(isSpace(el)):
							recreatedLine += el
						elif (el is not None):
							if(indexVal == -1):
								recreatedLine += el # this is the "command" (e.g., bbox.position.x)
							else:
								#print(indexVal)
								recreatedLine += str(value)
							indexVal += 1
							
					lines.append(recreatedLine)
					i+=1
				return '\n'.join(lines)
				
			
		
	
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



class BindData:
	def __init__(self, maskPLine=None, pLine=None):
		self.data = {}
		self.data['mode'] = 0
		self.data['ent'] = 0
		self.data['index'] = 0
		self.data['x'] = 0
		self.data['y'] = 0
		self.data['z'] = 0
		self.data['direction'] = 0
		self.data['frame'] = 0
		self.data['state'] = 0
		self.type = type
		
		self.indent = ''
		
		keys = ['x', 'y', 'z', 'direction', 'frame']
		
		if(maskPLine is None or pLine is None): return
	
		if(pLine != None): self.indent = pLine.getIndent()
		
		translations = dict(settings.get_option('entity/binding_additional_translations', {}))
		
		maskPLine.reset()
		pLine.reset()
		
		while maskPLine.next() != None:
			
			
			
			partMask = maskPLine.current()
			part = pLine.next()
			for key in keys:
			
				if partMask == '{' + key + '}':
					print(key, part)
					try:
						self.data[key] = int(part) # WARNING maybe won't all be int in the future
					except:
						self.data[key] = part
					if(key in translations):
						subTranslations = translations[key]
						if(part in subTranslations):
							self.data[key] = subTranslations[part]
					# now we force int
					try:
						self.data[key] = int(self.data[key])
					except:
						self.data[key] = 0
				
			
	def __getitem__(self, item):
		return self.data[item]
		
	def __setitem__(self, item, value):
		self.data[item] = value
		
	def __contains__(self, key):
		return key in self.data
		
		
	def getFrame(self, frame):
		try:
			return int(frame)
		except:
			return frame
				
	def getText(self, pLine=None):
		if(pLine == None): return ''
		# pLine.reset()
		text = pLine.line # mask model
		
		
		translations = settings.get_option('entity/binding_additional_translations', {})
		
		keys = ['x', 'y', 'z', 'direction', 'frame']
		
		
		print('model', text)
		
		for key in keys:
			value = self.data[key]
			if key in translations:
				subTranslations = translations[key]
				subTranslations_inv = {v: k for k, v in subTranslations.items()}
				
				# print('check', value, 'in', subTranslations_inv)
				if value in subTranslations_inv:
					value = subTranslations_inv[value]
				
			text = text.replace('{' + key + '}', str(value))

		return text
		# return self.indent + text
		


class FileWrapper:
	def __init__(self, path):
		self.path = path
		
	def getLines(self):
		f = open(self.path)
		try:
			lines = f.read().split('\n')
		except:
			f.close()
			import chardet    
			# rawdata = open(infile, 'rb').read()
			# result = chardet.detect(rawdata)
			# charenc = result['encoding']
			charenc = chardet.detect(open(self.path, 'rb').read())['encoding']
			f = open(self.path, encoding=charenc)
			lines = f.read().split('\n')
		f.close()
		
		return lines
		

class Cache:
	def __init__(self, type, path):
		cacheID = path.replace('/', '-')
		cacheID = cacheID.replace("\\", '-')
		cacheID = cacheID.replace(":", '')
		
		self.fullID = 'cache/' + type + '_' + cacheID
		
		self.data = settings.get_option(self.fullID, {})
		
	def save(self):
		settings.set_option(self.fullID, self.data)
