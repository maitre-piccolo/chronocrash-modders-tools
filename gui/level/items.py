import os, re, logging

from PyQt5 import QtCore, QtGui, QtWidgets

from common import settings
from gui.util import FileInput, loadSprite

from data import ParsedLine, FileWrapper


class Entity(QtWidgets.QGraphicsItemGroup):
	
	PROJECTS_VARS = {}
	
	
	@classmethod
	def projectChanged(cls, projectRoot=None):
		if(projectRoot != None):
			Entity.ROOT_PATH = projectRoot
		else :
			Entity.ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', '/home/piccolo/workspace/OpenBOR/data')) + os.sep
		
		
		if(Entity.ROOT_PATH in Entity.PROJECTS_VARS):
			vars = Entity.PROJECTS_VARS[Entity.ROOT_PATH]
			
			Entity.AVAILABLE_MODELS = vars['AVAILABLE_MODELS']
			Entity.PIXMAP_CACHE = vars['PIXMAP_CACHE']
			Entity.WARNED_NO_IDLE = vars['WARNED_NO_IDLE']
			Entity.LOADED_MODELS_REFERENCE = vars['LOADED_MODELS_REFERENCE']
		else:
			
		
			Entity.AVAILABLE_MODELS = []
			Entity.PIXMAP_CACHE = {}
			Entity.WARNED_NO_IDLE = []
			Entity.LOADED_MODELS_REFERENCE = {}
			
			vars = {}
			
			vars['AVAILABLE_MODELS'] = Entity.AVAILABLE_MODELS
			vars['PIXMAP_CACHE'] = Entity.PIXMAP_CACHE
			vars['WARNED_NO_IDLE'] = Entity.WARNED_NO_IDLE
			vars['LOADED_MODELS_REFERENCE'] = Entity.LOADED_MODELS_REFERENCE
			
			Entity.PROJECTS_VARS[Entity.ROOT_PATH] = vars
	
	
	def __init__(self, entName='rugal', line=-1, parentWidget=None, loadAllAnims=False, defaultAnim='idle', shadow=True, offset=False):
		QtWidgets.QGraphicsItemGroup.__init__(self)
		
		self.x = None
		self.z = None
		self.altitude = None
		self.at = None
		self.groupNumber = 0
		
		self.type = 'Unknown'
		
		self.reference = None
		
		self.allAnimLoaded = False
		self.palettes = []
		self.currentPalette = {'ID':''}

		# print(entName)
		self.parentWidget = parentWidget
		entName = entName.lower()
		self.name = entName
		self.line = line
		
		if shadow : self.showShadow = True
		else : self.showShadow =False
		# self.showShadow = True
		
		if offset : self.showOffset = True
		else : self.showOffset =False
		fPath = 'data/chars/rugal/2.gif'
		
		if(entName in Entity.LOADED_MODELS_REFERENCE and hasattr(Entity.LOADED_MODELS_REFERENCE[entName], 'anims')):
			reference = Entity.LOADED_MODELS_REFERENCE[entName]
			self.reference = reference
			self.anims = reference.anims
			self.allAnimLoaded = reference.allAnimLoaded
			self.modelPath = reference.modelPath
			self.type = reference.type
			self.entityModelFound = True
			
			self.palettes = reference.palettes
			
			
			
			self.xOffset = 0
			self.yOffset = 0
			self.fPath = None
			self.currentFrame = 0
			if(defaultAnim not in self.anims):
				self.loadAnims(defaultAnim, loadAllAnims)
		else:
		
			Entity.ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', '/home/piccolo/workspace/OpenBOR/data')) + os.sep
			
			path = os.path.join(Entity.ROOT_PATH, 'data', 'models.txt')
			if not os.path.isfile(path): return
		
			f = FileWrapper(path)
			lines = f.getLines()
			self.entityModelFound = False
			
			for i, line in enumerate(lines):
				pLine = ParsedLine(line)
				part = pLine.next()
				if part is None : continue
				if part.lower() == 'know' or part.lower() == 'load':
					name = pLine.next().lower()
					if name != entName : continue
					self.modelPath = pLine.next()
					
					
					
					self.loadAnims(defaultAnim, loadAllAnims)
				
			Entity.LOADED_MODELS_REFERENCE[self.name] = self
				
						
		
		
		
		if not self.entityModelFound:
			self.xOffset = 0
			self.yOffset = 0
			logging.debug('Level Editor : entity model not found for : ' + entName + ' (watch for case sensitivity)')
			return
			
		
		if(defaultAnim in self.anims):
			self.animUsed = defaultAnim
		else:
			if(self.name not in Entity.WARNED_NO_IDLE):
				Entity.WARNED_NO_IDLE.append(self.name)
				self.log('Entity ' + self.name + ' at line ' + str(self.line) + ' has no ' + defaultAnim + ' animation')
				
				
			self.animUsed = list(self.anims.keys())[0]
			
		
		self.changeAnimation(self.animUsed)

		
		px = Entity.PIXMAP_CACHE[self.fPath]
		self.frameWidth = px.width()
		self.frameHeight = px.height()
		
		
		self.frameItem = QtWidgets.QGraphicsPixmapItem(px)

		
		
			
		
		
		if('shadow' not in Entity.PIXMAP_CACHE):
			shadow = QtGui.QPixmap('icons/shadow.png').scaledToWidth(150)
			Entity.PIXMAP_CACHE['shadow'] = shadow
		else:
			shadow = Entity.PIXMAP_CACHE['shadow']
		# self.shadowWidth = shadow.width()
		# self.shadowHeight = shadow.height()
		
		self.shadow = QtWidgets.QGraphicsPixmapItem(shadow)
		# self.offset = QtWidgets.QGraphicsRectItem(self.xOffset, self.yOffset, 10, 10)
		
		self.offset = QtWidgets.QGraphicsItemGroup()
		showSquareOffset = settings.get_option('entity/binding_show_square_offset', False)
		
		self.squareOffset = QtWidgets.QGraphicsRectItem(0, 0, 10, 10)
		self.squareOffset.setBrush(QtGui.QBrush(QtGui.QColor(230,0,0, 100)))
		self.offset.addToGroup(self.squareOffset)
		if(not showSquareOffset): self.squareOffset.setVisible(False)
		showCrossOffset = settings.get_option('entity/binding_show_cross_offset', True)
		
			
		# line1 = QtWidgets.QGraphicsLineItem(5, 0 , 5, 10)
		# self.crossOffsetLine2 = QtWidgets.QGraphicsLineItem(0, 5 , 10, 5)
		self.crossOffsetLine1 = QtWidgets.QGraphicsRectItem(4, 0 , 2, 10)
		self.crossOffsetLine2 = QtWidgets.QGraphicsRectItem(0, 4 , 10, 2)
		
		self.offset.addToGroup(self.crossOffsetLine1)
		self.offset.addToGroup(self.crossOffsetLine2)
		
		
		self.crossOffsetLine1.setPen(QtGui.QPen(QtGui.QColor(255,255,255)))
		self.crossOffsetLine2.setPen(QtGui.QPen(QtGui.QColor(255,255,255)))
		self.crossOffsetLine1.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
		self.crossOffsetLine2.setBrush(QtGui.QBrush(QtGui.QColor(0,0,0)))
		
		if(not showCrossOffset):
			self.crossOffsetLine1.setVisible(False)
			self.crossOffsetLine2.setVisible(False)
			
		center = QtWidgets.QGraphicsRectItem(4, 4 , 2, 2)
		center.setBrush(QtGui.QBrush(QtGui.QColor(255,0,0)))
		self.offset.addToGroup(center)
		# else:
		# 	self.offset = QtWidgets.QGraphicsRectItem(0, 0, 10, 10)
		# 	self.offset.setBrush(QtGui.QBrush(QtGui.QColor(255,0,0)))
		
		# self.x = 0
		# self.y = 0
		
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
		
		
		
		if(self.showShadow):
			self.addToGroup(self.shadow)
		self.addToGroup(self.frameItem)
		
		if(self.showOffset):
			self.addToGroup(self.offset)
		
		
		# self.shadow.setPos(-self.shadowWidth/2 - self.xOffset, self.shadowHeight/2)
		self.updateShadowPos()
		
		self.timer = 0
		
		self.facingRight = True
		
	
	
	def setPalette(self, paletteRelativePath):
		
		paletteImage = loadSprite(os.path.join(Entity.ROOT_PATH, paletteRelativePath))
		
		
		self.currentPalette = {'ID':paletteRelativePath, 'colorTable': paletteImage.colorTable()}
		

		
		self.changeAnimation(self.animUsed)
		self.actualizeFrame()
		
		
	def loadAnims(self, defaultAnim, loadAllAnims=False):
		if(self.allAnimLoaded) : return
		fullPath = os.path.join(Entity.ROOT_PATH, self.modelPath)
		if not os.path.exists(fullPath) : return
	
		# print("loadAnims", defaultAnim, loadAllAnims)
		# print(fullPath)
		f = open(fullPath)
		lines2 = f.read().split('\n')
		f.close()
		inDefaultAnim = False
		self.fPath = None
		self.xOffset = 0
		self.yOffset = 0
		xOffset = 0
		yOffset = 0
		self.currentFrame = 0
		delay = 7
		self.palettes = []
		
		if(self.reference != None): self.anims = self.reference.anims
		else : self.anims = {}
		
		skipAnim = False
		for i, line2 in enumerate(lines2):
			pLine2 = ParsedLine(line2)
			part = pLine2.next()
			if(part != None) : part = part.lower()
			
			if(part == 'type'):
				self.type = pLine2.next().lower()
				
			elif(part == 'palette' or part == 'alternatepal'):
				print("adding palette")
				self.palettes.append(pLine2.next())
			
			elif part == 'anim':
				skipAnim = False
				animName = pLine2.next().lower()
				
				
				if animName == defaultAnim:
					inDefaultAnim = True
				elif inDefaultAnim and not loadAllAnims: # means we are leving default anim. And if not loadAllAnims, then we leave the loop when we leave default anim, there's no point to continue.
					break
					
				if(animName in self.anims):
					skipAnim = True
					# print("will skip", animName, self.anims[animName])
					
					continue
				
				# print("will load", animName)
				# if(animName != None) : animName = animName.lower()
				currentAnim = []
				self.anims[animName] = currentAnim
				currentFrame = {}
			
			elif skipAnim:
				continue
			elif part == 'offset': 
				xOffset = int(pLine2.next().lower())
				yOffset = int(pLine2.next().lower())
				
				currentFrame['xOffset'] = xOffset
				currentFrame['yOffset'] = yOffset
			elif part == 'delay': 
				delay = pLine2.next();
				try:
					delay = int(float(delay.lower()))
				except:
					self.log('Entity ' + self.name + ' at line ' + str(self.line) + ' has problem with delay ' + str(delay))
					delay = 7
				
				currentFrame['delay'] = delay
			elif part == 'frame': 
				fPath = pLine2.next() # .lower() cause problem in Linux
				
				currentFrame['path'] = fPath
				
					
				
				if('delay' not in currentFrame): currentFrame['delay'] = delay
				if('xOffset' not in currentFrame): currentFrame['xOffset'] = xOffset
				if('yOffset' not in currentFrame): currentFrame['yOffset'] = yOffset
				
				currentAnim.append(currentFrame)
				currentFrame = {}
				self.entityModelFound = True
				# break
		
		# if(self.reference != None):
		# 	self.reference.anims = self.anims
		if(loadAllAnims): self.allAnimLoaded = True
		
		
		
	def log(self, mess):
		if(self.parentWidget != None):
			try:
				self.parentWidget.logWarning(mess)
				
			except:
				print(mess)
	
	# def paint(self, painter, option, widget):
	# 	QtWidgets.QGraphicsPixmapItem.paint(self, painter, option, widget)
	# 	self.shadow.paint(painter, option, widget)
	
	def updateShadowPos(self):
		if(self.showShadow):
			self.shadow.setPos(self.xOffset - 72, self.yOffset - 54)
			
		if(self.showOffset):
			alt = 0
			# if(self.altitude != None): alt = self.altitude
			self.offset.setPos(self.xOffset-5, self.yOffset-5-alt)
		
		
	def actualizeFrame(self):
		if(self.timer != 0) : return
		# print('actualizing frame to ', self.frames[self.currentFrame]['path'])
		
		if(self.currentFrame >= len(self.frames)): return
		px = Entity.PIXMAP_CACHE[self.frames[self.currentFrame]['path'] + self.currentPalette['ID']]
		self.frameWidth = px.width()
		self.frameHeight = px.height()
		
		# self.frameWidth = px.width()
		# self.frameHeight = px.height()
		# self.removeFromGroup(self.frameItem)
		self.frameItem.setPixmap(px)
		# print(self.name, self.xOffset, self.yOffset)
		self.xOffset = self.frames[self.currentFrame]['xOffset']
		self.yOffset = self.frames[self.currentFrame]['yOffset']
		self.setAt(self.at)
		self.updateShadowPos()
		# self.frameItem = QtWidgets.QGraphicsPixmapItem(px)
		# self.addToGroup(self.frameItem)
		
		
	def changeAnimation(self, animID, reloadAnims=False, reloadAllAnims=False):
		if(reloadAnims):
			self.loadAnims(animID, reloadAllAnims)
		
		if(animID in self.anims):
			
			# preload pixmaps
			self.animUsed = animID
			self.frames = self.anims[self.animUsed]
			# print(self.name, animID,  self.anims[self.animUsed])
			if('xOffset' in self.frames[0]):
				if(self.xOffset == 0):
					self.xOffset = self.frames[0]['xOffset']
					self.yOffset = self.frames[0]['yOffset']
					
			if(self.fPath == None): self.fPath = self.frames[0]['path']
			
			
			options = {}
			if self.currentPalette['ID'] != '':
				options['colorTable'] = self.currentPalette['colorTable']
			
			for frame in self.frames:
				fPath = frame['path']
				if(fPath + self.currentPalette['ID'] not in Entity.PIXMAP_CACHE):
					# print("here", fPath + self.currentPalette['ID'])
					image = loadSprite(os.path.join(Entity.ROOT_PATH, fPath), 0, options)
					px = QtGui.QPixmap.fromImage(image)
					Entity.PIXMAP_CACHE[fPath + self.currentPalette['ID']] = px
			return True
		else:
			return False
		
		
	def paint(self, painter, option, a):
		# disable border select
		option.state = QtWidgets.QStyle.State_None
		return super(Entity, self).paint(painter, option)
		
	
	def setDirection(self, right):
		transform = QtGui.QTransform()
		transform.translate(self.xOffset, self.yOffset)


		
		
		if(right):
			transform.scale(1,1)
			# self.frameItem.setTransform(QtGui.QTransform.fromScale(1, 1))
		else:
			transform.scale(-1, 1)
			# self.frameItem.setTransform(QtGui.QTransform.fromScale(-1, 1))
			
		transform.translate(-self.xOffset, -self.yOffset)
		self.frameItem.setTransform(transform)
		self.facingRight = right
		self.setAt(self.at)
	
	def tick(self):
		self.timer += 1
		if(self.timer == self.frames[self.currentFrame]['delay']):
			self.timer = 0
			self.nextFrame()
			
	def nextFrame(self):
		self.timer = 0
		self.currentFrame += 1
		if( self.currentFrame >= len(self.frames)):
			self.currentFrame = 0
		# print('changing frame to ', self.currentFrame)
			

	def setFrame(self, frame):
		self.currentFrame = frame
		if( self.currentFrame >= len(self.frames)):
			self.currentFrame = 0
		if( self.currentFrame < 0):
			self.currentFrame = 0
		
		
	def setAt(self, at):
		# print('shadow width', self.shadowWidth)
		self.at = at
		if(at == None):
			return
		x = self.x
		y = self.z
		if(x == None):
			x = 0
			y = 0
		
		xOffset = self.xOffset
		yOffset = self.yOffset
		#print("HERE", x, y, self.at, xOffset, yOffset)
		# if(not self.facingRight):
		# 	xOffset =   -self.xOffset - self.frameWidth
		self.setPos(x + self.at - xOffset, y - yOffset)
		# self.shadow.setPos(self.x + self.at - self.xOffset, self.z - self.yOffset)
		if(self.altitude != None and self.entityModelFound):
			self.frameItem.setPos(0, -self.altitude)
			offsetX = self.offset.pos().x()
			offsetY = self.offset.pos().y()
			self.offset.setPos(offsetX, offsetY-self.altitude)
			
		
	def getCoords(self):
		if(self.at != None):
			
			data = [int(self.pos().x()) - self.at + self.xOffset, int(self.pos().y() + self.yOffset)]
		else :
			data = [int(self.pos().x()) - 0 + self.xOffset, int(self.pos().y() + self.yOffset)]
		# if(self.altitude != None):
		data.append(self.altitude)
		return data
		
		
	def mouseReleaseEvent(self, event):
		QtWidgets.QGraphicsItemGroup.mouseReleaseEvent(self, event)
		try:
			self.parentWidget.endDrag.emit()
		except:
			pass
	
	def showCrossOffsetChanged(self, show):
		self.crossOffsetLine1.setVisible(show)
		self.crossOffsetLine2.setVisible(show)
		
	def showSquareOffsetChanged(self,show):
		self.squareOffset.setVisible(show)
		
		
	def tint(self, tint):
		
		defaultColors = [
	   (230, 0, 0),
	   (230, 230, 0),
	   (0, 230, 230),
	   (230, 0, 230),
	   (0, 230, 0),
	   (0, 0, 230)
	   
	   ]
		
		colors = []
		for i in range(6):
			defaultValue = QtGui.QColor(*defaultColors[i]).name()
			value = settings.get_option('level/group_tint_color' + str(i), defaultValue)
			colors.append(value)
		
		
		if(self.groupNumber == 0): return
		group = self.groupNumber
		while group > 6:
			group = group % 6
		
		
	
		color = colors[group-1]
		
		
# 		px = Entity.PIXMAP_CACHE[self.fPath]
# 		self.frameWidth = px.width()
# 		self.frameHeight = px.height()
# 		
		
# 		self.frameItem = QtWidgets.QGraphicsPixmapItem(px)
		if(tint):
		
			# color = QtGui.QColor(*color)
			color = QtGui.QColor(color)
			effect = QtWidgets.QGraphicsColorizeEffect()
			effect.setColor(color)
			effect.setStrength(1.0)
			self.frameItem.setGraphicsEffect(effect)
			# image = QtGui.QImage(px)
			# mainColor = image.color(0)
			# for x in range(image.width()):
			# 	for y in range(image.height()):
			# 		pixel = image.pixel(x, y)
			# 		if pixel == mainColor: continue
			# 		grayPixel = QtGui.qGray(pixel)
			# 		dstPixel = QtGui.qRgba(grayPixel, grayPixel, grayPixel, 255)
			# 		image.setPixel(x, y, dstPixel)
			# self.frameItem = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(image))
		else:
			
			self.frameItem.setGraphicsEffect(None)
			return 
			px = Entity.PIXMAP_CACHE[self.fPath]
			
# 			px = Entity.PIXMAP_CACHE[self.frames[self.currentFrame]['path']]
# 			self.frameWidth = px.width()
# 			self.frameHeight = px.height()
# 			
			# self.frameWidth = px.width()
			# self.frameHeight = px.height()
			# self.removeFromGroup(self.frameItem)
			self.frameItem.setPixmap(px)
			
		
	def width(self):
		return self.frameWidth


class Bar(QtWidgets.QGraphicsItemGroup):
	
	
	def at(self, pos):
		
		pen = QtGui.QPen()
		if(hasattr(self, 'overWriteColor')):
			color = self.overWriteColor
			
		else:
			color = QtGui.QColor(*self.COLOR)
		brush = QtGui.QBrush(color)
		pen.setWidth(4)
		pen.setBrush(brush)
		

		
		self.textItem = QtWidgets.QGraphicsTextItem(self.TEXT)
		self.textItem.setPos(pos-10, self.TEXT_POS)
		self.line = QtWidgets.QGraphicsLineItem(pos, self.LINE_Y1 , pos, self.LINE_Y2)
		
		self.textItem.setDefaultTextColor(color)
		self.line.setPen(pen)
		
		self.addToGroup(self.line)
		self.addToGroup(self.textItem)


class Group(Bar):
	
	TEXT = 'G'
	COLOR = (0,200,0)
	TEXT_POS = 0
	LINE_Y1 = 30
	LINE_Y2 = 200
	
	def __init__(self, min, max):
		Bar.__init__(self)
		self.min = min
		self.max = max
		
	def setColor(self, groupNumber):
		self.groupNumber = groupNumber
		defaultColors = [
		(230, 0, 0),
		(230, 230, 0),
		(0, 230, 230),
		(230, 0, 230),
		(0, 230, 0),
		(0, 0, 230)
		
		]
		
		colors = []
		for i in range(6):
			defaultValue = QtGui.QColor(*defaultColors[i]).name()
			value = settings.get_option('level/group_tint_color' + str(i), defaultValue)
			colors.append(value)
		
		
		if(self.groupNumber == 0): return
		group = self.groupNumber
		while group > 6:
			group = group % 6-1
		
		

		color = colors[group-1]
		
		self.overWriteColor = QtGui.QColor( color)
		
		
		
class Wait(Bar):
	
	TEXT_POS = 300
	LINE_Y1 = 200
	LINE_Y2 = 300
	
	TEXT = 'W'
	COLOR = (200,200,200)




class DraggingItem(QtWidgets.QGraphicsItem):
	def __init__(self, parent, coordKey, isXAxis=True):
		QtWidgets.QGraphicsEllipseItem.__init__(self)
		self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
		self.parent = parent
		self.coordKey = coordKey
		self.isXAxis = isXAxis
	
	def itemChange(self, change, value):
		if (change == QtWidgets.QGraphicsItem.ItemPositionChange and self.scene()):
			if not self.parent.updating and self.parent.movingDot is None:
				self.parent.movingDot = self
				newPos = value
				rect = self.scene().sceneRect();
				
				
				
				
				print('pos changed', self.pos(), newPos)
				if self.isXAxis:
					xDist = newPos.x() -self.pos().x()
					newPos.setY(self.pos().y())
					
					self.parent.coords[self.coordKey] += xDist
				else:
					yDist = newPos.y() - self.pos().y()
					self.parent.coords[self.coordKey] -= yDist
					newPos.setX(self.pos().x())
					
				self.parent.updatePolygon()
				self.parent.movingDot = None
			#if (!rect.contains(newPos)) {
			#// Keep the item inside the scene rect.
			#newPos.setX(qMin(rect.right(), qMax(newPos.x(), rect.left())));
			#newPos.setY(qMin(rect.bottom(), qMax(newPos.y(), rect.top())));
			#return newPos;
			#}
		#}
		return QtWidgets.QGraphicsItem.itemChange(self, change, value);
		#}
		
	def move(self, xDist, yDist):
		pos = self.pos()
		pos.setX(pos.x() + xDist)
		pos.setY(pos.y() + yDist)
		self.setPos(pos)

class DraggingDot(QtWidgets.QGraphicsEllipseItem, DraggingItem):
	pass

class DraggingPix(QtWidgets.QGraphicsPixmapItem, DraggingItem):
	def __init__(self, parent, coordKey, isXAxis=True):
		DraggingItem.__init__(self, parent, coordKey, isXAxis)
		
		

class Wall(QtWidgets.QGraphicsItemGroup,): # TODO qgraphicsitemgroup

	BASE_ONLY = False
	COLOR = (186,85,211)
	LINE_WIDTH = settings.get_option('level/line_weight', 2)
	DOT_SIZE = settings.get_option('level/dot_size', 10)
	updated = QtCore.pyqtSignal()

	def __init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth, alt=100, type=None):
		self.updating = False
		self.movingDot = None
	
		QtWidgets.QGraphicsPolygonItem.__init__(self)
		
		self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
		
		self.mainItem = QtWidgets.QGraphicsPolygonItem()
		self.second = QtWidgets.QGraphicsPolygonItem()
		self.line1 = QtWidgets.QGraphicsLineItem()
		self.line2 = QtWidgets.QGraphicsLineItem()
		self.line3 = QtWidgets.QGraphicsLineItem()
		self.line4 = QtWidgets.QGraphicsLineItem()
		
		self.dot1 = DraggingDot(self, 'upperLeft')
		self.dot2 = DraggingDot(self, 'lowerLeft')
		self.dot3 = DraggingDot(self, 'lowerRight')
		self.dot4 = DraggingDot(self, 'upperRight')
		self.dot5 = DraggingDot(self, 'depth', False)
		self.dot6 = DraggingDot(self, 'alt', False)
		
		self.type = type
		
		# print("Wall create with type", type)
		
		#self.dot5.setPixmap(QtGui.QPixmap('icons/arrow3.png'))
		
		self.dots = [self.dot1, self.dot2, self.dot3, self.dot4, self.dot5, self.dot6]

		pen = QtGui.QPen()
		brush = QtGui.QBrush(QtGui.QColor(*self.COLOR))
		pen.setWidth(self.LINE_WIDTH)
		pen.setBrush(brush)
		self.normalPen = pen
		
		self.setPen(pen)
		
				
		brush = QtGui.QBrush(QtGui.QColor(255,0,255))
		for dot in self.dots:
			#dot.setVisible(False)
			#if dot is not self.dot5:
			dot.setBrush(brush)
			dot.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True);
			dot.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True);
			
		self.dot5.setBrush(QtGui.QColor(0,255,0))
		self.dot6.setBrush(QtGui.QColor(0,0,255))
		
		pen = QtGui.QPen()
		brush = QtGui.QBrush(QtGui.QColor(255,85,211))
		pen.setWidth(self.LINE_WIDTH + 1)
		pen.setBrush(brush)
		self.selectedPen = pen
		
		
		self.xOffset = xOffset
		self.zOffset = zOffset
		self.coords = {'upperLeft':upperLeft, 'lowerLeft':lowerLeft, 'upperRight':upperRight, 'lowerRight':lowerRight, 'depth':depth, 'alt':alt}

		self.updatePolygon()
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True);
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True);
		
		self.levelEditor = levelEditor
		
		
		
		
		self.addToGroup(self.mainItem)
		self.addToGroup(self.second)
		self.addToGroup(self.line1)
		self.addToGroup(self.line2)
		self.addToGroup(self.line3)
		self.addToGroup(self.line4)
		
		self.setParts()
		#self.addToGroup(self.dot1)
		#self.addToGroup(self.dot2)
		#self.addToGroup(self.dot3)
		#self.addToGroup(self.dot4)
		
		

	def hide(self):
		for dot in self.dots:
			dot.hide()
			
		QtWidgets.QGraphicsItemGroup.hide(self)
		
	def show(self):
		for dot in self.dots:
			dot.show()
			
		QtWidgets.QGraphicsItemGroup.show(self)

		
	def setParts(self):
		if self.BASE_ONLY:
			for item in (self.second, self.line1, self.line2, self.line3, self.line4, self.dot5, self.dot6):
				item.setVisible(False)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
				
				
				
				if item not in (self.dot5, self.dot6):
					#print('y', item.y(), self.y())
					self.removeFromGroup(item)

			
		else:
			for item in (self.second, self.line1, self.line2, self.line3, self.line4, self.dot5, self.dot6):
				item.setVisible(True)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
				if item not in (self.dot5, self.dot6):
					item.setY(self.y())
					item.setX(self.x())
					self.addToGroup(item)
			
		
		
	def copy(self, x, z):
		return Wall(self.levelEditor, int(x), int(z), self.coords['upperLeft'], self.coords['lowerLeft'], self.coords['upperRight'], self.coords['lowerRight'], self.coords['depth'], self.coords['alt'])
		
	def itemChange(self, change, value):
		if (change == QtWidgets.QGraphicsItem.ItemPositionChange and self.scene()):
			self.updating = True
			newPos = value
			xDist = newPos.x() - self.pos().x()
			yDist = newPos.y() - self.pos().y()
			#rect = self.scene().sceneRect();
			for dot in self.dots:
				dot.move(xDist, yDist)
			
			#self.dot1.setPos(newPos)
			#self.dot2.setPos(newPos)anim    freespecial11 #Light Hadouken but no need for repeating execution
			#self.dot3.setPos(newPos)
			#self.dot4.setPos(newPos)
			self.updating = False
		elif(change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged):
			if value == 1:
				self.setPen(self.selectedPen)
			else:
				self.setPen(self.normalPen)
			#aDotIsSelected = False
			#for dot in self.dots:
				#if dot.isSelected() :
					#aDotIsSelected = True
					#break
			
			#if not aDotIsSelected:
				#for dot in self.dots:
					#dot.setVisible(value)
			
		return QtWidgets.QGraphicsItem.itemChange(self, change, value);


	def setPen(self, pen):
		self.mainItem.setPen(pen)
		self.second.setPen(pen)
		for line in (self.line1, self.line2, self.line3, self.line4):
			line.setPen(pen)
		
	def updatePolygon(self):
		x1 = int(self.xOffset+self.coords['upperLeft'])
		x2 = int(self.xOffset+self.coords['lowerLeft'])
		x3 = int(self.xOffset+self.coords['lowerRight'])
		x4 = int(self.xOffset+self.coords['upperRight'])
		alt = int(self.coords['alt'])
		
		z1 = int(self.zOffset-self.coords['depth'])
		z2 = int(self.zOffset)
		self.mainItem.setPolygon(QtGui.QPolygonF([
				QtCore.QPoint(x1, z1), 
				QtCore.QPoint(x2, z2),
				QtCore.QPoint(x3, z2),
				QtCore.QPoint(x4, z1)
				]));
		
		
		self.second.setPolygon(QtGui.QPolygonF([
				QtCore.QPoint(x1, z1-alt), 
				QtCore.QPoint(x2, z2-alt),
				QtCore.QPoint(x3, z2-alt),
				QtCore.QPoint(x4, z1-alt)
				]));
		#self.setPolygon(QtGui.QPolygon([QtCore.QPoint(self.upperLeft, -self.coords['depth']), QtCore.QPoint(self.lowerLeft, 0), QtCore.QPoint(self.lowerRight, self.zOffset), QtCore.QPoint(self.upperRight,-self.coords['depth'])]));
			
		self.line1.setLine(x1, z1, x1, z1-alt)
		self.line2.setLine(x2, z2, x2, z2-alt)
		self.line3.setLine(x3, z2, x3, z2-alt)
		self.line4.setLine(x4, z1, x4, z1-alt)
		
		size = self.DOT_SIZE
		if self.movingDot in (self.dot1, self.dot2, self.dot3, self.dot4): # x moving
			rect = self.dot5.rect()
			rect.setX((x1+x4)/2-size/2)
			rect.setWidth(size)
			self.dot5.setRect(rect)
			
			
			rect = self.dot6.rect()
			rect.setX((x1+x4)/2-size/2)
			rect.setWidth(size)
			self.dot6.setRect(rect)
			
			return
			
		if self.movingDot is None:
		
			self.dot1.setRect(x1-size/2, z1-size/2, size, size)
			self.dot2.setRect(x2-size/2, z2-size/2, size, size)
			#self.dot2.setY(z2-size/2)
			self.dot3.setRect(x3-size/2, z2-size/2, size, size)
			self.dot4.setRect(x4-size/2, z1-size/2, size, size)
			self.dot5.setRect((x1+x4)/2-size/2, z1-size/2, size, size)
			#self.dot5.setOffset((x1+x4)/2-size/2, z1-size/2)
			self.dot6.setRect((x1+x4)/2-size/2, z1-size/2-alt, size, size)
			return
			
		
		if self.movingDot is self.dot5: # depth
			rect = self.dot1.rect()
			rect.setY(z1-size/2)
			rect.setHeight(size)
			self.dot1.setRect(rect)
			
			#rect = self.dot2.rect()
			#rect.setY(z2-size/2)
			#rect.setHeight(size)
			#self.dot2.setRect(rect)
			
			rect = self.dot4.rect()
			rect.setY(z1-size/2)
			rect.setHeight(size)
			self.dot4.setRect(rect)
			
			
			rect = self.dot6.rect()
			rect.setY(z1-alt-size/2)
			rect.setHeight(size)
			self.dot6.setRect(rect)
			
		#self.updated.emit()
		
	
	#def contextMenuEvent(self, e):
		#popMenu = QtWidgets.QMenu(self.levelEditor)
		#copy = popMenu.addAction(QtGui.QIcon.fromTheme('edit-copy'), _("Copy"))
		#delete = popMenu.addAction(QtGui.QIcon.fromTheme('list-remove'), _("Close"))
		#action = popMenu.exec_(e.screenPos())
		#if action == delete:
			#for dot in self.dots:
				#self.scene().removeItem(dot)
			#self.scene().removeItem(self)
			#self.levelEditor.walls.remove(self)
		#e.setAccepted(True)
			



	def mousePressEvent(self, event):
		QtWidgets.QGraphicsItemGroup.mousePressEvent(self, event)
		try:
			self.levelEditor.select(self)
		except:
			pass
		
	def mouseReleaseEvent(self, event):
		QtWidgets.QGraphicsItemGroup.mouseReleaseEvent(self, event)
		points = list(self.mainItem.polygon())
		
		print( points)
		print( self.xOffset)
		print( self.coords['upperLeft'])
		print (points[0].x() -self.coords['upperLeft'])
		print (self.x())
		
	def paint(self, painter, option, widget):
		option.state &= ~QtWidgets.QStyle.State_Selected;
		QtWidgets.QGraphicsItemGroup.paint(self, painter, option, widget)
		
		#self.dot1.paint(painter, option, widget) 
		#self.dot2.paint(painter, option, widget) 
		#self.dot3.paint(painter, option, widget) 
		#self.dot4.paint(painter, option, widget) 
		
	def getParams(self):
		return self.xOffset + int(self.x()), self.zOffset + int(self.y()), int(self.coords['upperLeft']), int(self.coords['lowerLeft']), int(self.coords['upperRight']), int(self.coords['lowerRight']), int(self.coords['depth']), int(self.coords['alt']), self.type
	
		
	def __str__(self):
		txt = str(self.xOffset + int(self.x())) + ' ' + str(self.zOffset + int(self.y())) + ' ' + str(int(self.coords['upperLeft'])) + ' ' + str(int(self.coords['lowerLeft'])) + ' ' + str(int(self.coords['upperRight'])) +  ' ' + str(int(self.coords['lowerRight'])) + ' ' + str(int(self.coords['depth'])) + ' ' + str(int(self.coords['alt']))
		if(self.type != None):
			txt += ' ' + str(self.type)
			
		return txt
	
class Item2(QtWidgets.QGraphicsPolygonItem): # TODO qgraphicsitemgroup
	def __init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth):
		self.second = QtWidgets.QGraphicsPolygonItem()
		self.line1 = QtWidgets.QGraphicsLineItem()
		self.line2 = QtWidgets.QGraphicsLineItem()
		self.line3 = QtWidgets.QGraphicsLineItem()
		self.line4 = QtWidgets.QGraphicsLineItem()
		QtWidgets.QGraphicsPolygonItem.__init__(self)
		self.xOffset = xOffset
		self.zOffset = zOffset
		self.upperLeft = upperLeft
		self.lowerLeft = lowerLeft
		self.upperRight = upperRight
		self.lowerRight = lowerRight
		self.depth = depth
		self.alt = 100
		self.updatePolygon()
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True);
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True);
		
		self.levelEditor = levelEditor
		
		
		
		
	def updatePolygon(self):
		x1 = self.xOffset+self.upperLeft
		x2 = self.xOffset+self.lowerLeft
		x3 = self.xOffset+self.lowerRight
		x4 = self.xOffset+self.upperRight
		
		z1 = self.zOffset-self.depth
		z2 = self.zOffset
		self.setPolygon(QtGui.QPolygonF([
				QtCore.QPoint(x1, z1), 
				QtCore.QPoint(x2, z2),
				QtCore.QPoint(x3, z2),
				QtCore.QPoint(x4, z1)
				]));
		
		
		self.second.setPolygon(QtGui.QPolygonF([
				QtCore.QPoint(x1, z1-self.alt), 
				QtCore.QPoint(x2, z2-self.alt),
				QtCore.QPoint(x3, z2-self.alt),
				QtCore.QPoint(x4, z1-self.alt)
				]));
		#self.setPolygon(QtGui.QPolygon([QtCore.QPoint(self.upperLeft, -self.depth), QtCore.QPoint(self.lowerLeft, 0), QtCore.QPoint(self.lowerRight, self.zOffset), QtCore.QPoint(self.upperRight,-self.depth)]));
			
		self.line1 = QtWidgets.QGraphicsLineItem(x1, z1, x1, z1-self.alt)
		self.line2 = QtWidgets.QGraphicsLineItem(x2, z2, x2, z2-self.alt)
		self.line3 = QtWidgets.QGraphicsLineItem(x3, z2, x3, z2-self.alt)
		self.line4 = QtWidgets.QGraphicsLineItem(x4, z1, x4, z1-self.alt)
		


	def mousePressEvent(self, event):
		QtWidgets.QGraphicsPolygonItem.mousePressEvent(self, event)
		self.levelEditor.select(self)
		
	def mouseReleaseEvent(self, event):
		QtWidgets.QGraphicsPolygonItem.mouseReleaseEvent(self, event)
		points = list(self.polygon())
		
		print( points)
		print( self.xOffset)
		print( self.upperLeft)
		print (points[0].x() -self.upperLeft)
		print (self.x())
		
	def paint(self, painter, option, widget):
		QtWidgets.QGraphicsPolygonItem.paint(self, painter, option, widget)
		QtWidgets.QGraphicsPolygonItem.paint(self.second, painter, option, widget)
		
		self.line1.paint(painter, option, widget) 
		self.line2.paint(painter, option, widget) 
		self.line3.paint(painter, option, widget) 
		self.line4.paint(painter, option, widget) 
		
	def __str__(self):
		return str(self.xOffset + int(self.x())) + ' ' + str(self.zOffset + int(self.y())) + ' ' + str(self.upperLeft) + ' ' + str(self.lowerLeft) + ' ' + str(self.upperRight) +  ' ' + str(self.lowerRight) + ' ' + str(self.depth) + ' ' + '2000'
		

class Hole(Wall):
	BASE_ONLY = True
	COLOR = (0,85,211)
	
	def __init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth, alt, type):
		Wall.__init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth)
		
		self.alt = alt
		self.type = type
		self.com = ''
		
		self.mainItem.setOpacity(0.2)
		self.mainItem.setBrush(QtGui.QColor(0,0,0))
		
		brush = QtGui.QBrush(QtGui.QColor(100,100,100))
		for dot in self.dots:
			#dot.setVisible(False)
			#if dot is not self.dot5:
			dot.setBrush(brush)
			
	def __str__(self):
		line = str(self.xOffset + int(self.x())) + ' ' + str(self.zOffset + int(self.y())) + ' ' + str(int(self.coords['upperLeft'])) + ' ' + str(int(self.coords['lowerLeft'])) + ' ' + str(int(self.coords['upperRight'])) +  ' ' + str(int(self.coords['lowerRight'])) + ' ' + str(int(self.coords['depth']))
		if(self.alt != None):
			line += ' ' + str(self.alt)
		if(self.type != None):
			line += ' ' + str(self.type)
			
		if(self.com != ''):
			line += ' #' + self.com
			
		return line
	
class Basemap(QtWidgets.QGraphicsItemGroup): # TODO qgraphicsitemgroup

	BASE_ONLY = False
	COLOR = (186,85,211)
	LINE_WIDTH = settings.get_option('level/line_weight', 2)
	DOT_SIZE = settings.get_option('level/dot_size', 10)

	def __init__(self, levelEditor, xOffset, zOffset, xSize, zSize, aMin, aMax):
		self.updating = False
		self.movingDot = None
		QtWidgets.QGraphicsPolygonItem.__init__(self)
		self.setFlag(QtWidgets.QGraphicsItem.ItemSendsGeometryChanges)
		
		self.mainItem = QtWidgets.QGraphicsPolygonItem()
		self.second = QtWidgets.QGraphicsPolygonItem()
		self.line1 = QtWidgets.QGraphicsLineItem()
		self.line2 = QtWidgets.QGraphicsLineItem()
		self.line3 = QtWidgets.QGraphicsLineItem()
		self.line4 = QtWidgets.QGraphicsLineItem()
		
		self.dot1 = DraggingDot(self, 'xSize')
		self.dot2 = DraggingDot(self, 'zSize', False)
		self.dot3 = DraggingDot(self, 'aMin', False)
		self.dot4 = DraggingDot(self, 'aMax', False)

		
		#self.dot5.setPixmap(QtGui.QPixmap('icons/arrow3.png'))
		
		self.dots = [self.dot1, self.dot2, self.dot3, self.dot4]

		pen = QtGui.QPen()
		brush = QtGui.QBrush(QtGui.QColor(*self.COLOR))
		pen.setWidth(self.LINE_WIDTH)
		pen.setBrush(brush)
		self.normalPen = pen
		
		self.setPen(pen)
		
				
		brush = QtGui.QBrush(QtGui.QColor(255,0,255))
		for dot in self.dots:
			#dot.setVisible(False)
			#if dot is not self.dot5:
			dot.setBrush(brush)
			dot.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True);
			dot.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True);
			

		self.dot2.setBrush(QtGui.QColor(0,255,0))
		self.dot3.setBrush(QtGui.QColor(0,0,255))
		self.dot4.setBrush(QtGui.QColor(0,0,255))
		
		pen = QtGui.QPen()
		brush = QtGui.QBrush(QtGui.QColor(255,85,211))
		pen.setWidth(self.LINE_WIDTH + 1)
		pen.setBrush(brush)
		self.selectedPen = pen
		
		
		self.xOffset = xOffset
		self.zOffset = zOffset
		self.coords = {'xSize':xSize, 'zSize':zSize, 'aMin':aMin, 'aMax':aMax}

		self.updatePolygon()
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True);
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True);
		
		self.levelEditor = levelEditor
		
		
		
		
		self.addToGroup(self.mainItem)
		self.addToGroup(self.second)
		self.addToGroup(self.line1)
		self.addToGroup(self.line2)
		self.addToGroup(self.line3)
		self.addToGroup(self.line4)
		
		self.setParts()
		#self.addToGroup(self.dot1)
		#self.addToGroup(self.dot2)
		#self.addToGroup(self.dot3)
		#self.addToGroup(self.dot4)
		
		

		
	def setParts(self):
		if self.BASE_ONLY:
			for item in (self.second, self.line1, self.line2, self.line3, self.line4):
				item.setVisible(False)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
				
				
				
				#if item not in (self.dot5, self.dot6):
					#print('y', item.y(), self.y())
				self.removeFromGroup(item)

			
		else:
			for item in (self.second, self.line1, self.line2, self.line3, self.line4):
				item.setVisible(True)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
				item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
				#if item not in (self.dot5, self.dot6):
				item.setY(self.y())
				item.setX(self.x())
				self.addToGroup(item)
			
		
		
	def copy(self, x, z):
		return Wall(self.levelEditor, int(x), int(z), self.coords['upperLeft'], self.coords['lowerLeft'], self.coords['upperRight'], self.coords['lowerRight'], self.coords['depth'], self.coords['alt'])
		
	def itemChange(self, change, value):
		if (change == QtWidgets.QGraphicsItem.ItemPositionChange and self.scene()):
			self.updating = True
			newPos = value
			xDist = newPos.x() - self.pos().x()
			yDist = newPos.y() - self.pos().y()
			#rect = self.scene().sceneRect();
			for dot in self.dots:
				dot.move(xDist, yDist)
			
			#self.dot1.setPos(newPos)
			#self.dot2.setPos(newPos)
			#self.dot3.setPos(newPos)
			#self.dot4.setPos(newPos)
			self.updating = False
		elif(change == QtWidgets.QGraphicsItem.ItemSelectedHasChanged):
			if value == 1:
				self.setPen(self.selectedPen)
			else:
				self.setPen(self.normalPen)
			#aDotIsSelected = False
			#for dot in self.dots:
				#if dot.isSelected() :
					#aDotIsSelected = True
					#break
			
			#if not aDotIsSelected:
				#for dot in self.dots:
					#dot.setVisible(value)
			
		return QtWidgets.QGraphicsItem.itemChange(self, change, value);


	def setPen(self, pen):
		self.mainItem.setPen(pen)
		self.second.setPen(pen)
		for line in (self.line1, self.line2, self.line3, self.line4):
			line.setPen(pen)
		
	def updatePolygon(self):
		x1 = self.xOffset
		x2 = self.xOffset
		x3 = self.xOffset+self.coords['xSize']
		x4 = self.xOffset+self.coords['xSize']
		aMin = self.coords['aMin']
		aMax = self.coords['aMax']
		
		z1 = self.zOffset-self.coords['zSize']
		z2 = self.zOffset
		self.mainItem.setPolygon(QtGui.QPolygonF([
				QtCore.QPoint(x1, z1), 
				QtCore.QPoint(x2, z2),
				QtCore.QPoint(x3, z2),
				QtCore.QPoint(x4, z1)
				]));
		
		
		self.second.setPolygon(QtGui.QPolygonF([
				QtCore.QPoint(x1, z1-aMin), 
				QtCore.QPoint(x2, z2-aMin),
				QtCore.QPoint(x3, z2-aMax),
				QtCore.QPoint(x4, z1-aMax)
				]));
		#self.setPolygon(QtGui.QPolygon([QtCore.QPoint(self.upperLeft, -self.coords['depth']), QtCore.QPoint(self.lowerLeft, 0), QtCore.QPoint(self.lowerRight, self.zOffset), QtCore.QPoint(self.upperRight,-self.coords['depth'])]));
			
		self.line1.setLine(x1, z1, x1, z1-aMin)
		self.line2.setLine(x2, z2, x2, z2-aMin)
		self.line3.setLine(x3, z2, x3, z2-aMax)
		self.line4.setLine(x4, z1, x4, z1-aMax)
		
		size = self.DOT_SIZE
		if self.movingDot in (self.dot1,): # x moving
			rect = self.dot2.rect()
			rect.setX((x1+x4)/2-size/2)
			rect.setWidth(size)
			self.dot2.setRect(rect)
			
			
			rect = self.dot3.rect()
			rect.setX(x1-size/2)
			rect.setWidth(size)
			self.dot3.setRect(rect)
			
			rect = self.dot4.rect()
			rect.setX(x4-size/2)
			rect.setWidth(size)
			self.dot4.setRect(rect)
			
			return
			
		if self.movingDot is None:
		
			self.dot1.setRect(x3-size/2, z1-size/2, size, size)
			self.dot2.setRect((x1+x4)/2-size/2, z1-size/2, size, size)
			#self.dot2.setY(z2-size/2)
			self.dot3.setRect(x1-size/2, z1-size/2-aMin, size, size)
			self.dot4.setRect(x4-size/2, z1-size/2-aMax, size, size)
			
			
			
			return
			
		
		if self.movingDot is self.dot2: # depth
			rect = self.dot1.rect()
			rect.setY(z1-size/2)
			rect.setHeight(size)
			self.dot1.setRect(rect)
			
			#rect = self.dot2.rect()
			#rect.setY(z2-size/2)
			#rect.setHeight(size)
			#self.dot2.setRect(rect)
			
			#rect = self.dot4.rect()
			#rect.setY(z1-size/2)
			#rect.setHeight(size)
			#self.dot4.setRect(rect)
			
			
			rect = self.dot3.rect()
			rect.setY(z1-aMin-size/2)
			rect.setHeight(size)
			self.dot3.setRect(rect)
			
			rect = self.dot4.rect()
			rect.setY(z1-aMax-size/2)
			rect.setHeight(size)
			self.dot4.setRect(rect)
		
	
	#def contextMenuEvent(self, e):
		#popMenu = QtWidgets.QMenu(self.levelEditor)
		#copy = popMenu.addAction(QtGui.QIcon.fromTheme('edit-copy'), _("Copy"))
		#delete = popMenu.addAction(QtGui.QIcon.fromTheme('list-remove'), _("Close"))
		#action = popMenu.exec_(e.screenPos())
		#if action == delete:
			#for dot in self.dots:
				#self.scene().removeItem(dot)
			#self.scene().removeItem(self)
			#self.levelEditor.walls.remove(self)
		#e.setAccepted(True)
			



	def mousePressEvent(self, event):
		QtWidgets.QGraphicsItemGroup.mousePressEvent(self, event)
		self.levelEditor.select(self)
		
	#def mouseReleaseEvent(self, event):
		#QtWidgets.QGraphicsItemGroup.mouseReleaseEvent(self, event)
		#points = list(self.mainItem.polygon())
		
		#print( points)
		#print( self.xOffset)
		#print( self.coords['upperLeft'])
		#print (points[0].x() -self.coords['upperLeft'])
		#print (self.x())
		
	def paint(self, painter, option, widget):
		option.state &= ~QtWidgets.QStyle.State_Selected;
		QtWidgets.QGraphicsItemGroup.paint(self, painter, option, widget)
		
		#self.dot1.paint(painter, option, widget) 
		#self.dot2.paint(painter, option, widget) 
		#self.dot3.paint(painter, option, widget) 
		#self.dot4.paint(painter, option, widget) 
		
		
	
	def __str__(self):
		return str(self.xOffset + int(self.x())) + ' ' + str(self.zOffset + int(self.y())) + ' ' + str(int(self.coords['xSize'])) + ' ' + str(int(self.coords['zSize'])) + ' ' + str(int(self.coords['aMin'])) +  ' ' + str(int(self.coords['aMax']))
	
	
class FontObject(QtWidgets.QGraphicsItemGroup):
	
	def __init__(self, text, fontSprite=None):
		QtWidgets.QGraphicsItemGroup.__init__(self)
		
		self.fontSprite = fontSprite
		self.loadFont()
		
		yOffset = 0
		
		i = 0
		for letter in text:
			
			letter_pos = self.letters.find(letter)
			
			#print("letter is", letter, letter_pos)
			
			if(letter_pos != -1):
				
				px = self.charsPX[letter_pos]
		
				item = QtWidgets.QGraphicsPixmapItem(px)
				item.setPos(i*(self.charWidth), yOffset)
				
				self.addToGroup(item)
			i+=1
	
	
	def loadFont(self):
		#FONT WORK
		
		print('font path', Entity.ROOT_PATH + '/sprites/font.gif')
		
		fonts = [ {'path':Entity.ROOT_PATH + 'data/sprites/font.gif', 'yOffset':-400},
				 {'path':'/home/piccolo/workspace/OpenBOR/tmp/data/sprites/font2.gif', 'yOffset':-300},
			{'path':'/home/piccolo/workspace/OpenBOR/tmp/data/sprites/font4.gif', 'yOffset':-200},
			{'path':'/home/piccolo/workspace/OpenBOR/tmp/data/sprites/font6.gif', 'yOffset':-100}
			]
		
		
		
		if(self.fontSprite != None):
			fontData = {'path':self.fontSprite, 'yOffset':-400}
		else:
		
			fontData = fonts[0]
		
			
		fontImage = loadSprite(fontData['path'])
		charWidth = int(fontImage.width() / 16)
		self.charWidth = charWidth
		charHeight = int(fontImage.height() / 16)
		# charHeight = charWidth
		print("charWidth", charWidth)
		
		x = 0
		y = 0
		
		# letters = '0 1 2 3 4 5 6 7 8 9 A B C D E F 0 1 2 3 4 5 6 7 8 9 A B C D E F ! " # $ % & Â´ ( )  * + , - . / 0 1 2 3 4 5 6 7 8 9 : ; { = } ? @ A B C D E F G H I J K L M N O P Q R S T U V W X Y Z [ \ ] ^ ` a b c d e f g h i j k l m n o p q r s t u v w x y z'
		# letters = letters.replace(' ', '')
		
		letters = '0123456789ABCDEF0123456789ABCDEF!"#$%&Â´()*+,-./0123456789:;{=}?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^ `abcdefghijklmnopqrstuvwxyz'
		self.letters = letters
		
		charsPX = []
		
		for y in range(8):
			for i in range(16):
			
		
				charIMG = fontImage.copy(i*charWidth, y*charHeight, charWidth, charHeight)
			
				px = QtGui.QPixmap.fromImage(charIMG)
				
				charsPX.append(px)
				
				#item = QtWidgets.QGraphicsPixmapItem(px)
				#item.setPos(i*(charWidth+5), y*(charHeight+5))
				#self.scene.addItem(item)
				
		self.charsPX = charsPX
		
		
	def writeText(self):
		phrase_to_draw = "This test sentence was built"
		phrase_to_draw2 = "with CMT font parser"
		
		# phrase_to_draw = "01 ABC"
		
		
		yOffset = fontData['yOffset']
		i = 0
		for letter in phrase_to_draw:
			
			letter_pos = letters.find(letter)
			
			print("letter is", letter, letter_pos)
			
			if(letter_pos != -1):
				
				px = charsPX[letter_pos]
		
				item = QtWidgets.QGraphicsPixmapItem(px)
				item.setPos(i*(charWidth+5), yOffset)
				self.scene.addItem(item)
			i+=1
		
		i = 0
		for letter in phrase_to_draw2:
			
			letter_pos = letters.find(letter)
			
			print("letter is", letter, letter_pos)
			
			if(letter_pos != -1):
				
				px = charsPX[letter_pos]
		
				item = QtWidgets.QGraphicsPixmapItem(px)
				item.setPos(i*(charWidth+5), yOffset+charHeight+5)
				self.scene.addItem(item)
			i+=1
