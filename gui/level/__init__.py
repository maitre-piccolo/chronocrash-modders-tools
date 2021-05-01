import os, re

from PyQt5 import QtCore, QtGui, QtWidgets

from common import settings
from gui.util import FileInput, loadSprite

from data import ParsedLine
from gui.level.items import Wall, Hole, Basemap, Group, Wait, Entity

class LevelEditorWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.setContentsMargins(0, 0, 0, 0)
			
		layout = QtWidgets.QHBoxLayout()
		self.setLayout(mainLayout)
	
		view = ImageWidget()
		view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		scene = LevelScene(self)
		self.scene = scene

		self.buttonBar = QtWidgets.QToolBar()
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('zoom-in'), None, view.zoomIn)
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('zoom-out'), None, view.zoomOut)
		mainLayout.addWidget(self.buttonBar, 0)
		mainLayout.addLayout(layout)
		view.setScene(scene)
		layout.addWidget(view, 1)
		
		self.levelControlWidget = LevelControlWidget(self)
		self.wallControlWidget = WallControlWidget(self)
		layout.addWidget(self.wallControlWidget, 0)
		layout.addWidget(self.levelControlWidget, 0)
		self.wallControlWidget.hide()
		
		self.walls = []
		
		self.scene.selectionChanged.connect(self.selectionChanged)
		
	
		
		
	def loadLines(self, lines):
		self.lines = lines
		self.wallControlWidget.loadLines(lines)
		
		
	'''
		Recreate the text with the current data
	'''
	def rebuildText(self):
		self.updating = True
		newLines = []
		currentWall = 0
		currentHole = 0
		currentBasemap = 0
		currentEntity = 0
		inEntity = False
		for line in self.lines:
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None:
				pass
			elif part.lower() == 'wall':
				wall = self.walls[currentWall]
				currentWall += 1
				if wall.xOffset == 'DELETE':
					continue
				pLine.parts[2:] = [str(wall)]
				line = pLine.getText()
			elif part.lower() == 'hole':
				hole = self.holes[currentHole]
				currentHole += 1
				if hole.xOffset == 'DELETE':
					continue
				pLine.parts[2:] = [str(hole)]
				line = pLine.getText()
			elif part.lower() == 'basemap':
				basemap = self.basemaps[currentBasemap]
				currentBasemap += 1
				if basemap.xOffset == 'DELETE':
					continue
				pLine.parts[2:] = [str(basemap)]
				line = pLine.getText()
			elif part.lower() == 'spawn':
				inEntity = True
				e = self.entities[currentEntity]
			elif part.lower() == 'coords':
				if inEntity:
					e = self.entities[currentEntity]
					x, y = e.getCoords()
					line = 'coords ' + str(x) + ' ' + str(y)
			elif part.lower() == 'at':
				if inEntity:
					e = self.entities[currentEntity]
					line = 'at ' + str(e.at)
					currentEntity += 1
					inEntity = False
					
				
				
			newLines.append(line)
		
		for i in range(currentWall, len(self.walls)):
			wall = self.walls[i]
			line = 'wall ' + str(wall)
			newLines.append(line)
		self.updating = False
		return newLines

		
	def select(self, item):
		print('select', item)
		self.wallControlWidget.show()
		self.wallControlWidget.load(item)
		
	def selectionChanged(self):
		print('selectionChanged', self.scene.selectedItems())
		if(len(self.scene.selectedItems()) == 0):
			self.wallControlWidget.hide()
			if self.levelControlWidget.isVisible():
				self.levelControlWidget.hide()
			else:
				self.levelControlWidget.show()
		else:
			self.levelControlWidget.hide()
			item = self.scene.selectedItems()[0]
			if type(item) == Entity:
				self.wallControlWidget.hide()
		 
			
		
		
		
		
class LevelScene(QtWidgets.QGraphicsScene):
	def __init__(self, parent):
		QtWidgets.QGraphicsScene.__init__(self, parent)
		self.clipboardItem = None
	
	def contextMenuEvent(self, e):
		item = self.itemAt(e.scenePos(), QtGui.QTransform())
		if item is not None:
			group = item.group()
			if group is not None:
				item = group
		popMenu = QtWidgets.QMenu()
		copy = popMenu.addAction(QtGui.QIcon.fromTheme('edit-copy'), _("Copy"))
		if item is None : copy.setEnabled(False)
		paste = popMenu.addAction(QtGui.QIcon.fromTheme('edit-paste'), _("Paste"))
		if self.clipboardItem is None : paste.setEnabled(False)
		delete = popMenu.addAction(QtGui.QIcon.fromTheme('list-remove'), _("Close"))
		if item is None : delete.setEnabled(False)
		action = popMenu.exec_(e.screenPos())
		if action == delete:
			for dot in item.dots:
				self.removeItem(dot)

			#self.parent().walls.remove(item)
			self.removeItem(item)
			item.xOffset = 'DELETE'
		elif action == copy:
			self.clipboardItem = item
		elif action == paste:
			wall = self.clipboardItem.copy(e.scenePos().x(), e.scenePos().y())
			self.parent().walls.append(wall)
			self.addItem(wall)
			for dot in wall.dots:
				self.addItem(dot)
			self.clipboardItem = None
			
		e.setAccepted(True)
		
		
	def mouseMoveEvent(self, e):
		QtWidgets.QGraphicsScene.mouseMoveEvent(self, e)
		self.parent().window().statusBar().showMessage(str((round(e.scenePos().x()), round( e.scenePos().y()))), 2000)

	

class ImageWidget(QtWidgets.QGraphicsView):
	def __init__(self):
		QtWidgets.QGraphicsView.__init__(self)
		
		self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		#self.setInteractive(False)
		self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState | QtWidgets.QGraphicsView.DontAdjustForAntialiasing)
		print (self.optimizationFlags())

		scene = LevelScene(self)
		self.pic = QtGui.QPixmap('icons/8.jpg')
		#scene.addItem(QtWidgets.QGraphicsPixmapItem(pic))
		self.image = QtWidgets.QGraphicsPixmapItem(self.pic)
		#scene.addPixmap(self.pic)
		scene.addItem(self.image)
		self.setScene(scene)
		self.show()
		
		# Data attributes
		#self.zoom = 1 # DEPRECATED
		self.scaleFactor = 1.0
		
		
		self.setMouseTracking(True)
		
	
		
	def loadFile(self, elt):
		path = elt.path
		image= QtGui.QPixmap(path)
		self.scene().setSceneRect(0, 0, image.width(), image.height())
		self.image.setPixmap(image)
		
		
	def wheelEvent(self, e):
		#scene.addItem(QtWidgets.QGraphicsPixmapItem(pic))
		#self.image.setPixmap(pic)
		
		if e.angleDelta().y() > 0:
			self.zoomIn()
			return
			self.image.setPixmap(self.pic.scaled(self.scaleFactor * self.pic.size()))
			#self.scaleImage(1.25)
			
			return
			factor = self.zoom / (self.zoom + 0.1)
			self.zoom += 0.1
		else:
			self.zoomOut()
			return
			self.image.setPixmap(self.pic.scaled(self.scaleFactor * self.pic.size()))
			#self.scaleImage(0.8)
			return
			factor = self.zoom / (self.zoom - 0.1)
			self.zoom -= 0.1
		self.scale(factor, factor)
		
		self.centerOn(e.x(), e.y())
		print( self.zoom)
		print( '')
	
	def scaleImage(self, factor):
		self.scaleFactor *= factor
		self.scale(factor, factor)
		
	def zoom(self, factor):
		self.scaleFactor *= factor
		self.scale(factor, factor)
		
	def zoomIn(self):
		self.zoom(1.25)
		
	def zoomOut(self):
		self.zoom(0.8)
		
		
class WallControlWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.levelEditor = parent
		
		layout = QtWidgets.QFormLayout()
		

		self.setLayout(layout)
		
		#dataPath = settings.get_option('general/datapath', '')
		#lastPath = settings.get_option('level_editor/last_file', '')#.decode('utf-8')
		#if lastPath == '':
			#lookPath = dataPath
		#else:
			#lookPath = os.path.dirname(lastPath)
		#self.levelFile = FileInput('openFile', lastPath, 'Select a .txt level file', lookPath, 'TXT Files (*.txt)')
		#layout.addRow(_('Level file') + ' : ', self.levelFile)
		
		fields = ('xOffset', 'zOffset', 'upperLeft', 'lowerLeft', 'upperRight', 'lowerRight', 'depth', 'alt', 'xSize', 'zSize', 'aMin', 'aMax')
		
		self.lineEdits = {}
		validator = QtGui.QIntValidator()
		for field in fields:
			self.lineEdits[field] = QtWidgets.QLineEdit()
			self.lineEdits[field].setValidator(validator)
			layout.addRow(_(field) + ' : ', self.lineEdits[field])
			

		
	
		button = QtWidgets.QPushButton(_('Update'))
		button.clicked.connect(self.update)
		layout.addRow(button)
		
		
		baseOnly = QtWidgets.QCheckBox(_('Show base only'))
		baseOnly.stateChanged.connect(self.setBaseOnly)
		layout.addRow(baseOnly)
		
		#button = QtWidgets.QPushButton(_('Get wall'))
		#button.clicked.connect(self.getWall)
		#layout.addRow(button)
		
		#button = QtWidgets.QPushButton(_('Load Image'))
		#button.clicked.connect(self.loadImage)
		#layout.addRow(button)
		
		#button = QtWidgets.QPushButton(_('Load Walls'))
		#button.clicked.connect(self.loadWalls)
		#layout.addRow(button)
		self.item = None
		
	def getWall(self):
		print ('wall ' + str(self.item) )
		
		
	def loadBackground(self, parts):
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', ''))
		path = os.path.join(ROOT_PATH, parts[0])
		img = loadSprite(path)
		item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(img));
		self.levelEditor.scene.addItem(item);
		self.levelEditor.backgroundsImages.append(item)
		
	def loadImage(self, path=None):
		if path is None:
			path = '/home/piccolo/workspace/OpenBOR/data/bgs/polar/snow4.png'
			
		img = loadSprite(path)
		#img = QtGui.QImage(path)
		#img = img.convertToFormat(QtGui.QImage.Format_Indexed8)
		#img.setColor(0, QtGui.qRgba(255, 255, 255, 0))
		
		item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(img));
		item.setPos(self.levelEditor.panelPos, 0)
		self.levelEditor.panelPos += item.pixmap().width()
		self.levelEditor.scene.addItem(item);
		print('panel', path)
		
		return item
		
	def loadFrontPanel(self, path=None):
		if path is None:
			path = '/home/piccolo/workspace/OpenBOR/data/bgs/polar/snow4.png'
		#img = QtGui.QImage(path)
		img = loadSprite(path)
		#img = img.convertToFormat(QtGui.QImage.Format_Indexed8)
		#table = img.colorTable()
		#print(img.colorCount())
		#print(table)
		#img.setColor(0, QtGui.qRgba(255, 255, 255, 0))
		#img.setColorTable(table)
		item = QtWidgets.QGraphicsPixmapItem(QtGui.QPixmap.fromImage(img));
		item.setPos(self.levelEditor.frontPanelPos, 0)
		self.levelEditor.frontPanelPos += item.pixmap().width()
		self.levelEditor.scene.addItem(item);
		item.setZValue(1)
		self.levelEditor.panelsImages.append(item)
		
	def loadWalls(self):
		
		self.loadImage()
		#7040 990	0 850	200 1050 250 2000
	
		levelFilePath = self.levelFile.text()
		if(os.path.isfile(levelFilePath)):
			settings.set_option('level_editor/last_file', levelFilePath)
			
		f = open(levelFilePath, 'rU')
		lines = f.readlines()
		

		#lines = re.split('\n', text)
		self.loadLines(lines)
		
	def loadLines(self, lines):
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', ''))
		self.levelEditor.scene.clear()
		self.levelEditor.walls = []
		self.levelEditor.holes = []
		self.levelEditor.basemaps = []
		self.levelEditor.entities = []
		self.levelEditor.backgroundsImages = []
		self.levelEditor.groups = []
		self.levelEditor.panels = []
		self.levelEditor.panelsImages = []
		self.levelEditor.panelPos = 0
		self.levelEditor.frontPanels = []
		self.levelEditor.frontPanelsImages = []
		self.levelEditor.frontPanelPos = 0
		nextAt = None
		for line in lines:
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None: continue
		
		
			if part.lower() == 'at':
				if nextAt == 'group':
					group = self.levelEditor.groups[-1]
					group.at(int(pLine.next()))
					self.levelEditor.scene.addItem(group)
				elif nextAt == 'wait':
					wait = Wait()
					wait.at(int(pLine.next()))
					self.levelEditor.scene.addItem(wait)
				elif nextAt == 'spawn':
					e = self.levelEditor.entities[-1]
					e.setAt(int(pLine.next()))
					self.levelEditor.scene.addItem(e)
		
			elif part.lower() == 'spawn':
				e = Entity(pLine.next())
				self.levelEditor.entities.append(e)
				nextAt = 'spawn'
				
			elif part.lower() == 'coords':
				e = self.levelEditor.entities[-1]
				e.x = int(pLine.next())
				e.y = int(pLine.next())
				
				
			elif part.lower() == 'group':
				parts = []
				while pLine.next() != None:
					parts.append(int(pLine.getCurrent()))
				self.levelEditor.groups.append(Group(*parts))
				nextAt = 'group'
				
			elif part.lower() == 'wait':
				nextAt = 'wait'

			elif part.lower() == 'wall':
				parts = []
				while pLine.next() != None:
					parts.append(int(pLine.getCurrent()))
				while len(parts) < 8:
					parts.append(0)
				wall = Wall(self.levelEditor, *parts)
				self.levelEditor.scene.addItem(wall)
				self.levelEditor.scene.addItem(wall.dot1)
				self.levelEditor.scene.addItem(wall.dot2)
				self.levelEditor.scene.addItem(wall.dot3)
				self.levelEditor.scene.addItem(wall.dot4)
				self.levelEditor.scene.addItem(wall.dot5)
				self.levelEditor.scene.addItem(wall.dot6)
				self.levelEditor.walls.append(wall)
			elif part.lower() == 'hole':
				parts = []
				while pLine.next() != None:
					parts.append(int(pLine.getCurrent()))
				while len(parts) < 7:
					parts.append(0)
				wall = Hole(self.levelEditor, *parts)
				self.levelEditor.scene.addItem(wall)
				self.levelEditor.scene.addItem(wall.dot1)
				self.levelEditor.scene.addItem(wall.dot2)
				self.levelEditor.scene.addItem(wall.dot3)
				self.levelEditor.scene.addItem(wall.dot4)
				self.levelEditor.scene.addItem(wall.dot5)
				self.levelEditor.scene.addItem(wall.dot6)
				self.levelEditor.holes.append(wall)
			elif part.lower() == 'basemap':
				parts = []
				while pLine.next() != None:
					parts.append(int(pLine.getCurrent()))
				while len(parts) < 6:
					parts.append(0)
				wall = Basemap(self.levelEditor, *parts)
				self.levelEditor.scene.addItem(wall)
				self.levelEditor.scene.addItem(wall.dot1)
				self.levelEditor.scene.addItem(wall.dot2)
				self.levelEditor.scene.addItem(wall.dot3)
				self.levelEditor.scene.addItem(wall.dot4)
				self.levelEditor.basemaps.append(wall)
			elif part.lower() in ('background', 'bglayer'):
				parts = []
				while pLine.next() != None:
					parts.append(pLine.getCurrent())
				self.loadBackground(parts)
			elif part.lower() == 'panel':
				path = pLine.next()
				self.levelEditor.panels.append(os.path.join(ROOT_PATH, path))
				
				image = self.loadImage(os.path.join(ROOT_PATH, path))
				self.levelEditor.panelsImages.append(image)
				
			elif part.lower() == 'frontpanel':
				path = pLine.next()
				self.levelEditor.frontPanels.append(os.path.join(ROOT_PATH, path))
				self.loadFrontPanel(os.path.join(ROOT_PATH, path))
				
				
			elif part.lower() == 'order':
				pass

		#scene.addItem(Item(1700, 920, 0, 850, 200, 1050, 250));

		#scene.addItem(Item(1700, 920, 0, 0, 850, 0, 200));
		
		
	def load(self, item):
		self.item = item
		
		self.lineEdits['xOffset'].setText(str(item.xOffset + int(self.item.x())))
		self.lineEdits['zOffset'].setText(str(item.zOffset + int(self.item.y())))
		
		
		if type(item) == Basemap:
			pass
		else: # Walls or Hole
		
			self.lineEdits['upperLeft'].setText(str(int(item.coords['upperLeft'])))
			self.lineEdits['lowerLeft'].setText(str(int(item.coords['lowerLeft'])))
			self.lineEdits['upperRight'].setText(str(int(item.coords['upperRight'])))
			self.lineEdits['lowerRight'].setText(str(int(item.coords['lowerRight'])))
			self.lineEdits['depth'].setText(str(int(item.coords['depth'])))
			self.lineEdits['alt'].setText(str(int(item.coords['alt'])))
		
		
	def setBaseOnly(self, state):
		if state == QtCore.Qt.Checked:
			Wall.BASE_ONLY = True
		else:
			Wall.BASE_ONLY = False
		for wall in self.levelEditor.walls:
			wall.setParts()
			wall.updatePolygon()
			
		
	def update(self):
		if self.item is None: return
		#self.item.xOffset = int(self.lineEdits['xOffset'].text())
		#self.item.zOffset = int(self.lineEdits['zOffset'].text())
		self.item.coords['upperLeft'] = int(self.lineEdits['upperLeft'].text())
		self.item.coords['lowerLeft'] = int(self.lineEdits['lowerLeft'].text())
		self.item.coords['upperRight'] = int(self.lineEdits['upperRight'].text())
		self.item.coords['lowerRight'] = int(self.lineEdits['lowerRight'].text())
		self.item.coords['depth'] = int(self.lineEdits['depth'].text())
		self.item.coords['alt'] = int(self.lineEdits['alt'].text())
		self.item.updatePolygon()
		#print(list (self.item.polygon()))
		
		
class LevelControlWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.levelEditor = parent
		
		layout = QtWidgets.QFormLayout()
		

		self.setLayout(layout)
		
	
		a = QtWidgets.QCheckBox(_('Hide panels'))
		a.stateChanged.connect(self.hidePanels)
		layout.addRow(a)
		
		b = QtWidgets.QCheckBox(_('Hide front panels'))
		b.stateChanged.connect(self.hideFrontPanels)
		layout.addRow(b)
		
		
		c = QtWidgets.QCheckBox(_('Hide backgrounds'))
		c.stateChanged.connect(self.hideBackgrounds)
		layout.addRow(c)
		
		
	def hideBackgrounds(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.backgroundsImages:
				p.hide()
		else:
			for p in self.levelEditor.backgroundsImages:
				p.show()
				
	def hideFrontPanels(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.frontPanelsImages:
				p.hide()
		else:
			for p in self.levelEditor.frontPanelsImages:
				p.show()
		
		
	def hidePanels(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.panelsImages:
				p.hide()
		else:
			for p in self.levelEditor.panelsImages:
				p.show()
			
		

