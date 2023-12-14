import os, re, time

from PyQt5 import QtCore, QtGui, QtWidgets

from common import settings, util
from gui.util import FileInput, loadSprite

from data import ParsedLine, FileWrapper
from gui.level.items import Wall, Hole, Basemap, Group, Wait, Entity, FontObject


PLAYER_MIN_Z = 160
PLAYER_MAX_Z = 232

FRONTPANEL_Z  =  PLAYER_MAX_Z+50
PANEL_Z      =   PLAYER_MIN_Z-50

class LevelEditorWidget(QtWidgets.QWidget):
	
	refresh = QtCore.pyqtSignal()
	
	
	PROJECTS_VARS = {}
	
	RESOLUTIONS = [(320,240), (480,272), (640,480), (720,480), (800,480), (800,600), (960,540)]
	
	
		
	
	
	@classmethod
	def projectChanged(cls, projectRoot=None):
		if(projectRoot != None):
			cls.ROOT_PATH = projectRoot
		else :
			cls.ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', '/home/piccolo/workspace/OpenBOR/data')) + os.sep
		
		
		if(cls.ROOT_PATH in cls.PROJECTS_VARS):
			vars = cls.PROJECTS_VARS[cls.ROOT_PATH]
			
			cls.PIXMAP_CACHE = vars['PIXMAP_CACHE']
			
		else:
			
		
			
			cls.PIXMAP_CACHE = {}
			
			
			vars = {}
			
			vars['PIXMAP_CACHE'] = cls.PIXMAP_CACHE
			
			
			cls.PROJECTS_VARS[cls.ROOT_PATH] = vars

	
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		mainLayout = QtWidgets.QVBoxLayout()
		mainLayout.setContentsMargins(0, 0, 0, 0)
			
		layout = QtWidgets.QHBoxLayout()
		self.setLayout(mainLayout)
	
		self.autoPlayOnLoad = settings.get_option('level/auto_play_on_load', True)
		
		self.entities_types = []
	
		view = ImageWidget()
		view.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		scene = LevelScene(self)
		self.graphicView = view
		self.scene = scene

		self.buttonBar = QtWidgets.QToolBar()
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('zoom-in'), None, view.zoomIn)
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('zoom-out'), None, view.zoomOut)
		self.buttonBar.addSeparator()
		self.buttonBar.addAction(QtGui.QIcon.fromTheme('media-playback-start'), _('Play animations'), self.animateEntities)
		# self.buttonBar.addAction(QtGui.QIcon.fromTheme('media-playback-start'), _('Flip entities'), self.flipEntitiesDirection)
		
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F7", "Flip Opponent")), self, self.flipEntitiesDirection)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F8", "Next Frame")), self, self.nextFrame)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F4", "Next Frame")), self, self.nextFrame)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("right", "Scroll forward")), self, self.scrollForward)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Alt+right", "Scroll forward")), self, self.scrollForwardFast)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Shift+right", "Scroll forward")), self, self.scrollForwardFast)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("left", "Scroll backward")), self, self.scrollBackward)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Alt+left", "Scroll backward")), self, self.scrollBackwardFast)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Shift+left", "Scroll backward")), self, self.scrollBackwardFast)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("up", "Scroll Up")), self, self.scrollUp)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Shift+up", "Scroll Up")), self, self.scrollUpFast)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("down", "Scroll Down")), self, self.scrollDown)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Shift+down", "Scroll Down")), self, self.scrollDownFast)
		
		
		mainLayout.addWidget(self.buttonBar, 0)
		mainLayout.addLayout(layout)
		view.setScene(scene)
		layout.addWidget(view, 1)
		
		
		self.rightPanel = QtWidgets.QTabWidget()
		
		self.levelControlWidget = LevelControlWidget(self)
		self.wallControlWidget = WallControlWidget(self)
		self.entityControlWidget = EntityControlWidget(self)
		
		self.rightPanel.addTab(self.levelControlWidget, _('Level'))
		self.rightPanel.addTab(self.wallControlWidget, _('Wall'))
		self.rightPanel.addTab(self.entityControlWidget, _('Entity'))
		layout.addWidget(self.rightPanel, 0)
		
		
		
		self.walls = []
		
		self.scene.selectionChanged.connect(self.selectionChanged)
		
		self.softWarnings = []
		self.refresh.connect(self.actualizeEntities)
		
		self.videoMode = 0
		self.scrollPosition = 0
		self.scrollPosition_Z = 0
		# hide shadows
		
	def actualizeEntities(self):
		for e in self.entities:
			e.actualizeFrame()
			# self.scene.removeItem(e)
			# self.scene.addItem(e)
	
	def flipEntitiesDirection(self):
		for e in self.entities:
			e.setDirection(not e.facingRight)
			
	def nextFrame(self):
		for e in self.entities:
			e.nextFrame()
			e.actualizeFrame()
	
	def animateEntities(self):
		@util.threaded
		def play():
			delay = 1
			while self.looping:
				for e in self.entities:
					e.tick()
					# for i, frame in enumerate(self.parent.anim):
					# 	if not self.looping or i > len(self.parent.anim) : break
					# 	path = os.path.join(EntityEditorWidget.ROOT_PATH, frame['frame'])
					# 	self.parent.currentFrame = i
					# 	self.refresh.emit()
					# 	if 'delay' in frame:
					# 		delay = frame['delay']
					# 	#self.loadFrame(i)
				time.sleep(delay / 100)
				self.refresh.emit()
		if self.looping:
			self.looping = False
			return
		
		self.looping = True
		
		play()
	
	def logWarning(self, warning):
		self.softWarnings.append(warning)
		text = '\n\n'.join(self.softWarnings)
		self.levelControlWidget.logWidget.setPlainText(text)
		
	def loadVideoMode(self):
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', ''))
		path = os.path.join(ROOT_PATH, 'data', 'video.txt')
		print(path)
		if not os.path.isfile(path):
			print('WARNING : no video.txt')
			return
		
		f = FileWrapper(path)
		lines = f.getLines()
		for i, line in enumerate(lines):
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None : continue
			if part.lower() == 'video':
				part2 = pLine.next()
				if('x' in part2.lower()):
					width, height = part2.lower().split('x')
					LevelEditorWidget.RESOLUTIONS.append((int(width), int(height)))
					# print(width, height)
					self.videoMode = len(LevelEditorWidget.RESOLUTIONS) -1
					# print(self.videoMode)
				else:
					self.videoMode = int(part2)
		
		
	def loadFile(self, fd):
		if(hasattr(fd, 'z')):
			print('THERE IS z')
			self.z = fd.z
		if(hasattr(fd, 'HUD_settings')):
			print('THERE IS HUD_settings')
			self.HUD_settings = fd.HUD_settings
		self.loadLines(fd.lines)
	
	
	def loadLines(self, lines):
		self.loadVideoMode()
		
		
		self.softWarnings = []
		self.lines = lines
		self.wallControlWidget.loadLines(lines)
		self.looping = False
		
		if(self.autoPlayOnLoad):
			self.animateEntities()
		
		self.levelControlWidget.loadHideButtons()
		
	'''
		Recreate the text with the current data
	'''
	def rebuildText(self):
				
			
		self.updating = True
		newLines = []
		currentWall = 0
		currentHole = 0
		currentBasemap = 0
		currentEntity = -1
		inEntity = False
		isInScript = False
		for line in self.lines:
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None:
				pass
			elif part.lower() == '@end_script':
				isInScript = False
			elif isInScript:
				continue
				# processScriptLine()
			elif part.lower() == 'wall':
				inEntity = False
				wall = self.walls[currentWall]
				currentWall += 1
				if wall.xOffset == 'DELETE':
					continue
				pLine.parts[2:] = [str(wall)]
				line = pLine.getText()
			elif part.lower() == 'hole':
				inEntity = False
				hole = self.holes[currentHole]
				currentHole += 1
				if hole.xOffset == 'DELETE':
					continue
				pLine.parts[2:] = [str(hole)]
				line = pLine.getText()
			elif part.lower() == 'basemap':
				inEntity = False
				basemap = self.basemaps[currentBasemap]
				currentBasemap += 1
				if basemap.xOffset == 'DELETE':
					continue
				pLine.parts[2:] = [str(basemap)]
				line = pLine.getText()
			elif part.lower() == 'group':
				inEntity = False
			elif part.lower() == 'spawn':
				currentEntity += 1
				inEntity = True
				e = self.entities[currentEntity]
			elif part.lower() == 'coords':
				if inEntity:
					e = self.entities[currentEntity]
					x, y, alt = e.getCoords()
					line = 'coords ' + str(x) + ' ' + str(y)
					if(alt != None):
						line += ' ' + str(alt)
			elif part.lower() == 'at':
				if inEntity:
					e = self.entities[currentEntity]
					line = 'at ' + str(e.at)
					
					inEntity = False
			
			elif part.lower() == '@script':
				isInScript == True
				
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
			self.rightPanel.setCurrentWidget(self.levelControlWidget)
		else:
			self.levelControlWidget.hide()
			item = self.scene.selectedItems()[0]
			if type(item) == Entity:
				self.rightPanel.setCurrentWidget(self.entityControlWidget)
				self.entityControlWidget.load(item)
		
			elif type(item) == Wall:
				self.rightPanel.setCurrentWidget(self.wallControlWidget)
				
			
		
	def scrollForward(self):
		# modifiers = QtWidgets.QApplication.keyboardModifiers()
		# if modifiers == QtCore.Qt.AltModifier:
		# 	self.scrollPosition += 10
		# else:
		self.scrollPosition += 1
		self.adjustToScrollPos()
		
	def scrollForwardFast(self):
		self.scrollPosition += 10
		self.adjustToScrollPos()
		
	def scrollBackward(self):
		if(self.scrollPosition > 0):
			self.scrollPosition -= 1
			self.adjustToScrollPos()
			
	def scrollBackwardFast(self):
		self.scrollPosition -= 10
		if(self.scrollPosition < 0):
			self.scrollPosition = 0
		self.adjustToScrollPos()
		
		
	def scrollUp(self):
		#if(self.scrollPosition_Z > 0):
		self.scrollPosition_Z -= 1
		self.adjustToScrollPos()
			
	def scrollUpFast(self):
		#if(self.scrollPosition_Z > 0):
		self.scrollPosition_Z -= 10
		self.adjustToScrollPos()
			
	def scrollDown(self):
		#if(self.scrollPosition_Z > 0):
		self.scrollPosition_Z += 1
		self.adjustToScrollPos()
		
	def scrollDownFast(self):
		self.scrollPosition_Z += 10
		self.adjustToScrollPos()
			
			
	def adjustToScrollPos(self):
		self.screenItem.setPos(self.scrollPosition, self.scrollPosition_Z)
		
		for bg in self.backgroundsImages:
			bg.setPos(bg.xRatio*self.scrollPosition + bg.xOffset, bg.zRatio*self.scrollPosition_Z + bg.zOffset ) # bg.pos().y()
			
		for fg in self.frontPanelsImages:
			fg.setPos(fg.xRatio*self.scrollPosition + fg.xOffset, fg.zRatio*self.scrollPosition_Z + fg.zOffset) # fg.pos().y()
		
		
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
		x = round(e.scenePos().x())
		wait = 0
		for waitEntry in self.parent().waits[::-1]:
			if waitEntry <= x:
				wait = waitEntry
				break
			
		distanceFromWait = x - wait
		self.parent().window().statusBar().showMessage(str((x, round( e.scenePos().y()), "from wait :", distanceFromWait)), 2000)

	
	def mousePressEvent(self, event):
		self.parent().looping = False
		QtWidgets.QGraphicsScene.mousePressEvent(self, event)
		
	
	def mouseReleaseEvent(self, event):
		QtWidgets.QGraphicsScene.mouseReleaseEvent(self, event)
		self.selectionChanged.emit()
		
	

class ImageWidget(QtWidgets.QGraphicsView):
	def __init__(self):
		QtWidgets.QGraphicsView.__init__(self)
		
		self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		#self.setInteractive(False)
		self.setOptimizationFlags(QtWidgets.QGraphicsView.DontSavePainterState | QtWidgets.QGraphicsView.DontAdjustForAntialiasing)
		print (self.optimizationFlags())
		
		openGLRendering = settings.get_option('gui/opengl_rendering', False)
		if(openGLRendering):
			gl =  QtWidgets.QOpenGLWidget()
			# QSurfaceFormat format;
			# format.setSamples(4);
			# gl->setFormat(format);
			self.setViewport(gl);

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
	
class EntityControlWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.levelEditor = parent
		
		layout = QtWidgets.QFormLayout()
		

		self.setLayout(layout)
		
		self.nameLabel = QtWidgets.QLabel()
		layout.addRow(self.nameLabel)
		
		self.animLabel = QtWidgets.QLabel()
		layout.addRow(self.animLabel)
		
		self.frameLabel = QtWidgets.QLabel()
		layout.addRow(self.frameLabel)
		
		fields = ('x', 'z', 'altitude (y)', 'at')
		
		self.lineEdits = {}
		validator = QtGui.QIntValidator()
		for field in fields:
			self.lineEdits[field] = QtWidgets.QLineEdit()
			self.lineEdits[field].setValidator(validator)
			layout.addRow(_(field) + ' : ', self.lineEdits[field])
			
		button = QtWidgets.QPushButton(_('Update'))
		button.clicked.connect(self.update)
		layout.addRow(button)
		
		button = QtWidgets.QPushButton(_('Hide'))
		button.clicked.connect(self.hide)
		layout.addRow(button)
		
		self.item = None
		
	def load(self, item):
		self.item = item
		
		fPath = item.frames[item.currentFrame]['path']
		# print(item.currentFrame,  len(item.frames),  fPath)
		image = loadSprite(os.path.join(Entity.ROOT_PATH, fPath))
		# px = QtGui.QPixmap.fromImage(image)
		# self.frameLabel.setPixmap(px)
		px = Entity.PIXMAP_CACHE[item.frames[item.currentFrame]['path']]
		if(px.width() > 300):
			px = px.scaledToWidth(300)
		self.frameLabel.setPixmap(px)
		
		self.nameLabel.setText(item.name)
		self.animLabel.setText(item.animUsed)
		
		x, y, alt = item.getCoords()
		
		self.lineEdits['x'].setText(str(x))
		self.lineEdits['z'].setText(str(y))
		self.lineEdits['at'].setText(str(self.item.at))
		if(alt != None):
			self.lineEdits['altitude (y)'].setText(str(alt))
		else:
			self.lineEdits['altitude (y)'].setText('')
		
		
	
	def hide(self):
		if self.item is None: return
		self.item.hide()
		
	def update(self):
		if self.item is None: return
		#self.item.xOffset = int(self.lineEdits['xOffset'].text())
		#self.item.zOffset = int(self.lineEdits['zOffset'].text())
		self.item.x = int(self.lineEdits['x'].text())
		self.item.z = int(self.lineEdits['z'].text())
		
		if(self.lineEdits['altitude (y)'].text() != ''):
			self.item.altitude = int(self.lineEdits['altitude (y)'].text())
			
		self.item.setAt(int(self.lineEdits['at'].text()))
		
		self.levelEditor.selectionChanged()
		# self.item.update()
		#print(list (self.item.polygon()))
		
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
		#self.levelFile = FileInput(self, 'openFile', lastPath, 'Select a .txt level file', lookPath, 'TXT Files (*.txt)')
		#layout.addRow(_('Level file') + ' : ', self.levelFile)
		
		fields = ('xOffset', 'zOffset', 'upperLeft', 'lowerLeft', 'upperRight', 'lowerRight', 'depth', 'alt', 'xSize', 'zSize', 'aMin', 'aMax', 'type')
		
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
		
		
	def loadBackground(self, parts, transp=0, z=0):
		# 0 : {path} 1{xratio} 2{zratio} 3{xposition} 4{zposition} 5{xspacing} 6{zspacing} 7{xrepeat} 8{zrepeat} {transparency} {alpha} {watermode} {amplitude} {wavelength} {wavespeed} 15:{bgspeedratio}
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', ''))
		path = os.path.join(ROOT_PATH, parts[0])
		
		
		px = self.getPixmap(path, transp)
		
		
		
			
		xRatio = 0.5
		try:
			xRatio = float(parts[1])
		except:
			pass
		
		
		zRatio = 0.5
		try:
			zRatio = float(parts[2])
		except:
			pass
		
		
		bgspeedratio = 0
		try:
			bgspeedratio = float(parts[15])
		except:
			pass
		
		
		xRatio *= bgspeedratio
		
		
		
		xPosition = 0
		try:
			xPosition = int(parts[3])
		except:
			pass
		
		zPosition = 0
		try:
			zPosition = int(parts[4])
		except:
			pass
		
		
		xSpacing = 0
		try:
			xSpacing = int(parts[5])
		except:
			pass
		
		
		xRepeat = 1
		try:
			xRepeat = int(parts[7])
		except:
			pass
		
		if(xRepeat == -1):
			xRepeat = self.fullWidth / (px.width() + xSpacing)
			print("xRepeat was", xRepeat)
			if(xRepeat <= 1):
				xRepeat = 1
		
		print(parts)
		#print("bg xRepeat is", xRepeat, px.width(), self.fullWidth)
		
		
		xOffset = 0
		for i in range(int(xRepeat)):
		
			item = QtWidgets.QGraphicsPixmapItem(px)
			item.xOffset = xOffset
			item.zOffset = 0
			item.xRatio = xRatio
			item.zRatio = zRatio
			item.setPos(xPosition+xOffset, zPosition)
			self.levelEditor.scene.addItem(item)
			# item.setZValue(zPosition)
			item.setZValue(z)
			
			self.levelEditor.backgroundsImages.append(item)
			xOffset += px.width()  + xSpacing
		
	def getPixmap(self, path, transp=0):
		if(path not in LevelEditorWidget.PIXMAP_CACHE):
			
			img = loadSprite(path, transp)
			#img = QtGui.QImage(path)
			#img = img.convertToFormat(QtGui.QImage.Format_Indexed8)
			#img.setColor(0, QtGui.qRgba(255, 255, 255, 0))
			LevelEditorWidget.PIXMAP_CACHE[path] = QtGui.QPixmap.fromImage(img)
			
			# img = loadSprite(path)
			#img = img.convertToFormat(QtGui.QImage.Format_Indexed8)
			#table = img.colorTable()
			#print(img.colorCount())
			#print(table)
			#img.setColor(0, QtGui.qRgba(255, 255, 255, 0))
			#img.setColorTable(table)
			
		return LevelEditorWidget.PIXMAP_CACHE[path]
		
	def loadImage(self, path=None, transp=0):
		if path is None:
			path = '/home/piccolo/workspace/OpenBOR/data/bgs/polar/snow4.png'
		
		
		
		
		
		item = QtWidgets.QGraphicsPixmapItem(self.getPixmap(path, transp));
		item.setPos(self.levelEditor.panelPos, 0)
		item.setZValue(-1)
		self.levelEditor.panelPos += item.pixmap().width()
		self.levelEditor.scene.addItem(item);
		print('panel', path)
		
		return item
		
	def loadFrontPanel(self, parts=[], type="frontpanel", transp=0):
		# fglayer 0{path} 1{z} 2{xratio} 3{zratio} 4{xposition} 5{zposition} {xspacing} {zspacing} {xrepeat} {zrepeat} {transparency} {alpha} {watermode} {amplitude} {wavelength} {wavespeed} {bgspeedratio}
		
		path = '/home/piccolo/workspace/OpenBOR/data/bgs/polar/snow4.png'
		try:
			ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', ''))
			path = os.path.join(ROOT_PATH, parts[0])
		except:
			pass
		
		
			
		#img = QtGui.QImage(path)
		
		z = FRONTPANEL_Z
		try:
			z += int(parts[1])
		except:
			pass
		
		
		
		xRatio = 1
		try:
			xRatio = float(parts[2])
		except:
			pass
		
		if(type == 'frontpanel'):
			xRatio = -0.4
		
		
		zRatio = 1
		try:
			zRatio = float(parts[3])
		except:
			pass
		
		
		
		xPosition = 0
		try:
			xPosition = int(parts[4])
		except:
			pass
		
		zPosition = 0
		try:
			zPosition = int(parts[5])
		except:
			pass
		
		
		xSpacing = 0
		try:
			xSpacing = int(parts[6])
		except:
			pass
			
		
		xRepeat = 1
		try:
			xRepeat = int(parts[8])
		except:
			pass
		
		
		px = self.getPixmap(path, transp)
		
		if(xRepeat == -1):
			xRepeat = self.fullWidth / (px.width() + xSpacing)
			print("xRepeat was", xRepeat)
			if(xRepeat <= 1):
				xRepeat = 1
			
			
		print("xRepeat is", xRepeat)
		
		
		xOffset = 0
		for i in range(int(xRepeat)):
		
			item = QtWidgets.QGraphicsPixmapItem(px)
			item.xRatio = xRatio
			item.zRatio = zRatio
			item.xOffset = xOffset
			item.zOffset = 0
			if(type == 'frontpanel'):
				item.setPos(self.levelEditor.frontPanelPos, 0)
				self.levelEditor.frontPanelPos += item.pixmap().width()
			else:
				item.setPos(xPosition+xOffset, zPosition)
			self.levelEditor.scene.addItem(item)
			item.setZValue(z)
			self.levelEditor.panelsImages.append(item)
			self.levelEditor.frontPanelsImages.append(item)
			
			xOffset += px.width() + xSpacing
		
	def loadWalls(self):
		
		self.loadImage()
		#7040 990	0 850	200 1050 250 2000
	
		levelFilePath = self.levelFile.text()
		if(os.path.isfile(levelFilePath)):
			settings.set_option('level_editor/last_file', levelFilePath)
			
		# f = open(levelFilePath, 'rU')
		# lines = f.readlines()
		
		f = FileWrapper(levelFilePath)
		lines = f.getLines()
		

		#lines = re.split('\n', text)
		self.loadLines(lines)
		
		
	def getTransp(self, pLine):
		com = pLine.getCom()
				
				
		transp = 0
		if('transp=' in com):
			parts = com.split('transp=')
			part = parts[1]
			parts = part.split(';')
			transp = parts[0]
			
		return transp
		
	def loadLines(self, lines):
		def processScriptLine():
			ogLine = pLine.line
			# print('script', ogLine)
			ogLineWithoutSpace = ''.join(ogLine.split())
			parts = ogLineWithoutSpace.split(';') # in case there is mutiple calls
			ogLineWithoutSpace = parts[0]
			parts = ogLineWithoutSpace.split('(')
			if(parts[0].startswith('performattack')):
				
				aniID = ogLineWithoutSpace.split(',')[1]
				result = re.search('"ANI_(.*)"', aniID)
				aniID = result.group(1)
				# print(e.name, aniID)
				e.changeAnimation(aniID, True)
			elif(parts[0].startswith('changeentityproperty')):
				# changeentityproperty(self, "animation", openborconstant("ANI_FREESPECIAL1")); // Another man
				parts = ogLineWithoutSpace.split(',')
				if('"animation"' not in parts[1]): return
				aniID = parts[2]
				result = re.search('"ANI_(.*)"', aniID)
				aniID = result.group(1)
				# print(e.name, aniID)
				e.changeAnimation(aniID, True)
			elif(parts[0].startswith('setentityvar')):
				# setentityvar(getlocalvar("self"), "activeAnimationID", openborconstant("ANI_freespecial2"));
				
				parts = ogLineWithoutSpace.split(',')
				if('"activeAnimationID"' not in parts[1]): return
				aniID = parts[2]
				result = re.search('"ANI_(.*)"', aniID)
				aniID = result.group(1)
				
				# e.changeAnimation(aniID, True, True)
				e.changeAnimation(aniID, True)
				# e.timer = 0
				# e.setAt(0)
				# e.actualizeFrame()
				# print("setentityvar activeAnimationID", e.name, aniID, aniID in e.anims)
				# if('round' in e.name): print(e.anims[aniID])
				
				
		
		ROOT_PATH = os.path.dirname(settings.get_option('general/data_path', ''))
		self.levelEditor.scene.clear()
		
		
		loadEntities = True
		processScript = False
		
		
		self.levelEditor.walls = []
		self.levelEditor.holes = []
		self.levelEditor.basemaps = []
		self.levelEditor.entities = []
		self.levelEditor.entities_types = []
		self.levelEditor.backgrounds = []
		self.levelEditor.backgroundsImages = []
		self.levelEditor.groups = []
		self.levelEditor.panels = []
		self.levelEditor.HUD = []
		self.levelEditor.panelsImages = []
		self.levelEditor.panelPos = 0
		self.levelEditor.frontPanels = []
		self.levelEditor.frontPanelsImages = []
		self.levelEditor.panelOrder = [0]
		self.levelEditor.frontPanelPos = 0
		self.levelEditor.waits = [0]
		nextAt = None
		part = None
		previousFirstPart = None
		e = None
		isInScript = False
		i = 0
		for line in lines:
			i += 1
			pLine = ParsedLine(line)
			previousFirstPart = part
			part = pLine.next()
			if part is None: continue
		
		
			elif part.lower() == '@end_script':
				isInScript = False
			elif part.lower() == '@script':
				isInScript = True
			elif isInScript:
				# continue
				if(loadEntities and processScript): processScriptLine()
			
			if part.lower() == 'at':
				if nextAt == 'group':
					group = self.levelEditor.groups[-1]
					group.at(int(pLine.next()))
					self.levelEditor.scene.addItem(group)
				elif nextAt == 'wait':
					wait = Wait()
					waitPos = int(pLine.next())
					wait.at(waitPos)
					self.levelEditor.waits.append(waitPos)
					self.levelEditor.scene.addItem(wait)
				elif nextAt == 'spawn':
					if(loadEntities):
						e = self.levelEditor.entities[-1]
						e.setAt(int(pLine.next()))
						self.levelEditor.scene.addItem(e)
				elif nextAt == None and previousFirstPart not in ('light', 'music', 'shadowopacity', 'scrollx', 'shadowcolor' ):
					self.levelEditor.logWarning('Problem at line ' + str(i) + ' : orphan "at", skipped.')
				nextAt = None
		
			elif part.lower() == 'spawn':
				# before moving on to this spawn point, we review beforehand if last spawn point was properly declared
				if e != None:
					if e.at == None:
						self.levelEditor.logWarning('Problem with spawn point : Entity ' + e.name + ' at line ' + str(e.line) + ' has no "at" set')
							
					if e.x == None:
						self.levelEditor.logWarning('Problem with spawn point : Entity ' + e.name + ' at line ' + str(e.line) + ' has no "coords" set')
				
				if(loadEntities):
					e = Entity(pLine.next(), i, self.levelEditor, defaultAnim="idle", loadAllAnims=True, offset=True)
					if(e.type not in self.levelEditor.entities_types):
						self.levelEditor.entities_types.append(e.type)
					self.levelEditor.entities.append(e)
				nextAt = 'spawn'
				
			elif part.lower() == 'coords':
				if (nextAt == None):
					self.levelEditor.logWarning('Problem at line ' + str(i) + ' : orphan "coords", skipped.')
					continue
					
				if(loadEntities):
					e = self.levelEditor.entities[-1]
					e.x = int(pLine.next())
					try:
						e.z = int(pLine.next())
					except:
						e.z = 0
						self.levelEditor.logWarning('Problem at line ' + str(i) + ' : z coords missing or not integer.')
					e.altitude = pLine.next()
					if(e.altitude!=None): e.altitude = int(e.altitude)
				
				
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
					part2 = pLine.getCurrent()
					try:
						part2 = int(part2)
					except:
						pass
					parts.append(part2)
				print(parts)
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
					if(len(parts) <7):
						parts.append(int(pLine.getCurrent()))
					else :
						parts.append(pLine.getCurrent())
				while len(parts) < 7:
					parts.append(0)
				while len(parts) < 9:
					parts.append(None)
				wall = Hole(self.levelEditor, *parts)
				wall.com = pLine.getCom()
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
				
				transp = self.getTransp(pLine)
				z = -99999
				#z = 0
				if(part.lower() == 'background'): z = -99999
				
				
				self.levelEditor.backgrounds.append({'parts':parts, 'z':z, 'transp':transp})
				
				
			elif part.lower() == 'panel':
				
				transp = self.getTransp(pLine)
				
				
				path = pLine.next()
				self.levelEditor.panels.append({'path':os.path.join(ROOT_PATH, path), 'transp':transp, 'z-ajust':PANEL_Z})
				
				
				
			elif part.lower() in ('frontpanel', 'fglayer'):
				parts = []
				while pLine.next() != None:
					parts.append(pLine.getCurrent())
					
				transp = self.getTransp(pLine)
				
				self.levelEditor.frontPanels.append({'type':part.lower(), 'parts':parts, 'transp':transp})
				
				
			
				
				
			elif part.lower() == 'order':
				corres = {'a':0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7, 'i':8, 'j':9, 'k':10, 'l':11, 'm':12, 'n':13, 'o':14, 'p':15, 'q':16, 'r':17, 's':18, 't':19, 'u':20, 'v':21, 'w':22, 'x':23, 'y':24, 'z':25}
				order = pLine.next()
				self.levelEditor.panelOrder = []
				for letter in order:
					letterMin = letter.lower()
					self.levelEditor.panelOrder.append(corres[letterMin])

		
		xOffset = 0
		first = True
		for i in self.levelEditor.panelOrder:
			
			panelData = self.levelEditor.panels[i]
			
			image = self.loadImage(panelData['path'], panelData['transp'])
			
			if(first):
			
				panelHeight = image.pixmap().height()
			
				width, height = LevelEditorWidget.RESOLUTIONS[self.levelEditor.videoMode]
				print('video mode', width, height, self.levelEditor.videoMode)
				self.levelEditor.screenItem = QtWidgets.QGraphicsRectItem(xOffset, panelHeight-height, width, height)
				self.levelEditor.screenItem.setZValue(PANEL_Z)
				self.levelEditor.screenItem.setPen(QtGui.QPen(QtGui.QColor(255,0,0), 5))
				self.levelEditor.scene.addItem(self.levelEditor.screenItem)
				
				first = False
			
			self.levelEditor.panelsImages.append(image)
			
			xOffset += image.pixmap().width()
		
		
		self.fullWidth = xOffset
		#self.fullWidth = 5000
		
		
		print("self.fullWidth", self.fullWidth)
		
		
			
		
		
		for background in self.levelEditor.backgrounds:
			self.loadBackground(background['parts'], background['transp'], background['z'])
		
		for frontPanel in self.levelEditor.frontPanels:
			self.loadFrontPanel(frontPanel['parts'], frontPanel['type'], frontPanel['transp'])
		#scene.addItem(Item(1700, 920, 0, 850, 200, 1050, 250));

		#scene.addItem(Item(1700, 920, 0, 0, 850, 0, 200));
		
		if(hasattr(self.levelEditor, 'z')):
			print("self.z", self.levelEditor.z)
		
			self.xMin = QtWidgets.QGraphicsLineItem(0.0, float(self.levelEditor.z['xMin']) , float(self.fullWidth), float(self.levelEditor.z['xMin']))
			self.xMin.setZValue(9999)
			self.xMin.setPen(QtGui.QPen(QtGui.QColor(240,140,120)))
			self.levelEditor.scene.addItem(self.xMin)
			
			self.xMax = QtWidgets.QGraphicsLineItem(0.0, float(self.levelEditor.z['xMax']) , float(self.fullWidth), float(self.levelEditor.z['xMax']))
			self.xMax.setZValue(9999)
			self.xMax.setPen(QtGui.QPen(QtGui.QColor(150,100,255)))
			self.levelEditor.scene.addItem(self.xMax)
		
			
			#self.line.setPen(pen)
		if(hasattr(self.levelEditor, 'HUD_settings')):
			HUD = self.levelEditor.HUD_settings
			print('THERE IS HUD_settings 2')
			if('lbarsize' in HUD):
				width = HUD['lbarsize']['width']
				height = HUD['lbarsize']['height']
				for pLife in ['p1life', 'p2life', 'p3life', 'p4life']:
					if(pLife in HUD):
						x = HUD[pLife]['x']
						y = HUD[pLife]['y']
						
						lifeBar = QtWidgets.QGraphicsRectItem(x, y, width, height)
						lifeBar.setZValue(9999)
						lifeBar.setBrush(QtGui.QBrush(QtGui.QColor(0,100,0)))
						lifeBar.setPen(QtGui.QPen(QtGui.QColor(0,100,0)))
						self.levelEditor.scene.addItem(lifeBar)
						self.levelEditor.HUD.append(lifeBar)
						
				for pName in ['p1namej', 'p2namej', 'p3namej', 'p4namej'] :
					x1 = HUD[pName]['x1']
					y1 = HUD[pName]['y1']
					pNameObject = FontObject(pName)
					pNameObject.setZValue(9999)
					pNameObject.setPos(x1, y1)
					self.levelEditor.scene.addItem(pNameObject)
					self.levelEditor.HUD.append(pNameObject)
					
				for pIcon in ['p1icon', 'p2icon', 'p3icon', 'p4icon'] :
					x = HUD[pIcon]['x']
					y = HUD[pIcon]['y']
					lifeBar = QtWidgets.QGraphicsRectItem(x, y, 25, 25)
					lifeBar.setZValue(9999)
					lifeBar.setBrush(QtGui.QBrush(QtGui.QColor(100,100,100)))
					lifeBar.setPen(QtGui.QPen(QtGui.QColor(50,50,50)))
					self.levelEditor.scene.addItem(lifeBar)
					self.levelEditor.HUD.append(lifeBar)
				
			
		
		
		
		
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
			
			
			# print("self.type", item.type)
			if(item.type != None):
				self.lineEdits['type'].setText(str(item.type))
			else:
				self.lineEdits['type'].setText('')
		
		
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
		if(self.lineEdits['type'].text().strip() == ''):
			self.item.type = None
		else:
			self.item.type = self.lineEdits['type'].text()
		self.item.updatePolygon()
		#print(list (self.item.polygon()))
		
		
class LevelControlWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.levelEditor = parent
		
		layout = QtWidgets.QFormLayout()
		
		self.hideButtons = []
		
		self.setLayout(layout)
		
		a = QtWidgets.QCheckBox(_('Cursor drag mode'))
		a.setChecked(True)
		a.stateChanged.connect(self.changeCursorMode)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide HUD'))
		a.stateChanged.connect(self.hideHUD)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide entities'))
		a.stateChanged.connect(self.hideEntities)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide entities offset'))
		a.stateChanged.connect(self.hideEntitiesOffset)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide entities shadow'))
		a.stateChanged.connect(self.hideEntitiesShadow)
		layout.addRow(a)
		
		
		a = QtWidgets.QCheckBox(_('Hide all geometry (walls, ...)'))
		a.stateChanged.connect(self.hideGeometry)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide walls'))
		a.stateChanged.connect(self.hideWalls)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide holes'))
		a.stateChanged.connect(self.hideHoles)
		layout.addRow(a)
		
		a = QtWidgets.QCheckBox(_('Hide basemaps'))
		a.stateChanged.connect(self.hideBasemaps)
		layout.addRow(a)
		
	
		a = QtWidgets.QCheckBox(_('Hide panels'))
		a.stateChanged.connect(self.hidePanels)
		layout.addRow(a)
		
		b = QtWidgets.QCheckBox(_('Hide front panels'))
		b.stateChanged.connect(self.hideFrontPanels)
		layout.addRow(b)
		
		
		c = QtWidgets.QCheckBox(_('Hide backgrounds'))
		c.stateChanged.connect(self.hideBackgrounds)
		layout.addRow(c)
		
		self.logWidget = QtWidgets.QPlainTextEdit('Log...')
		layout.addRow(self.logWidget)
		# self.logWidget.setFixedWidth(300)
		
		self.layout = layout
		
		
	def changeCursorMode(self, state):
		if state == QtCore.Qt.Checked:
			#RubberBandDrag
			self.levelEditor.graphicView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		else:
			self.levelEditor.graphicView.setDragMode(QtWidgets.QGraphicsView.NoDrag)
			
		
		
	def loadHideButtons(self):
		
		for b in self.hideButtons:
			self.layout.removeWidget(b)
		
		self.hideButtons = []
		
		for type in self.levelEditor.entities_types:
			a = QtWidgets.QCheckBox(_('Hide entities [' + type + ']'))
			a.setProperty('entType', type)
			a.stateChanged.connect(self.hideEntityType)
			self.hideButtons.append(a)
			self.layout.addRow(a)
		
		
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
				#print('hide front', p)
				p.hide()
		else:
			for p in self.levelEditor.frontPanelsImages:
				p.show()
		
		
	def hideGeometry(self, state):
		if state == QtCore.Qt.Checked:
			for p in [*self.levelEditor.walls, *self.levelEditor.basemaps, *self.levelEditor.holes]:
				
				p.hide()
		else:
			for p in [*self.levelEditor.walls, *self.levelEditor.basemaps, *self.levelEditor.holes]:
				
				p.show()
		

	def hideBasemaps(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.basemaps:
				
				p.hide()
		else:
			for p in self.levelEditor.basemaps:
				
				p.show()
		
	def hideWalls(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.walls:
				
				p.hide()
		else:
			for p in self.levelEditor.walls:
				
				p.show()
				
	def hideHoles(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.holes:
				
				p.hide()
		else:
			for p in self.levelEditor.holes:
				
				p.show()
			
		
	def hidePanels(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.panelsImages:
				p.hide()
		else:
			for p in self.levelEditor.panelsImages:
				p.show()
	
	def hideHUD(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.HUD:
				p.hide()
		else:
			for p in self.levelEditor.HUD:
				p.show()
	
	def hideEntities(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.entities:
				p.hide()
		else:
			for p in self.levelEditor.entities:
				p.show()
				
		for p in self.hideButtons:
			p.setChecked(state == QtCore.Qt.Checked)
				
				
	def hideEntitiesOffset(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.entities:
				if hasattr(p, 'offset'):
					p.offset.hide()
		else:
			for p in self.levelEditor.entities:
				if hasattr(p, 'offset'):
					p.offset.show()
				
	def hideEntitiesShadow(self, state):
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.entities:
				if hasattr(p, 'shadow'):
					p.shadow.hide()
		else:
			for p in self.levelEditor.entities:
				if hasattr(p, 'shadow'):
					p.shadow.show()
			
	def hideEntityType(self, state):
		entType = self.sender().property('entType')
		if state == QtCore.Qt.Checked:
			for p in self.levelEditor.entities:
				if p.type == entType:
					p.hide()
		else:
			for p in self.levelEditor.entities:
				if p.type == entType:
					p.show()

