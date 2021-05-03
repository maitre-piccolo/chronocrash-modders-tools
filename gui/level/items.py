import os, re, logging

from PyQt5 import QtCore, QtGui, QtWidgets

from common import settings
from gui.util import FileInput, loadSprite

from data import ParsedLine


class Entity(QtWidgets.QGraphicsPixmapItem):
	def __init__(self, entName='rugal'):
		
		print(entName)
		fName = 'data/chars/rugal/2.gif'
		
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', '/home/piccolo/workspace/OpenBOR/data')) + os.sep
		
		path = os.path.join(ROOT_PATH, 'data', 'models.txt')
		if not os.path.isfile(path): return
		f = open(path)
		lines = f.read().split('\n')
		f.close()
		entityModelFound = False
		for i, line in enumerate(lines):
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None : continue
			if part.lower() == 'know' or part.lower() == 'load':
				name = pLine.next()
				path = pLine.next()
				if name != entName : continue
				
				
				
				
				fullPath = os.path.join(ROOT_PATH, path)
				if not os.path.exists(fullPath) : continue
				print(fullPath)
				f = open(fullPath)
				lines2 = f.read().split('\n')
				f.close()
				inIdleAnim = False
				self.xOffset = 0
				self.yOffset = 0
				for i, line2 in enumerate(lines2):
					pLine2 = ParsedLine(line2)
					part = pLine2.next()
					if part == 'anim':
						animName = pLine2.next().lower()
						if animName == 'idle':
							inIdleAnim = True
					elif part == 'offset' and inIdleAnim:
						self.xOffset = int(pLine2.next().lower())
						self.yOffset = int(pLine2.next().lower())
					elif part == 'frame' and inIdleAnim:
						fName = pLine2.next().lower()
						entityModelFound = True
						break
						
		
		if not entityModelFound:
			self.xOffset = 0
			self.yOffset = 0
			logging.debug('Level Editor : entity model not found for : ' + entName + ' (watch for case sensitivity)')

		
		image = loadSprite(os.path.join(ROOT_PATH, fName))
		px = QtGui.QPixmap.fromImage(image)
		QtWidgets.QGraphicsPixmapItem.__init__(self, px)
		
		self.x = 0
		self.y = 0
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, True)
		self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, True)
		
	def setAt(self, at):
		self.at = at
		self.setPos(self.x + self.at - self.xOffset, self.y - self.yOffset)
		
	def getCoords(self):
		return int(self.pos().x()) - self.at + self.xOffset, int(self.pos().y() + self.yOffset)



class Bar(QtWidgets.QGraphicsItemGroup):
	
	
	def at(self, pos):
		
		pen = QtGui.QPen()
		brush = QtGui.QBrush(QtGui.QColor(*self.COLOR))
		pen.setWidth(4)
		pen.setBrush(brush)
		

		
		self.textItem = QtWidgets.QGraphicsTextItem(self.TEXT)
		self.textItem.setPos(pos-10, self.TEXT_POS)
		self.line = QtWidgets.QGraphicsLineItem(pos, self.LINE_Y1 , pos, self.LINE_Y2)
		
		self.textItem.setDefaultTextColor(QtGui.QColor(*self.COLOR))
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

	def __init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth, alt=100):
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
		x1 = self.xOffset+self.coords['upperLeft']
		x2 = self.xOffset+self.coords['lowerLeft']
		x3 = self.xOffset+self.coords['lowerRight']
		x4 = self.xOffset+self.coords['upperRight']
		alt = self.coords['alt']
		
		z1 = self.zOffset-self.coords['depth']
		z2 = self.zOffset
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
		return self.xOffset + int(self.x()), self.zOffset + int(self.y()), int(self.coords['upperLeft']), int(self.coords['lowerLeft']), int(self.coords['upperRight']), int(self.coords['lowerRight']), int(self.coords['depth']), int(self.coords['alt'])
	
		
	def __str__(self):
		return str(self.xOffset + int(self.x())) + ' ' + str(self.zOffset + int(self.y())) + ' ' + str(int(self.coords['upperLeft'])) + ' ' + str(int(self.coords['lowerLeft'])) + ' ' + str(int(self.coords['upperRight'])) +  ' ' + str(int(self.coords['lowerRight'])) + ' ' + str(int(self.coords['depth'])) + ' ' + str(int(self.coords['alt']))
	
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
	
	def __init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth):
		Wall.__init__(self, levelEditor, xOffset, zOffset, upperLeft, lowerLeft, upperRight, lowerRight, depth)
		
		self.mainItem.setOpacity(0.2)
		self.mainItem.setBrush(QtGui.QColor(0,0,0))
		
		brush = QtGui.QBrush(QtGui.QColor(100,100,100))
		for dot in self.dots:
			#dot.setVisible(False)
			#if dot is not self.dot5:
			dot.setBrush(brush)
			
	def __str__(self):
		return str(self.xOffset + int(self.x())) + ' ' + str(self.zOffset + int(self.y())) + ' ' + str(int(self.coords['upperLeft'])) + ' ' + str(int(self.coords['lowerLeft'])) + ' ' + str(int(self.coords['upperRight'])) +  ' ' + str(int(self.coords['lowerRight'])) + ' ' + str(int(self.coords['depth']))
	
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
