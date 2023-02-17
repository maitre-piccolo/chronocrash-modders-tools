import os, re, time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from common import util
from common import settings
from gui.util import FileInput, loadSprite

from gui.portrait import IconViewer, Portrait

from qutepart import Qutepart, EverydayPart

from data import ParsedLine, ParsedLineMask, BBox, AttackBox, Cache, BindData
from common.util import parseInt, parseFloat


from gui.entity.animselector import AnimSelector
from gui.entity.frameproperties import FramePropertiesEditor, BindingEditor

from gui.level.items import Wall, Entity





def convertRect(x, y, x2, y2):
	xStart = x
	xEnd = x2
	yStart = y
	yEnd = y2
	if x2 < x:
		xStart = x2
		xEnd = x
		
	if y2 < y:
		yStart = y2
		yEnd = y
	
	return xStart, yStart, xEnd, yEnd


class Platform:
	def __init__(self, data=[]):
		if(len(data) == 0):
			data = [100,100, -50,-50,50,50, 30,30]
		while len(data) < 8:
			data.append(0)
		self.data = data
		self.wall = None
		
	def getWall(self, xOffset=0, yOffset=0):
		data = list(self.data)
		data[0] -= xOffset
		data[1] -= yOffset
		self.xOffset = xOffset
		self.yOffset = yOffset
		self.wall = Wall(self, *data)
		#self.wall.updated.connect(self.platformUpdated)
		return self.wall
		
	def getParams(self):
		return self.data
		
	def getText(self):
		return 'platform ' + ' '.join(map(str, map(int, self.data)))
	
	def platformUpdated(self):
		self.data = list(self.wall.getParams())
		self.data[0] += self.xOffset
		self.data[1] += self.yOffset
		print(self.data)
	
	
class Anim:
	def __init__(self, frames):
		self.frames = frames
		
	def __getitem__(self, key):
		 return self.frames[key]
	 
	def __len__(self):
		 return len(self.frames)
	 
	 
	def getDrawMethod(self, frameNumber, prop):
		val = None
		if prop in ('scalex', 'scaley'):
			val = 1
			
		if prop in ('flipx', 'flipy'):
			val = 0
		
		i = frameNumber
		while i > 0 and 'drawmethod_' + prop not in self.frames[i]:
			i-=1
		
		if 'drawmethod_' + prop in self.frames[i]: 
			rawVal = self.frames[i]['drawmethod_' + prop]
			if rawVal != None : val = rawVal
			
		if prop in ('scalex', 'scaley'):
			return float(val)
		elif prop in ('flipx', 'flipy'):
			return int(val)
		else:
			return val
		
	def getPlatform(self, frameNumber=None):
		if frameNumber is None:
			frameNumber = self.currentFrame
		platform = Platform()
		
		i = frameNumber
		while i > 0 and 'platform' not in self.frames[i]:
			i-=1
		
		if 'platform' in self.frames[i]:
			platform = self.frames[i]['platform']
			
		return platform


	
		
		
	def getBBox(self, frameNumber):
		bbox = BBox()
		#x, y, w, h, z = None, None, None, None, None
		i = frameNumber
		while i > 0 and 'bbox' not in self.frames[i]:
			i-=1
		
		if 'bbox' in self.frames[i]:
			bbox = self.frames[i]['bbox']
			#x, y, w, h = self.frames[i]['bbox'][0:4]
			#if len(self.frames[i]['bbox']) == 5:
				#z = self.frames[i]['bbox'][4]
		return bbox
		#return x, y, w, h, z
		
		
	def getOffset(self, frameNumber):
		xOffset, yOffset = -1, -1
		i = frameNumber
		while i > 0 and 'offset' not in self.frames[i]:
			i-=1
		if 'offset' in self.frames[i]:
			xOffset, yOffset = self.frames[i]['offset']
			
		return xOffset, yOffset
	
	
	def getRange(self, frameNumber):
		xMin, xMax = None, None
		i = frameNumber
		while i > 0 and 'range' not in self.frames[i]:
			i-=1
		if 'range' in self.frames[i]:
			xMin, xMax = self.frames[i]['range']
		return xMin, xMax
	


		
class EntityEditorWidget(QtWidgets.QWidget):
	
	try:
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', '/home/piccolo/workspace/OpenBOR/data')) + os.sep
	except AttributeError:
		print("FATAL ERROR")
	
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)
		
		self.mainSplitter = QtWidgets.QSplitter()
		self.mainSplitter.setContentsMargins(0, 0, 0, 0)
		layout.addWidget(self.mainSplitter)
		
		self.animSelector = AnimSelector(self)
		
		
		self.frames = []
		self.currentFrame = 0
		self.anim = Anim(self.frames)
		
		self.pixmapCache = {}
		

		#self.loadEntity('oro')

		
		#self.text = '''	hitflash Flash6
	#bbox	40 6 48 87
	#sound data/chars/oro/ohe.wav
	#delay	5
	#offset	63 92
	#frame data/chars/oro/506.gif
	#bbox	32 3 35 89
	#attack	78 11 76 25 1 0 0 0 0 0
	#delay	3
	#offset	53 91
	#frame data/chars/oro/507.gif
	#delay 5
	#attack 0
	#offset 42 91
	#frame data/chars/oro/508.gif
	#delay 3
	#offset 41 95
	#frame data/chars/oro/509.gif
	#offset 41 99
	#frame data/chars/oro/510.gif
	#offset 49 99
	#frame data/chars/oro/511.gif
	#bbox	43 11 47 92
	#offset	68 102
	#frame data/chars/oro/94.gif
	#offset 67 97
	#frame data/chars/oro/95.gif
	#offset 69 94
	#frame data/chars/oro/96.gif'''
		
		
		
		#self.editorTabWidget = QtWidgets.QTabWidget(self)
		
		
		
		
		self.frameEditor = FrameEditor(self)
		

		self.frameViewer = IconViewer(self)
		self.frameViewer.currentChange.connect(self.onFrameClick)


		
		editor = EverydayPart()
		theme = settings.get_option('gui/editor_theme', None)
		if(theme != None and 'dark' in theme.lower()):
			editor.detectSyntax(xmlFileName='entity-dark.xml')
		else:
			editor.detectSyntax(xmlFileName='entity.xml')
		self.editor = editor
		self.editor.indentUseTabs = True
		self.editor.cursorPositionChanged.connect(self.positionChanged)
		self.editor.textChanged.connect(self.notifyChange)

		
		self.editor.installEventFilter(self)
		self.frameEditor.graphicView.installEventFilter(self)
		#self.editorTabWidget.addTab(self.frameEditor, _('Visual'))
		#self.editorTabWidget.addTab(editor, _('Text'))
		
		
		rightSide = QtWidgets.QWidget()
		layout2 = QtWidgets.QVBoxLayout()
		layout2.setContentsMargins(0, 0, 0, 0)
		
		upLayout = QtWidgets.QSplitter()
		upLayout.setContentsMargins(0, 0, 0, 0)
		self.splitter = upLayout
		
		
		upLayout.addWidget(editor)
		upLayout.addWidget(self.frameEditor)
		layout2.addWidget(upLayout, 1)
		
		layout2.addWidget(self.frameViewer, 0)
		rightSide.setLayout(layout2)
		
		
		self.mainSplitter.addWidget(self.animSelector)
		self.mainSplitter.addWidget(rightSide)
		self.mainSplitter.setStretchFactor(0,0)
		self.mainSplitter.setStretchFactor(1,1)
		
		# self.mainSplitter.splitterMoved.connect(self.mainSplitterMoved)
		# splitterPos = settings.get_option('entity/secondary_splitter_pos', -1)
		# if(splitterPos != -1): self.splitter.moveSplitter(splitterPos, 1)
		self.splitter.splitterMoved.connect(self.secondarySplitterMoved)
		
		
		self.updating = False
		self.loadingAnim = False
		
		#self.editorTabWidget.currentChanged.connect(self.reloadText)
		
		self.frameEditor.loadFrame()
		
	def addAnim(self, ID):
		self.validateChanges()
		if ID in self.dicData:
			return
		lines = ['anim ' + ID, '\tframe data/chars/misc/empty.gif']
		data = {'ID':ID, 'label':'', 'lines':lines}
		self.dicData[ID] = lines
		self.fullData.append(data)
		
	def eventFilter(self, obj, e):
		#print(e.type(), e.FocusIn)
		return False
		minSize = 200
		if(e.type() == e.FocusIn and obj == self.editor):
			self.splitter.setSizes([self.splitter.width()-minSize, minSize])
		if(e.type() == e.FocusOut and (obj == self.editor )): #or obj == self.frameEditor.graphicView)
			self.splitter.setSizes([self.splitter.width()/2, self.splitter.width()/2])
			self.processLines()
			self.frameEditor.loadFrame()
		elif(e.type() == e.FocusIn and obj == self.frameEditor.graphicView):
			self.splitter.setSizes([minSize, self.splitter.width()-minSize])
			#return True
		#else:
		return False
		
		

	
	def getFullLines(self):
		self.processLines() # Update data to match current text
		self.validateChanges() # Shouldn't be needed
		
		sections = []
		lines = []
		for data in self.fullData:
			lines.extend(data['lines'])
		return lines

		
	def loadAnim(self, ID):
		self.loadingAnim = True
		self.validateChanges()
		if ID not in self.dicData:
			self.currentAnim = None
			return
		self.currentAnim = ID
		lines = self.dicData[ID]
		#print(lines)
		self.editor.lines = lines
		print(lines)
		self.processLines(lines)
		self.currentFrame = 0
		self.frameEditor.loadFrame()
		self.loadingAnim = False
	
	
	def loadFile(self, path):
		f = open(path)
		self.fullText = f.read()
		f.close()
		lines = self.fullText.split('\n')
		self.loadLines(lines)
		
	'''
		 fullData and dicData are linked (they share the same data)
		 dicData exists to provide a key access to fullData
	'''
	def loadLines(self, lines, model=None):
		
		self.updating = True
		self.currentAnim = None
		
		sectionLines = []
		dicData = {'header':sectionLines}
		fullData = [{'ID':'header', 'label':'', 'lines':sectionLines}]
		
		
		ent_cache = Cache('entities_data', EntityEditorWidget.ROOT_PATH)
		
		name = None
		
		for line in lines:
			pLine = ParsedLine(line)
			part = pLine.next()
			if part != None : part = part.lower()
			if part == 'anim':
				label = pLine.getCom()
				#print(pLine.parts, pLine.pos)
				animID = pLine.next()
				sectionLines = []
				fullData.append({'ID':animID, 'label':label, 'lines': sectionLines})
				dicData[animID] = sectionLines
			elif part == 'name':
				name = pLine.next().lower()
				if(model is None): model = name
			elif part == 'type':
				type = pLine.next().lower()
				if model is not None:
					try:
						ent_cache.data[model]['type'] = type
						ent_cache.save()
					except:
						print("no model named ", model)
			elif part == 'icon':
				icon = pLine.next()
				if model is not None:
					try:
						ent_cache.data[model]['icon'] = icon
						ent_cache.save()
					except:
						print("no model named ", model)
			sectionLines.append(line)
			
		self.dicData = dicData
		self.fullData = fullData
		#print(fullData)
		for key in dicData:
			print(key)
			
		self.animSelector.clear()
		self.animSelector.load(fullData)

		self.editor.lines = []
		self.loadAnim('idle')
		self.frameEditor.loadFrame(self.currentFrame)
		self.updating = False
		self.switchingFrame = False
		

	def secondarySplitterMoved(self, pos, index):
		print(pos, index)
		settings.set_option('entity/secondary_splitter_pos', pos)

	'''
		text changed
	'''
	def notifyChange(self):
		print('notifyChange')
		lines = self.editor.lines
		self.processLines(lines)
		self.frameEditor.loadFrame()
		
	'''
		DEPRECATED
	'''
	def reloadText(self, index):
		if index == 1: # Going to editor
			print("currentFrame", self.currentFrame)
			if len(self.anim) > 0:
				self.frameEditor.propEditor.updateData(self.frames[self.currentFrame])
			self.rebuildText()
			print("currentFrame", self.currentFrame)
			cursor = self.editor.textCursor()
			cursor.setPosition(self.editor.document().findBlockByLineNumber(self.getLineOf(self.currentFrame)).position())
			self.editor.setTextCursor(cursor)
			print("currentFrame", self.currentFrame)
			
			
		self.processLines(self.editor.lines)
		self.frameEditor.loadFrame(self.currentFrame)
			
		
		
	def reloadSplitterPos(self):
		splitterPos = settings.get_option('entity/secondary_splitter_pos', -1)
		if(splitterPos != -1): self.splitter.moveSplitter(splitterPos, 1)
	
	def getLineOf(self, frameNumber):
		if len(self.anim) == 0 : return 0
		lines = self.editor.lines
		
		inLineScript = False
	
		currentFrameNumber = -1
		for lineNumber, line in enumerate(lines):
			pLine = ParsedLine(line)
			part = pLine.next()
			
			if(part == '@script'):
				inLineScript = True
			elif(part == '@end_script'):
				inLineScript = False
			elif(not inLineScript and part == 'frame'):
				path = pLine.next()
				currentFrameNumber += 1
			if(currentFrameNumber == frameNumber):
				break
				
		#print(frameNumber, 
		return lineNumber
	
	
	def getNumberOfLine(self, targetLineNumber):
		if len(self.anim) == 0 : return 0
		lines = self.editor.lines
		
		inLineScript = False
	
		currentFrameNumber = 0
		for lineNumber, line in enumerate(lines):
			if(lineNumber == targetLineNumber):
				break
				
			pLine = ParsedLine(line)
			part = pLine.next()
				
			if(part == '@script'):
				inLineScript = True
			elif(part == '@end_script'):
				inLineScript = False
			elif(part == 'frame'):
				path = pLine.next()
				currentFrameNumber += 1
				

				
			
			
		if currentFrameNumber >= len(self.anim) : return len(self.anim) -1
		#print(frameNumber, 
		return currentFrameNumber
		
		
	def positionChanged(self):
		if self.updating or self.switchingFrame:
			return
		print("pos changed")
		line = self.editor.textCursor().blockNumber()
		frameNumber = self.getNumberOfLine(line)
		#cIndex = self.frameViewer.currentIndex()
		#print('isValid', cIndex.isValid())
		#nIndex = cIndex.sibling(frameNumber, 0)
		nIndex = self.frameViewer.model.createIndex(frameNumber, 0) 
		self.updating = True
		self.frameViewer.setCurrentIndex(nIndex)
		self.updating = False
		#self.frameEditor.loadFrame()

		
	def onFrameClick(self, index):
		if self.loadingAnim : return
		if len(self.anim) == 0 : return
		self.switchingFrame = True
		print('onFrameClick', self.currentFrame)
		if self.currentFrame < len(self.frames):
			self.frameEditor.propEditor.updateData(self.frames[self.currentFrame])
		frameNumber = index.row()

		
		
		
		if not self.updating:
			cursor = self.editor.textCursor()
			cursor.setPosition(self.editor.document().findBlockByLineNumber(self.getLineOf(frameNumber)).position())
			self.editor.setTextCursor(cursor)
			
		
		self.frameEditor.loadFrame(frameNumber)
		self.switchingFrame = False
	
		

		
	def select(self, item):
		self.controlWidget.load(item)
		
		
		
	'''
		Animation text editor lines to data (serves as update)
	'''
	def processLines(self, lines=None):
		
		def checkForBindingMask():
			if bindingMaskIdentifier == None: return
			if(pLine.line.lstrip().startswith(bindingMaskIdentifier)):
				print('processLines bindingMaskIdentifier FOUND')

				bindData = BindData(pLineMask, ParsedLineMask(pLine.line))
				frame['bind'] = bindData
		
		
		if lines is None : lines = self.editor.lines
		frame = {}
		self.frames = []
		#lines = text.split('\n')
		
		isInScript = False
		
		
		bindingMask = settings.get_option('entity/binding_mask', '')
		bindingMaskIdentifier = None
		bindingMaskIdentifierIsComment = False
		if(bindingMask != ''):
			pLineMask = ParsedLineMask(bindingMask)
			bindingMaskIdentifier = pLineMask.identifier
			if(bindingMaskIdentifier.startswith('#')): bindingMaskIdentifierIsComment = True
		print('processLines bindingMaskIdentifier', bindingMaskIdentifier)
		
		
	
		for line in lines:
			pLine = ParsedLine(line)
				
			part = pLine.next()
			if(part is None):
				checkForBindingMask()
				continue
			
			elif(part == '@script'):
				isInScript = True
			elif(part == '@end_script'):
				isInScript = False
				
			if isInScript: continue
		
			if(part == 'frame'):
				path = pLine.next()
				if path != None:
					frame['frame'] = path
					self.frames.append(frame)
					frame = {}
				
			elif(part == 'delay'):
				#delay = int(float(pLine.next()))
				delay = parseInt(pLine.next())
				
				frame['delay'] = delay
				
			elif(part == 'dropv'):
				if 'attack' not in frame:
					frame['attack'] = AttackBox()
				abox = frame['attack']
				data = []
				while(pLine.next() != None):
					data.append(parseFloat(pLine.current()))
				abox.loadLegacy('dropv', data)
				
				
			elif(part == 'hitfx'): # TODO
				if 'attack' not in frame:
					frame['attack'] = AttackBox()
				abox = frame['attack']
				data = []
				while(pLine.next() != None):
					data.append(pLine.current())
				abox.loadLegacy('hitfx', data)
				
			elif(part == 'hitflash'): # TODO
				if 'attack' not in frame:
					frame['attack'] = AttackBox()
				abox = frame['attack']
				data = []
				while(pLine.next() != None):
					data.append(pLine.current())
				abox.loadLegacy('hitflash', data)
				
			elif(part == 'offset'):
				x = parseInt(pLine.next())
				y = parseInt(pLine.next())
				frame['offset'] = (x, y)
			
			elif(part.startswith('bbox')):
				
				commandParts = part.split('.')
				if len(commandParts) == 1: # bbox legacy/main command (with multiple/all params)
					frame['bbox'] = BBox(pLine)
					
				else: # e.g., bbox.position.x
					if 'bbox' not in frame:
						frame['bbox'] = BBox()
					bbox = frame['bbox']
					
					try:
						if commandParts[1] == 'position':
							if commandParts[2] == 'x':
								bbox.x = parseInt(pLine.next())
								bbox.ogLineX = pLine
							elif commandParts[2] == 'y':
								bbox.y = parseInt(pLine.next())
								bbox.ogLineY = pLine
						elif commandParts[1] == 'size':
							if commandParts[2] == 'x':
								bbox.width = parseInt(pLine.next())
								bbox.ogLineWidth = pLine
							elif commandParts[2] == 'y':
								bbox.height = parseInt(pLine.next())
								bbox.ogLineHeight = pLine
							elif commandParts[2] == 'z':
								if commandParts[3] == '1':
									bbox.z1 = parseInt(pLine.next())
									bbox.ogLineZ1 = pLine
								elif commandParts[3] == '2':
									bbox.z2 = parseInt(pLine.next())
									bbox.ogLineZ2 = pLine
						
								
					except IndexError:
						pass
					
				
			elif(part.startswith('attack') or part.startswith('shock') or part.startswith('burn')):
				
				commandParts = part.split('.')
				if len(commandParts) == 1: # attack legacy/main command (with multiple/all params)
					if len(pLine) > 6:
						data = [part]
						while(pLine.next() != None):
							data.append(parseInt(pLine.current()))
							
										
						while len(data) < 11:
							data.append(0)
						# x, y, w, h, d, p, block, noflash, pause, z
						
						frame['attack'] = AttackBox(data)
						frame['attack'].ogLine = pLine
				else: # e.g., abox.position.x
					if 'attack' not in frame:
						frame['attack'] = AttackBox()
					abox = frame['attack']
					
					try:
						if commandParts[1] == 'block':
							if commandParts[2] == 'penetrate':
								abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
								abox.ogLines['.'.join(commandParts[1:])] = pLine
								
						elif commandParts[1] == 'damage':
							if commandParts[2] == 'force':
								abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
								abox.ogLines['.'.join(commandParts[1:])] = pLine
							if commandParts[2] == 'type':
								abox.data['.'.join(commandParts[1:])] = pLine.next()
								abox.ogLines['.'.join(commandParts[1:])] = pLine
								
						elif commandParts[1] == 'effect':
							if commandParts[2] == 'hit':
								if commandParts[3] == 'flash':
									if commandParts[4] == 'disable':
										abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
										abox.ogLines['.'.join(commandParts[1:])] = pLine
									elif commandParts[4] == 'model':
										abox.data['.'.join(commandParts[1:])] = pLine.next()
										abox.ogLines['.'.join(commandParts[1:])] = pLine
								elif commandParts[3] == 'sound':
									if commandParts[4] == 'path':
										abox.data['.'.join(commandParts[1:])] = pLine.next()
										abox.ogLines['.'.join(commandParts[1:])] = pLine
								
						elif commandParts[1] == 'position':
							if commandParts[2] == 'x':
								abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
								abox.ogLines['.'.join(commandParts[1:])] = pLine
							elif commandParts[2] == 'y':
								abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
								abox.ogLines['.'.join(commandParts[1:])] = pLine
								
						elif commandParts[1] == 'reaction':
							if commandParts[2] == 'fall':
								if commandParts[3] == 'force':
									abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
									abox.ogLines['.'.join(commandParts[1:])] = pLine
								if commandParts[3] == 'velocity':
									if commandParts[4] == 'x':
										abox.data['.'.join(commandParts[1:])] = parseFloat(pLine.next())
										abox.ogLines['.'.join(commandParts[1:])] = pLine
									elif commandParts[4] == 'y':
										abox.data['.'.join(commandParts[1:])] = parseFloat(pLine.next())
										abox.ogLines['.'.join(commandParts[1:])] = pLine
									elif commandParts[4] == 'z':
										abox.data['.'.join(commandParts[1:])] = parseFloat(pLine.next())
										abox.ogLines['.'.join(commandParts[1:])] = pLine
							elif commandParts[2] == 'pause':
								if commandParts[3] == 'time':
									abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
									abox.ogLines['.'.join(commandParts[1:])] = pLine
									
						elif commandParts[1] == 'size':
							if commandParts[2] == 'x':
								abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
								abox.ogLines['.'.join(commandParts[1:])] = pLine
							elif commandParts[2] == 'y':
								abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
								abox.ogLines['.'.join(commandParts[1:])] = pLine
							elif commandParts[2] == 'z':
								if commandParts[3] == '1':
									abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
									abox.ogLines['.'.join(commandParts[1:])] = pLine
								elif commandParts[3] == '2':
									abox.data['.'.join(commandParts[1:])] = parseInt(pLine.next())
									abox.ogLines['.'.join(commandParts[1:])] = pLine
						
						
					except IndexError:
						pass
					
				
			elif(part == 'range'):
				xMin = parseInt(pLine.next())
				xMax = parseInt(pLine.next())
				frame['range'] = (xMin, xMax)
				
			elif(part == 'platform'):
				data = []
				while(pLine.next() != None):
					data.append(parseInt(pLine.current()))
				
				frame['platform'] = Platform(data)

				
			elif(part == 'drawmethod'):
				prop = pLine.next()
				if prop != None:
					frame['drawmethod_' + prop] = pLine.next()
					
			elif(bindingMaskIdentifier != None):
				checkForBindingMask()
				
				
				
				
				
		self.frameViewer.clear()
		for frame in self.frames:
			path = os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame'])
			self.frameViewer.model.append(Portrait.fromPath(path))
			
		self.anim = Anim(self.frames)
			
			
	'''
		Recreate the animation editor text with the current animation data
	'''
	def rebuildText(self):
		
		print('REBUILDING ANIM TEXT')
		
		legacy = settings.get_option('misc/legacy_commands', False)
		self.updating = True
		self.editor.saveScroll()
		lines = self.editor.lines # self.editor.text.split('\n')
		
		filled = {'bbox':False, 'attack':False, 'delay':False, 'offset':False, 'range':False, 'platform':False, 'bind':False}
		
		newLines = []
		currentFrame = 0
		inLineScript = False
		inBBox = False
		inAbox = False
		
		
		bindingMask = settings.get_option('entity/binding_mask', '')
		print('binding mask', bindingMask)
		bindingMaskIdentifier = None
		if(bindingMask != ''):
			pLineMask = ParsedLineMask(bindingMask)
			bindingMaskIdentifier = pLineMask.identifier
			
		print('binding id', bindingMaskIdentifier)
			
		
		for line in lines:
			
			pLine = ParsedLine(line)
			part = pLine.next()
			
			if inBBox and (part is not None and part.startswith('bbox')):
				continue
			else:
				inBBox = False
				
			if inAbox and (part is not None and part.startswith('attack')):
				continue
			else:
				inAbox = False
			
			
			if(bindingMaskIdentifier != None and pLine.line.lstrip().startswith(bindingMaskIdentifier)):
				
				bindData = self.anim[currentFrame]['bind']
				newLines.append(bindData.getText(pLineMask))
				filled['bind'] = True
				continue
				
			elif part is None:
				pass
			elif(part == '@script'):
				inLineScript = True
			elif(part == '@end_script'):
				inLineScript = False
			elif(not inLineScript and part == 'frame'):
				# Before ending current frame, fill new data (from frameEditor)
				if not filled['bbox'] and 'bbox' in self.anim[currentFrame]:
					bbox = self.anim[currentFrame]['bbox']
					newLines.append(bbox.getText())
					#newLines.append('\tbbox ' + ' '.join(map(str, self.anim[currentFrame]['bbox'].getParams())) )
				if not filled['attack'] and 'attack' in self.anim[currentFrame]:
					newLines.append(self.anim[currentFrame]['attack'].getText())
					
				if not filled['platform'] and 'platform' in self.anim[currentFrame]:
					platform = self.anim[currentFrame]['platform']
					newLines.append(platform.getText())
					
				if not filled['bind'] and 'bind' in self.anim[currentFrame] and bindingMaskIdentifier != None:
					bindData = self.anim[currentFrame]['bind']
					newLines.append(bindData.getText(pLineMask))
					
				currentFrame += 1
				filled = {'bbox':False, 'attack':False, 'delay':False, 'offset':False, 'range':False, 'platform':False, 'bind':False}
				
			elif(part == 'offset'):
				filled[part] = True
				pLine.next()
				newParts = ' '.join(map(str, self.anim[currentFrame]['offset']))
				pLine.parts[pLine.pos:] = newParts

			elif(part == 'delay'):
				filled[part] = True
				pLine.next()
				if 'delay' in self.anim[currentFrame]:
					pLine.set(str(self.anim[currentFrame]['delay']))
					
			elif(part in ('hitfx', 'hitflash')):
				#continue
				if not legacy : continue
			elif(part in ('dropv')):
				continue
					
			elif(part.startswith('bbox')):
				inBBox = True
				filled['bbox'] = True
				pLine.next()
				
				if 'bbox' in self.anim[currentFrame]: # If not, means added directly in animation text editor
					if self.anim[currentFrame]['bbox'].delete : # Set to DELETE from FramePropertiesEditor
						del self.anim[currentFrame]['bbox']
						continue
					
					newLines.extend(self.anim[currentFrame]['bbox'].getText().split('\n'))
					continue
					#newParts = ' '.join(map(str, self.anim[currentFrame]['bbox'].getParams()))
					#newParts = re.split('( )', newParts)
					#pLine.parts[pLine.pos:] = newParts
				#print(parts)
				
			elif(part.startswith('attack') or part.startswith('shock') or part.startswith('burn')): #  and len(pLine) > 6
				if(currentFrame >= len(self.anim.frames)):
					QtWidgets.QMessageBox.warning(self, _('Error'), _('An attackbox was declared after the last frame'))
					return
				
				inAbox = True
				filled['attack'] = True
				pLine.next()

				if 'attack' in self.anim[currentFrame]: # If not, means added directly in animation text editor
					if self.anim[currentFrame]['attack'].delete: # Set to DELETE from FramePropertiesEditor
						del self.anim[currentFrame]['attack']
						continue

					newLines.extend(self.anim[currentFrame]['attack'].getText().split('\n'))
					continue
				
					#newParts = ' '.join(map(str, self.anim[currentFrame]['attack']))
					#newParts = re.split('( )', newParts)
					#pLine.parts[pLine.pos:] = newParts
					#newParts.insert(0, '\t')
					#pLine.parts = newParts
					
			elif part == 'platform':
				filled['platform'] = True
				if 'platform' in self.anim[currentFrame]:
					newLines.extend(self.anim[currentFrame]['platform'].getText().split('\n'))
					continue
				
			elif(part == 'range'):
				filled[part] = True
				pLine.next()
				newParts = ' '.join(map(str, self.anim[currentFrame]['range']))
				pLine.parts[pLine.pos:] = newParts

			line = pLine.getText()
			newLines.append(line)
			
	
		self.editor.lines = newLines #self.editor.setPlainText('\n'.join(newLines))
		self.editor.restoreScroll()
		self.updating = False
		
		
		
	
	def save(self):
		lines = self.getFullLines()
		#output = '\n'.join(lines)
		
		self.parent.editor.setLines(lines)
		self.parent.save()
	
	'''
		Replace the initial section/anim with the edited copy in the file representation (fullData)
		This is required when moving from editing a section to editing another
	'''
	def validateChanges(self):
		if self.currentAnim is not None:
			#self.rebuildText() # WARNING
			print(self.editor.lines)
			del self.dicData[self.currentAnim][:]
			self.dicData[self.currentAnim].extend( list(self.editor.lines))

	
				
				
class FrameEditor(QtWidgets.QWidget):
	
	refresh = QtCore.pyqtSignal()
	endDrag = QtCore.pyqtSignal()
	
	
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.parent = parent
		
		layout = QtWidgets.QHBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(layout)
		
		view = ImageWidget()
		scene = FrameScene(self)
		self.scene = scene
		view.setScene(scene)
		self.graphicView = view
		
		
		rightPanel = QtWidgets.QTabWidget()
		
		self.propEditor = FramePropertiesEditor(parent)
		scrollArea = QtWidgets.QScrollArea()
		scrollArea.setWidget(self.propEditor)
		
		rightPanel.addTab(scrollArea, _('Frame'))
		
		self.bindingEditor = BindingEditor(parent)
		scrollArea = QtWidgets.QScrollArea()
		scrollArea.setWidget(self.bindingEditor)
		
		rightPanel.addTab(scrollArea, _('Bindings'))
		
		
		leftSide = QtWidgets.QWidget()
		leftLayout = QtWidgets.QVBoxLayout()
		leftLayout.setContentsMargins(0, 0, 0, 0)
		leftSide.setLayout(leftLayout)
		
		layout.addWidget(leftSide, 1)
		layout.addWidget(rightPanel, 0)
		
		
		buttonGroup = QtWidgets.QButtonGroup()
		self.buttonBar = QtWidgets.QToolBar()
		self.label = QtWidgets.QLabel('Frame 0')
		self.buttonBar.addWidget(self.label)
		self.buttonBar.addSeparator()
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('media-playback-start'), None, self.playFrames)
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('zoom-in'), None, self.graphicView.zoomIn)
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('zoom-out'), None, self.graphicView.zoomOut)
		self.buttonBar.addAction('Set Offset', lambda:self.setMode('offset'))
		self.buttonBar.addAction('Set Bbox', lambda:self.setMode('bbox'))
		self.buttonBar.addAction('Set Abox', lambda:self.setMode('attack'))
		self.buttonBar.addAction('Set Platform', lambda:self.setMode('platform'))
		self.onionSkinAction = self.buttonBar.addAction('Onion skin', self.setOnionSkin)
		self.onionSkinAction.setCheckable(True)
	
		self.exportAnimationAction = self.buttonBar.addAction('Export', self.exportAnimation)
		self.reloadSpritesAction = self.buttonBar.addAction('Reload sprites', self.reloadSprites)
		#self.buttonBar.addAction(QtGui.QIcon.fromTheme('go-next'), None, self.loadNext)
		#self.buttonBar.addAction(QtGui.QIcon.fromTheme('edit-clear'), None, self.clear)
		
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F5", "Refresh")), self, self.reloadSprites)
		
		# QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F3", "Flip Opponent")), self, self.flipOpponent)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F6", "Flip Opponent")), self, self.flipOpponent)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F4", "Next Frame")), self, self.nextFrameOpponent)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/zoom-in_global', 'Ctrl++')), self.parent, self.graphicView.zoomIn)
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/zoom-out_global', 'Ctrl+-')), self.parent, self.graphicView.zoomOut)
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/zoom-in', '+')), self.graphicView, self.graphicView.zoomIn, context=QtCore.Qt.WidgetShortcut)
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/zoom-out', '-')), self.graphicView, self.graphicView.zoomOut, context=QtCore.Qt.WidgetShortcut)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/set_body_box', 'B')), self.graphicView,  lambda:self.setMode('bbox'), context=QtCore.Qt.WidgetShortcut)
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/set_attack_box', 'A')), self.graphicView,  lambda:self.setMode('attack'), context=QtCore.Qt.WidgetShortcut)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/play_animation', 'P')), self.graphicView,  self.playFrames, context=QtCore.Qt.WidgetShortcut)
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/play_animation_global', 'Ctrl+P')), self.parent, self.playFrames, context=QtCore.Qt.ApplicationShortcut)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/next_frame_global', 'Ctrl+Right')), self.parent, self.nextFrame, self.nextFrame)
		QtWidgets.QShortcut(QtGui.QKeySequence(settings.get_option('shortcuts/previous_frame_global', 'Ctrl+Left')), self.parent, self.previousFrame, self.previousFrame)
		
		

		
		leftLayout.addWidget(self.buttonBar, 0)
		leftLayout.addWidget(view, 1)
		
		self.setMode('pos')
		self.looping = False
		self.refresh.connect(self.loadFrame)
		self.onionSkin = None
		self.opponentModel = None
		self.opponent = None
		self.grid = GridItem()
		self.drawOpponent()
		
		self.endDrag.connect(self.endDragEvent)
		
		
	def drawOnionSkin(self):
		if self.onionSkin != None:
			self.scene.addItem(self.onionSkin)
			
	def drawOpponent(self):
		if self.opponent != None:
			data = self.getCurrentFrame()
			if('bind' in data):
				bindData = data['bind']
				self.opponent.setAt(0)
				print(bindData['frame'])
				self.opponent.setFrame( bindData['frame'])
				self.opponent.actualizeFrame()
				
				direction = bindData['direction']
				self.opponent.x = bindData['x']
				self.opponent.altitude = bindData['y']
				self.opponent.z = bindData['z']
				
				self.opponent.setZValue(self.opponent.z)
				
#				
				if(direction == -1 or direction ==-2):
					self.opponent.setDirection(False)
				elif(direction == 1 or direction == 2):
					self.opponent.setDirection(True)
				else:
					self.opponent.setDirection(self.opponent.facingRight)
					# self.opponent.setAt(0)
				
				
				# self.opponent.at = 0
				
				
				# if(direction == -1):
				# 	self.opponent.setDirection(False)
				# else:
				# 	self.opponent.setDirection(True)
				# self.scene.addRect(self.opponent.xOffset, self.opponent.yOffset,10,10)
				
			self.scene.addItem(self.opponent)
	
	def nextFrameOpponent(self):
		if self.opponent != None:
			self.opponent.nextFrame()
			self.opponent.actualizeFrame()
			print(self.opponent.xOffset, self.opponent.yOffset)
		
	def flipOpponent(self):
		if self.opponent != None:
			self.opponent.setDirection(not self.opponent.facingRight)
	
		
	def getCurrentFrame(self):
		return self.parent.frames[self.parent.currentFrame]

		
	def endDraw(self, obj):
		if self.mode == 'bbox' or self.mode == 'attack':
			
			frame = self.getCurrentFrame()
			xOffset, yOffset = self.parent.anim.getOffset(self.parent.currentFrame)
			x, y, w, h = int(obj.rect().x()+xOffset), int(obj.rect().y()+yOffset), int(obj.rect().width()), int(obj.rect().height())
			
			
			if self.mode == 'bbox':
				frame['bbox'] = BBox([x, y, w, h])
			else:
				if('attack' in frame):
					abox = frame['attack']
					
				else:
					abox = AttackBox()
					frame['attack'] = abox
				abox.data['position.x'] = x
				abox.data['position.y'] = y
				abox.data['size.x'] = w
				abox.data['size.y'] = h
					
		elif self.mode == 'offset':
			frame = self.getCurrentFrame()
			xOffset, yOffset = self.parent.anim.getOffset(self.parent.currentFrame)
			x, y, w, h = int(obj.rect().x()+xOffset), int(obj.rect().y()+yOffset), int(obj.rect().width()), int(obj.rect().height())
			
			
			frame['offset'] = [x, y]
			
		self.setMode('pos')
		self.propEditor.updateData(frame)
		self.parent.rebuildText()
		
		
	def exportAnimation(self):
		import subprocess
		args = [settings.get_option('misc/imagemagick_path', 'convert')]
		
		args.append('-dispose')
		args.append('background')
		args.append('-loop')
		args.append('0')
		delay = 7
		
		pil_frames = []
		pil_dur = []
		pil_offsets = []
		for i, frame in enumerate(self.parent.anim):
			path = os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame'])
			pil_frames.append(path)
			if 'delay' in frame:
				delay = frame['delay']
				if(delay < 0): delay = 10
			pil_dur.append(int(delay)*10)
			args.append('-delay')
			args.append(str(delay))
			
			args.append('-dispose')
			args.append('background')
			args.append('-page')
			x, y = self.parent.anim.getOffset(i)
			pil_offsets.append((x,y))
			args.append('-' + str(x-200) + '-' + str(y-200))
			args.append(path)
			
			
		lookFolder = EntityEditorWidget.ROOT_PATH
		
		import pathlib
		
		print(pil_frames)

		# desktop = pathlib.Path.home() / 'Desktop'
		home = pathlib.Path.home()
		
		# path =str(desktop) + os.sep+ 'animation.gif'
		path =str(home) + os.sep+ 'animation.gif'
		# print(path)
		# print(args)

		# import glob

		
		from PIL import Image
		
		print(len(pil_dur), len(pil_frames))
		
		print(pil_dur)
		
		print(pil_frames)
		
		print(pil_offsets)

# 		def add_margin(pil_img, x, y, top, right, bottom, left, color):
# 			width, height = pil_img.size
# 			new_width = width + right + left
# 			new_height = height + top + bottom
# 			
# 			x = int(new_width/2) - x
# 			y = int(new_height/2) - y
# 			
# 			result = Image.new(pil_img.mode, (new_width+100, new_height+100))
# 			if(pil_img.mode == "P"):
# 				result.putpalette( pil_img.palette.getdata()[ 1 ] )
# 			result.paste(pil_img, (x, y))
# 			return result
# 			
# 			
# 		# def canvas(srcImage):
# 		# 	newImage = Image.new(srcImage.mode, (newWidth,newHeight))
# 		# 	if(srcImage.mode == "P"):
# 		# 		newImage.putpalette( srcImage.palette.getdata()[ 1 ] )
# 		# 	newImage.paste(srcImage, (x1,y1,x1+oldWidth,y1+oldHeight))
# 
# 		def make_gif(path):
# 			frames = [Image.open(image) for image in pil_frames]
# 			maxWidth = 0
# 			maxHeight = 0
# 			for i in range(len(frames)):
# 				im = frames[i]
# 				x, y = pil_offsets[i]
# 				width, height = im.size
# 				width = width + x
# 				height = height +x
# 				if(width > maxWidth):
# 					maxWidth = width
# 				if(height > maxHeight):
# 					maxHeight = height
# 			for i in range(len(frames)):
# 				im = frames[i]
# 				x, y = pil_offsets[i]
# 				
# 				# frames[i] = ImageChops.offset(im, xoffset=x-200, yoffset=y-200)
# 				frames[i] = add_margin(im, x, y, int(maxHeight/2), int(maxWidth/2), 0, int(maxWidth/2), (128, 0, 64))
# 			frame_one = frames[0]
# 			frame_one.save(path, format="GIF", append_images=frames[1:],
# 				save_all=True, duration=pil_dur, loop=0, disposal=2)
    

		def add_margin(pil_img, x, y,canvasWidth, canvasHeight, minYMargin, maxYMargin):
			width, height = pil_img.size
			
			
			# x = int(new_width/2) - x
			# y = int(new_height/2) - y
			# print(canvasWidth, width, x)
			# x =  canvasWidth - width + x -200
			# y = canvasHeight - height + y -200
			
			# x -= int(canvasWidth / 2)
			# y -= int(canvasHeight / 2)
			
			# x += 100
			
			# canvasWidth += 
			
			x = 0 + width - x + canvasWidth - width    - int(canvasWidth/2)
			# y = 0 + height -y + canvasHeight - height - int(canvasHeight/2)
			y = 0 + height -y + canvasHeight - height - minYMargin
			
			canvasHeight += maxYMargin
			canvasHeight += -minYMargin
			
			
			# rgb_im = pil_img.convert('RGB')
			# color = rgb_im.getpixel((1, 1))
			
			# color = pil_img.getpixel((1, 1))
			result = Image.new(pil_img.mode, (canvasWidth, canvasHeight))
			# print(pil_img.mode)
			
			if(pil_img.mode == "P"):
				result.putpalette( pil_img.palette.getdata()[ 1 ] )
			result.paste(pil_img, (x, y))
			return result
			
			
		# def canvas(srcImage):
		# 	newImage = Image.new(srcImage.mode, (newWidth,newHeight))
		# 	if(srcImage.mode == "P"):
		# 		newImage.putpalette( srcImage.palette.getdata()[ 1 ] )
		# 	newImage.paste(srcImage, (x1,y1,x1+oldWidth,y1+oldHeight))

		def make_gif(path):
			frames = [Image.open(image) for image in pil_frames]
			maxWidth = 0
			maxHeight = 0
			maxYMargin = 0
			minYMargin = 0
			for i in range(len(frames)):
				im = frames[i]
				x, y = pil_offsets[i]
				width, height = im.size
				yMargin = height - y
				# width = width + int(width/2) - x
				# height = height +y
				# width =  la plus grosse moitié * 2
				
				
				moitie1 = width - x
				moitie2 = width - moitie1
				biggestHalf = max(moitie1, moitie2)
				width = biggestHalf * 2 + 1
				
				# moitie1 = height - y
				# moitie2 = height - moitie1
				# biggestHalf = max(moitie1, moitie2)
				# height = biggestHalf * 2 + 1
				
				
				
				print('yMargin', yMargin, x, y)
				if(width > maxWidth):
					maxWidth = width
				if(height > maxHeight):
					maxHeight = height
					
				if(yMargin > maxYMargin):
					maxYMargin = yMargin
					
				if(yMargin < minYMargin):
					minYMargin = yMargin
				
			print('maxYMargin', maxYMargin, 'minYMargin', minYMargin)
			
			canvasWidth = maxWidth + 1 
			canvasHeight = maxHeight + 1
			for i in range(len(frames)):
				im = frames[i]
				x, y = pil_offsets[i]
				
				
				
				# frames[i] = ImageChops.offset(im, xoffset=x-200, yoffset=y-200)
				frames[i] = add_margin(im, x, y, canvasWidth, canvasHeight, minYMargin, maxYMargin)
			frame_one = frames[0]
			frame_one.save(path, format="GIF", append_images=frames[1:],
				save_all=True, duration=pil_dur, loop=0, disposal=0)
		

		# make_gif()
		#args.append('-layers')
		#args.append('Optimize')
		
		
		
		path = QtWidgets.QFileDialog.getSaveFileName(self, directory=lookFolder+ os.sep+ 'animation.gif')[0]
		if(path is not None and path != ''):
			make_gif(path)
			# args.append(path)
			# subprocess.call(args)
			# pass
			
			
	def reloadSprites(self):
		print('\n*** Reloading Sprites ***\n')
		frames = self.parent.anim.frames
		for frame in self.parent.anim.frames:
			key = frame['frame']
			if key in self.parent.pixmapCache:
				del self.parent.pixmapCache[key]
		self.loadFrame()
		
		# icon viewer at the bottom
		self.parent.frameViewer.clear()
		for frame in frames:
			path = os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame'])
			self.parent.frameViewer.model.append(Portrait.fromPath(path))
			
		
	def setMode(self, mode):
		self.mode = mode
		self.scene.setMode(mode)
		if mode == 'bbox' or mode == 'attack':
			self.graphicView.setDragMode(QtWidgets.QGraphicsView.NoDrag)
			#self.scene.makeItemsControllable(False)
		elif(mode == 'pos'):
			self.graphicView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
			#self.scene.makeItemsControllable(True)
		elif(mode == 'platform'):
			anim = self.parent.anim
			frameNumber = self.parent.currentFrame
			if 'platform' in anim[frameNumber]:
				platform = anim[frameNumber]['platform']
			
			
				wall = platform.wall
				for dot in wall.dots:
					dot.show()
					
			else : # add new platform
				xOffset = 0
				yOffset = 0
				platform = anim.getPlatform(frameNumber)
				anim[frameNumber]['platform'] = platform
				wall = platform.getWall(xOffset, yOffset)
				self.scene.addItem(wall)
				for dot in wall.dots:
					self.scene.addItem(dot)
					#dot.hide()
				self.parent.rebuildText() # so as to add platform in text
		self.graphicView.setFocus()
		self.loadFrame()
		
		
	def loadFrame(self, frameNumber=None):
		print('Loading frame', frameNumber)

		anim = self.parent.anim
		if len(anim) == 0: return
		
		self.scene.removeItem(self.opponent)
		self.scene.removeItem(self.grid)
		self.scene.removeItem(self.onionSkin)
		self.scene.clear()
		
		#self.scene.setBackgroundBrush(QtGui.QBrush(gradient));
		self.scene.addItem(self.grid)
		
		
		if frameNumber is None:
			frameNumber = self.parent.currentFrame
		else:
			self.parent.currentFrame = frameNumber
		self.label.setText('Frame ' + str(frameNumber))
		
		if(frameNumber >= len(anim)) : return
	
		anim.currentFrame = frameNumber
	
		self.drawOnionSkin()
		
		self.drawOpponent()
	
		frame = anim[frameNumber]
		
		
		# drawmethod
		scaleX = anim.getDrawMethod(frameNumber, 'scalex')
		scaleY = anim.getDrawMethod(frameNumber, 'scaley')
		flipX = anim.getDrawMethod(frameNumber, 'flipx')
		flipY = anim.getDrawMethod(frameNumber, 'flipy')

		xOffset, yOffset = anim.getOffset(frameNumber)
		xOffset *= scaleX
		yOffset *= scaleY
		#print('offset', xOffset, yOffset)
		
		if frame['frame'] not in self.parent.pixmapCache:
			image = loadSprite(os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame']))
			self.parent.pixmapCache[ frame['frame'] ] = QtGui.QPixmap.fromImage(image)
		image = self.parent.pixmapCache[ frame['frame'] ]
		
		if scaleX != 1 or scaleY != 1:
			image = image.scaled(image.width() * scaleX, image.height() * scaleY)
		
		if flipX == 1 or flipY == 1:
			#image = image.mirrored(True, False)
			sX = 1
			if flipX == 1: sX = -1
			sY = 1
			if flipY == 1: sY = -1
			image = image.transformed(QtGui.QTransform().scale(sX, sY))
		
		item = QtWidgets.QGraphicsPixmapItem(image)
		item.setPos(-xOffset, -yOffset)
		self.scene.addItem(item)
		
		#self.scene.addRect(100,100,100,200)
		
		
		
		

		if(self.mode != 'bbox'):
	
			x, y, w, h= anim.getBBox(frameNumber).getParams()[0:4]
			print('bbox',anim.getBBox(frameNumber))
			if x != None:
				#print(x,xOffset,y,yOffset,w,h)
				bbox = QtWidgets.QGraphicsRectItem(x-xOffset,y-yOffset,w,h)
				bbox.setBrush(QtGui.QBrush(QtCore.Qt.blue))
				bbox.setOpacity(0.3)
				self.scene.addItem(bbox)
			
		if(self.mode != 'attack'):
			if 'attack' in anim[frameNumber]:
				abox = anim[frameNumber]['attack']
				#while len(anim[frameNumber]['attack']) < 5:
					#anim[frameNumber]['attack'].append(0)
				x, y, w, h = abox.getParams()[1:5]
				bbox = QtWidgets.QGraphicsRectItem(x-xOffset,y-yOffset,w,h)
				bbox.setBrush(QtGui.QBrush(QtCore.Qt.red))
				bbox.setOpacity(0.3)
				self.scene.addItem(bbox)
				
		xMin, xMax = anim.getRange(frameNumber)
		if xMin != None:
			rangeBox = QtWidgets.QGraphicsRectItem(xMin,-10,xMax-xMin,20)
			rangeBox.setBrush(QtGui.QBrush(QtCore.Qt.yellow))
			rangeBox.setOpacity(0.3)
			self.scene.addItem(rangeBox)
			

		if 'platform' in anim[frameNumber]:
			platform = anim[frameNumber]['platform']
			
			
			
			wall = platform.getWall(xOffset, yOffset)
			self.scene.addItem(wall)
			for dot in wall.dots:
				self.scene.addItem(dot)
				#dot.hide()
			
		self.scene.addRect(-5,-5,10,10) #offset
		self.scene.addRect(-1,-1,2,2) #offset precise
		self.propEditor.loadData(frame)
		self.bindingEditor.loadData(frame)
		
		

		
		
	def playFrames(self):
		@util.threaded
		def play():
			delay = 7
			while self.looping:
				for i, frame in enumerate(self.parent.anim):
					if not self.looping or i > len(self.parent.anim) : break
					path = os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame'])
					self.parent.currentFrame = i
					self.refresh.emit()
					if 'delay' in frame:
						delay = frame['delay']
					#self.loadFrame(i)
					time.sleep(delay / 100)
				
		if self.looping:
			self.looping = False
			return
		
		self.looping = True
		play()
		
	def nextFrame(self):
		self.parent.currentFrame += 1
		if( self.parent.currentFrame >= len(self.parent.anim)):
			self.parent.currentFrame = 0
		self.refresh.emit()
		
	def previousFrame(self):
		self.parent.currentFrame -= 1
		if( self.parent.currentFrame < 0):
			self.parent.currentFrame = len(self.parent.anim)-1
		self.refresh.emit()
		
		
	def loadOpponent(self):
		self.opponent = Entity(self.opponentModel, parentWidget=self, loadAllAnims = True, defaultAnim=settings.get_option('entity/last_opponent_animation', 'idle'), shadow=False, offset=True)
	
	def showOpponent(self, show): 
		if not show: # Just unchecked
			self.opponent = None
			self.loadFrame()
			return
			
		if(self.opponentModel not in Entity.AVAILABLE_MODELS):
			return
		self.loadOpponent()
		self.loadFrame()
		
		
	def endDragEvent(self):
		print('opponent mouse release', self.opponent.pos().x(), self.opponent.pos().y())
		self.bindingEditor.refreshEntPos()
		self.opponent.update()
		
	def setOnionSkin(self, frameNumber=None):
		if not self.onionSkinAction.isChecked(): # Just unchecked
			self.onionSkin = None
			self.loadFrame()
			return
		
		anim = self.parent.anim
		if len(anim) == 0: return
	
		if frameNumber is None:
			frameNumber = self.parent.currentFrame
	
		xOffset, yOffset = anim.getOffset(frameNumber)
	
		frame = self.getCurrentFrame()
		if frame['frame'] not in self.parent.pixmapCache:
			image = loadSprite(os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame']))
			#image = image.createMaskFromColor(image.color(0), QtCore.Qt.MaskOutColor)
			self.parent.pixmapCache[ frame['frame'] ] = QtGui.QPixmap.fromImage(image)
		
		
		image = QtGui.QImage(self.parent.pixmapCache[ frame['frame'] ])
		#image = image.convertToFormat (QtGui.QImage.Format_ARGB32, QtCore.Qt.MonoOnly);
		#pixels = image.width() * image.height()
		
		mainColor = image.color(0)
		for x in range(image.width()):
			for y in range(image.height()):
				pixel = image.pixel(x, y)
				if pixel == mainColor: continue
				grayPixel = QtGui.qGray(pixel)
				dstPixel = QtGui.qRgba(grayPixel, grayPixel, grayPixel, 255)
				image.setPixel(x, y, dstPixel)
		#data = image.bits()
		#data.setsize(pixels)
		#for i in range(pixels):
			#val = QtGui.qGray(data[i])
			#data[i] = QtGui.qRgba(val, val, val, QtGui.qAlpha(data[i]))
			
			
			

		
		item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(image))
		item.setPos(-xOffset, -yOffset)
		
		self.onionSkin = item
		self.loadFrame()

		
		

        
        
class FrameScene(QtWidgets.QGraphicsScene):
	
	def __init__(self, mainEditor):
		QtWidgets.QGraphicsScene.__init__(self)
		self.mainEditor = mainEditor
		self.setMode('pos')
		
		
	def setMode(self, mode):
		self.mode = mode

	
	def mousePressEvent(self, e):
		QtWidgets.QGraphicsScene.mousePressEvent(self, e)
		if self.mode == 'pos':
			return
		
		if(self.mode == 'platform'):
			self.dragRect = None
			return
		
		self.origPoint = e.scenePos()
		
		
		
		self.dragRect = self.addRect(e.scenePos().x(),e.scenePos().y(),1,1)
		if(self.mode == 'bbox'):
			self.dragRect.setBrush(QtGui.QBrush(QtCore.Qt.blue))
			self.dragRect.setOpacity(0.3)
		elif(self.mode == 'attack'):
			self.dragRect.setBrush(QtGui.QBrush(QtCore.Qt.red))
			self.dragRect.setOpacity(0.3)
		
			
		
		
	def mouseMoveEvent(self, e):
		QtWidgets.QGraphicsScene.mouseMoveEvent(self, e)
		if self.mode == 'pos':
			return
		if self.dragRect is not None:
			xStart = self.origPoint.x()
			xEnd =  e.scenePos().x()
			yStart = self.origPoint.y()
			yEnd = e.scenePos().y()
			#print(xStart, xEnd, yStart, yEnd)
			xStart, yStart, xEnd, yEnd = convertRect(xStart, yStart, xEnd, yEnd)
			
			self.dragRect.setRect(xStart, yStart, xEnd-xStart, yEnd-yStart)
		
		
	def mouseReleaseEvent(self, e):
		QtWidgets.QGraphicsScene.mouseMoveEvent(self, e)
		if self.mode == 'pos':
			return
		if self.mode == 'platform':
			self.mainEditor.parent.anim.getPlatform().platformUpdated()
			self.mainEditor.parent.rebuildText()
			return
		self.mainEditor.endDraw(self.dragRect)
		self.dragRect = None
		

		
		
        
class ImageWidget(QtWidgets.QGraphicsView):
	def __init__(self):
		QtWidgets.QGraphicsView.__init__(self)
		
		self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		#self.setInteractive(False)
		self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState | QtWidgets.QGraphicsView.DontAdjustForAntialiasing)

		scene = QtWidgets.QGraphicsScene(self)
		self.pic = QtGui.QPixmap('icons/8.jpg')
		#scene.addItem(QtWidgets.QGraphicsPixmapItem(pic))
		self.image = QtWidgets.QGraphicsPixmapItem(self.pic)
		#scene.addPixmap(self.pic)
		scene.addItem(self.image)
		self.setScene(scene)
		self.show()
		
		# Data attributes
		self.zoom = 1
		self.scaleFactor = 1.0
		
		self.setAcceptDrops(True);
		self.dragRect = None
		

		
	def loadFile(self, elt):
		path = elt.path
		image= QtGui.QPixmap(path)
		self.scene().setSceneRect(0, 0, image.width(), image.height())
		self.image.setPixmap(image)
		
		
	def wheelEvent(self, e):
		#scene.addItem(QtWidgets.QGraphicsPixmapItem(pic))
		#self.image.setPixmap(pic)
		#print(e.orientation())
		
		delta = e.angleDelta().y()
		self.zoomFunction(delta)

		
		#self.centerOn(e.x(), e.y()) # Removed this because it messed up centering
		print(self.zoom)
		#print(e.delta())
		print ('')
	
	def scaleImage(self, factor):
		self.scaleFactor *= factor
		self.scale(factor, factor)
		
		
	def zoomFunction(self, delta):
		print(delta)
		if delta > 0:
			self.scaleFactor *= 1.25
			self.scale(1.25, 1.25)
			return
			self.image.setPixmap(self.pic.scaled(self.scaleFactor * self.pic.size()))
			#self.scaleImage(1.25)
			
			return
			factor = self.zoom / (self.zoom + 0.1)
			self.zoom += 0.1
		else:
			self.scaleFactor *= 0.8
			self.scale(0.8, 0.8)
			return
			self.image.setPixmap(self.pic.scaled(self.scaleFactor * self.pic.size()))
			#self.scaleImage(0.8)
			return
			factor = self.zoom / (self.zoom - 0.1)
			self.zoom -= 0.1
		self.scale(factor, factor)
		
			
	def zoomIn(self):
		self.zoomFunction(1)
		
	def zoomOut(self):
		self.zoomFunction(-1)
		
class GridItem(QtWidgets.QGraphicsItemGroup):

	
	def __init__(self):
		QtWidgets.QGraphicsPolygonItem.__init__(self)
		
		rect = QtWidgets.QGraphicsRectItem(-500,-500,1000,500)
		p = QtCore.QPoint(0,100)
		gradient = QtGui.QLinearGradient(rect.rect().center()-p, rect.rect().center()+p)
		gradient.setColorAt(0, QtGui.QColor('#3d4958'))
		gradient.setColorAt(1.0, QtGui.QColor('#5a87b8'))
		rect.setBrush(gradient)
		self.addToGroup(rect)
		
		rect = QtWidgets.QGraphicsRectItem(-500,0,1000,100)
		p = QtCore.QPoint(0,100)
		gradient = QtGui.QLinearGradient(rect.rect().topLeft(), rect.rect().bottomLeft())
		gradient.setColorAt(0, QtGui.QColor('#3d4958'))
		gradient.setColorAt(1.0, QtGui.QColor('#5a87b8'))
		rect.setBrush(gradient)
		self.addToGroup(rect)
		
		space = 50
		for i in range(-10, 10):
			
		
			line = QtWidgets.QGraphicsLineItem(i*space, -1000, i*space, 1000)
			self.addToGroup(line)
			line = QtWidgets.QGraphicsLineItem(-1000, i*space, 1000, i*space)
			self.addToGroup(line)
			
			
		
		
		
