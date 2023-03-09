import os, logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from guilib.treemodel import TreeModel, TreeItem, FilterModel
from operator import attrgetter

from common import settings, xdg
from data import ParsedLine, FileWrapper, Cache
from gui.modales import CreateFileDialog

from gui.util import FileInput, loadSprite
from gui.level.items import Entity


SELECTED_COLOR = [100,100,255];

class File:
	def __init__(self, path=None):
		if path is not None:
			self.name = os.path.basename(path)
		else:
			self.name = 'Unknown'
		self.path = path
		self.lines = None
		self.originalLines = None
		self.saved = True
		self.iconPath = None
		self.category = 'File'
		self.state = 0
		self.isVisible = False
		self.isAddedToAView = False
		
		
	def getLongText(self):
		if self.path is not None: return self.path
		else: return self.name
		
		
	@staticmethod
	def fromDic(dic):
		f = File(dic['path'])
		f.category = dic['category']
		f.state = dic['state']
		f.iconPath = dic['iconPath']
		if 'visible' in dic:
			f.isVisible = dic['visible']
		
		return f
		
		
	def __str__(self):
		return str({'path':self.path, 'category':self.category, 'iconPath':self.iconPath, 'state':self.state, 'visible':self.isVisible})
		
	def checkSave(self):
		if self.originalLines == None : return
		
		
		self.prepareChange()
		
		changedDetected = False
		
		if self.originalLines != self.lines : 
			self.saved = False
			self.notifyChange()
			return
	
		# Alternative method, maybe safer
# 		i = 0
# 		
# 		while i < len(self.originalLines) and i < len(self.lines):
# 			if self.originalLines[i] != self.lines[i]:
# 				print('DIFF', self.originalLines[i], self.lines[i])
# 				self.saved = False
# 				changedDetected = True
# 				return
# 			i+=1
		if(not changedDetected): 
			print('No changed detected')
			self.saved = True # useful in case of reverse
			self.notifyChange()
			
			
		
	def isLoaded(self):
		#print('isloaded', self.path)
		#print('isLoaded', self.lines)
		if self.path is None : return True
		elif self.lines is not None : return True
		return False
		
	def loadFromDisk(self):
		# print('loading from disk', self.path)
		try:
			f = open(self.path)
			lines = f.read().split("\n")
			self.originalLines = list(lines)
			self.lines = lines
			self.saved = True
			f.close()
		except FileNotFoundError:
			print('File not found', self.path)
		
	def notifyChange(self):
		# index = self.node.model.indexOfNode(self.node)
		# self.node.model.dataChanged.emit(index, index, [FileModel.itemRole, Qt.DecorationRole])
		self.node.model.layoutChanged.emit();
		
		
	def prepareChange(self):
		self.node.model.layoutAboutToBeChanged.emit();
		pass
		
	def save(self):
		f = open(self.path, 'w')
		f.write('\n'.join(self.lines))
		f.close()
		self.originalLines = list(self.lines)
		self.saved = True


class CustomTreeView( QtWidgets.QTreeView):


	def drawBranches(self, painter, rect, index):
		
		item = self.model().data(index, FileModel.itemRole)
		try:
			if(item.fd.state == 1):
				painter.fillRect(rect, QtGui.QColor(*SELECTED_COLOR));
		except:
			pass
		# else
		# painter->fillRect(rect, Qt::green);

		QtWidgets.QTreeView.drawBranches(self, painter, rect, index)

class FileSelector(QtWidgets.QWidget):
	
	ROOT_PATH = '/home/piccolo/workspace/OpenBOR/'
	
	def __init__(self, parent):
		self.mainEditor = parent
		QtWidgets.QWidget.__init__(self)
		
		trueLayout = QtWidgets.QHBoxLayout()
		w = QtWidgets.QWidget()
		tabBar = QtWidgets.QTabBar()
		tabBar.setShape(QtWidgets.QTabBar.RoundedWest)
		
		self.tabs = ['Entities', 'Levels', 'Scripts', 'System']
		for label in self.tabs:
			tabBar.addTab(_(label))
		tabBar.currentChanged.connect(self.setLibraryMode)
		
		wrapperLayout = QtWidgets.QHBoxLayout()
		layout = QtWidgets.QVBoxLayout()
		w.setLayout(wrapperLayout)
		
		wrapperLayout.addWidget(tabBar)
		wrapperLayout.addLayout(layout)
		wrapperLayout.setContentsMargins(0, 0, 0, 0)
		wrapperLayout.setSpacing(0)
		layout.setContentsMargins(0, 0, 0, 0)
		
		txt = _('FILE SELECTOR')
		txt = '\n'.join(txt)
		label = QtWidgets.QLabel(txt)
		trueLayout.addStretch()
		trueLayout.addWidget(label)
		trueLayout.addWidget(w)
		trueLayout.addStretch()
		
		self.cacheLabel = label
		self.cacheLabel.hide()
		self.content = w
		self.setLayout(trueLayout)
		
		actionGroup = QtWidgets.QActionGroup(self)
		self.buttonBar = QtWidgets.QToolBar()
		openIcon = QtGui.QIcon(QtGui.QPixmap('icons/folder.png'))
		b1 = self.buttonBar.addAction(openIcon, _('Open file'), self.mainEditor.openFile)
		addIcon = QtGui.QIcon.fromTheme('list-add')
		addAnim = self.buttonBar.addAction(addIcon, _('Create file'), self.createFile)
		self.buttonBar.addSeparator()
		self.buttonBar.addSeparator()
		self.buttonBar.addSeparator()
		libraryIcon = QtGui.QIcon(QtGui.QPixmap('icons/library.png'))
		filesIcon = QtGui.QIcon(QtGui.QPixmap('icons/box.png'))
		b1 = self.buttonBar.addAction(libraryIcon, 'Library', lambda:self.setMode('library'))
		b1bis = self.buttonBar.addAction(filesIcon, 'Opened', lambda:self.setMode('opened'))
		
		b1.setCheckable(True)
		b1bis.setCheckable(True)
		
		b1.setChecked(True)
		
		self.libraryButton = b1
		self.openedButton = b1bis
		
		self.buttonBar.addSeparator()
		self.buttonBar.addSeparator()
		self.buttonBar.addSeparator()
		expandIcon = QtGui.QIcon(QtGui.QPixmap('icons/expand.png'))
		collapseIcon = QtGui.QIcon(QtGui.QPixmap('icons/collapse.png'))
		self.collapseAllButton = self.buttonBar.addAction(collapseIcon, 'Collapse All', self.collapseAll)
		self.expandAllButton = self.buttonBar.addAction(expandIcon, 'Expand All', self.expandAll)
		
		actionGroup.addAction(b1)
		actionGroup.addAction(b1bis)
		
		
		layout.addWidget(self.buttonBar, 0)

		
		
		self.treeView = CustomTreeView(self)
		self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
		self.treeView.customContextMenuRequested.connect(self.showContextMenu)
		self.treeView.expanded.connect(self.expandChange)
		self.treeView.collapsed.connect(self.expandChange)
		self.libraryModels = {}
		for key in ('Entities', 'Levels', 'Scripts', 'System'):
			model = FileModel()
			model.isFilled = False
			self.libraryModels[key] = model

		self.openedModel = FileModel()
		self.treeView.setSortingEnabled(True)
		
		self.treeView.setAnimated(True)
		layout.addWidget(self.treeView, 1)
		
		
		self.filterModel = FilterModel()
		self.filterModel.setSortCaseSensitivity(QtCore.Qt.CaseInsensitive)
		self.filterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

		self.filterModel.setSourceModel(self.libraryModels['Entities'])
		
		self.treeView.setModel(self.filterModel)
		self.filterModel.sort(0)
		#self.treeView.setModel(self.model)
	
		self.treeView.activated.connect(self.loadItem)
		self.treeView.clicked.connect(self.loadItem)
		self.treeView.mouseReleaseEvent = self.mouseReleaseEvent
		
		header = self.treeView.header()
		header.setStretchLastSection(False)
		#header.setDefaultSectionSize(60)
		header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
		
		
		self.searchEntry = QtWidgets.QLineEdit()
		self.searchEntry.returnPressed.connect(self.search)
		layout.addWidget(self.searchEntry, 0)
		
		
		self.timeLine = QtCore.QTimeLine(400, self);
		self.timeLine.setUpdateInterval(20)
		
		#connect(timeLine, SIGNAL(frameChanged(int)), progressBar, SLOT(setValue(int)));
		self.timeLine.frameChanged.connect(self.tmp)
		
		self.loadedFiles = {}
		self.loadedPaths = []
		self.expandedFolders = set() # WARNING DEPRECATED?
		self.folderNodes = {'':None}
		
		self.openedItem = None
		# print(self.metaObject().className())
		self.setObjectName( "FileSelector" )
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F2", "Edit|Search")), self, self.focusForSearch)
		
		self.mode = 'library'
		self.libraryMode = 'Entities'
		self.sessionName = None
		self.isSavingSession = False
		self.lastSaveTime = 0
		self.lastSaveName = None
		
		
		
		
	def addFile(self, path, iconPath=None):
		if path is 'New':
			#self.setMode('opened')
			if path in self.loadedPaths:
				i = 2
				path = 'New ' + str(i)
				while path in self.loadedPaths:
					i+=1
					path = 'New ' + str(i)
			
			
		
		
		#if self.openedItem != None:
			#self.openedItem.state = 0
		
		if path not in self.loadedPaths:
			fd = File(path)
			self.loadedPaths.append(path)
			self.loadedFiles[path] = fd
			# print('APPENDING', path)
			fd.state = 1
			if path.startswith('New'): fd.path = None
			self.reloadFilesModel()
			
			
			self.makeSureVisible(fd)
		fd = self.loadedFiles[path]

		return fd
	
	'''
		Open a file from library model
	'''
	def addFromLibrary(self, fd):
		print('\n Opening file from Library...')
		if fd.path not in self.loadedPaths:
			print('was not loaded')
			self.loadedPaths.append(fd.path)
			self.loadedFiles[fd.path] = fd
			fd.state = 1
			
			self.reloadFilesModel()
			self.makeSureVisible(fd)
			
			
	def createFile(self):
		d = CreateFileDialog()
		if d.exec() == 1:
			print(d.filePath, d.category)
			# print('know xxx ' + d.filePath)
			
			
	def collapseAll(self, button=None, parentIndex=QtCore.QModelIndex()):
		self.treeView.collapseAll()
		# for i in range(self.filterModel.rowCount(parentIndex)):
		# 	index = self.filterModel.index(i, 0, parentIndex)
		# 	item = index.data(FileModel.itemRole)
		# 	# print(i, item.isExpanded)
		# 	# if item.isExpandedWithoutFilter:
		# 	self.treeView.setExpanded(index, False)
		# 	self.collapseAll(parentIndex=index)
	
	

	
	def expandAll(self, button=None, parentIndex=QtCore.QModelIndex()):
		self.treeView.expandAll()
		# for i in range(self.filterModel.rowCount(parentIndex)):
		# 	index = self.filterModel.index(i, 0, parentIndex)
		# 	item = index.data(FileModel.itemRole)
		# 	# print(i, item.isExpanded)
		# 	# if item.isExpandedWithoutFilter:
		# 	self.treeView.setExpanded(index, True)
		# 	self.expandAll(parentIndex=index)
	
	def focusForSearch(self):
		self.enterEvent(None)
		if self.searchEntry.hasFocus():
			if self.mode == 'opened':
				self.setMode('library')
			else:
				self.setMode('opened')
		self.searchEntry.setFocus()
		self.searchEntry.selectAll()
	
	'''
		Make sure associated node is visible in treeView
	'''
	def makeSureVisible(self, fd):
		node = fd.node
		print('Making sure ', node.label, ' is visible')
		while node != None:
			node.isExpanded = True
			node = node.parent()
		self.restoreExpandedState()
			
	def loadSession(self, name):
		path = os.path.join(xdg.get_data_home(), 'sessions') + os.sep + name
		#if not os.path.exists(path) : return
		self.loadedPaths = []
		self.loadedFiles = {}
		expandedFolders = []
		if name != '' and os.path.exists(path):
			self.sessionName = name
			f = open(path, 'r')
			lines = f.read().split('\n')
			section = 0
			
			if lines[0] != '':
				for line in lines:
					if line == '': section+=1
					
					elif section == 0: # List of files
						dicStr = line
						if dicStr == '': continue
						#import ast
						dic = eval(dicStr)
						path = dic['path']
						if os.path.exists(path):
							self.loadedFiles[path] = File.fromDic(dic)
							self.loadedPaths.append(path)
						
					elif section  == 1: # Expanded folders
						expandedFolders.append(line)
		else:
			self.sessionName = None
			fd = self.addFile('New')
			self.mainEditor.editor.setCurrent(fd)
		self.reloadFilesModel(expandedFolders, True)
			

		
	def tmp(self, val):
		self.mainEditor.splitter.setSizes([val, self.mainEditor.rect().width()])
		
	
	'''
		Append data to model (creating a node)
	'''
	def append(self, dataTuple, parentNode=None, model=None):
		if(model is None):
			model = self.libraryModels[self.libraryMode]
			#model = self.treeView.model()
		if(parentNode == None):
			parentNode = model.rootItem
			index = QtCore.QModelIndex() #self.model.createIndex(0,0)
			#index = self.treeView.rootIndex()
		else:
			index = parentNode.index
			#if(parentNode.isExpanded):
				#print('OOOOOUI', parentNode.isExpanded)
			#self.treeView.setExpanded(index, True)
		#print('APPEND', index.isValid())
		item = model.append(parentNode, Item(parentNode, dataTuple, model), index)
		#model.modelReset.emit()
		return item
	
	'''
		Append an (existing) node to model
	'''
	def appendNode(self, node, parentNode=None, model=None):
		if(model is None):
			model = self.libraryModels[self.libraryMode]
		if(parentNode == None):
			parentNode = model.rootItem
			index = QtCore.QModelIndex()
		else:
			index = parentNode.index
		node.parentItem = parentNode # Important
		model.append(parentNode, node, index)
		
	
	def close(self, closeAll=False):
		self.mainEditor.updateFD() # Important if we are to delete a file that we are currently editing
		if closeAll:
			self.saveSession()
			res = self.closeFolder('')
			self.reloadFilesModel()
			
		else:
			res = self.closeFile()
			self.reloadFilesModel()
		return res
		
		
	def closeFile(self, fd=None):
		if fd is None:
			fd = self.mainEditor.editor.current()
			print('\nDELETE', fd)
		if not fd.saved:
			d = UnsavedFileDialog([fd])
			if d.exec() == 0:
				return False
				
		
		print(fd.getLongText())
		self.remove(fd.getLongText())
		
		
		return True
		
	def closeFolder(self, folder):
		unsavedfiles = []
		pathsToClose = []
		for path in self.loadedPaths:
			if folder in path:
				pathsToClose.append(path)
				fd = self.loadedFiles[path]
				if not fd.saved:
					unsavedfiles.append(fd)
		if len(unsavedfiles) > 0:
			d = UnsavedFileDialog(unsavedfiles)
			if d.exec() == 0:
				return False
		for path in pathsToClose:
			self.remove(path)
			
		return True
		
	
	def deleteItem(self, index):
		item = index.data(FileModel.itemRole)
		self.mainEditor.updateFD() # Important if we are to delete a file that we are currently editing
		
		itemPath = item.path
		if itemPath is None:
			return
	
		print('ISDIR',os.path.isdir(itemPath))
		if os.path.isdir(itemPath): # If folder then be sure to remove subfiles
			if not self.closeFolder(itemPath) : return
		else:
			if item.fd != None:
				fd = item.fd
			if not self.closeFile(fd): return
			
		self.reloadFilesModel()
	
	def expandChange(self, index):
		# print('expand change', self.treeView.isExpanded(index))
		self.treeView.model().setData(index, self.treeView.isExpanded(index), FileModel.expandedRole)
		#if self.mode == 'opened': # DEPRECATED ?
			#item = index.data(FileModel.itemRole)
			#if item.path is not None and os.path.isdir(item.path):
				#if self.treeView.isExpanded(index):
					#self.expandedFolders.add(item.path)
				#else:
					#self.expandedFolders.remove(item.path)
		
		
	def enterEvent(self, e):
		if self.content.isVisible() and not settings.get_option('gui/auto_collapse', True) : return # Do not expand if already expanded
		self.treeView.update()
		self.timeLine.stop()
		self.content.show()
		self.cacheLabel.hide()
		self.timeLine.setFrameRange(self.mainEditor.splitter.sizes()[0], 300);
		self.timeLine.start()
		##self.mainEditor.splitter.setSizes([300, self.mainEditor.rect().width()])
		#b = QtCore.QByteArray()
		#b.append("sizes")
		#self.animate = QtCore.QPropertyAnimation(self.mainEditor.splitter, b)
		### Nous rentrons le délai de l'animation en ms
		#self.animate.setDuration(800)
		### Nous indiquons les propriétés de départ
		#self.animate.setStartValue([300,600])
		### Puis les propriétés de fin
		#self.animate.setEndValue([100,600])
		### Et enfin nous démarrons l'animation
		#self.animate.start()
		
	def leaveEvent(self, e):
		if self.rect().contains(self.mapFromGlobal(QtGui.QCursor.pos())):
			return
		
		if not settings.get_option('gui/auto_collapse', True) : return
		self.cacheLabel.show()
		self.content.hide()
		self.timeLine.stop()
		self.timeLine.setFrameRange(self.mainEditor.splitter.sizes()[0], 100);
		self.timeLine.start()
		#self.mainEditor.splitter.setSizes([100, self.mainEditor.rect().width()])
	
	
	'''
		Load library (default to entities library)
	'''
	def loadLibrary(self, reset=False):
		data = []
		model = self.libraryModels[self.libraryMode]
		self.filterModel.setSourceModel(model)
		if reset:
			model.reset()
			
		if model.isFilled and not reset:
			return
		
		if self.libraryMode == 'Entities':
			
			
			
			path = os.path.join(FileSelector.ROOT_PATH, 'data', 'models.txt')
			print(path)
			if not os.path.isfile(path):
				print('WARNING : no models.txt')
				return
				
			
			ent_cache = Cache('entities_data', FileSelector.ROOT_PATH)
			
			Entity.AVAILABLE_MODELS = []
			
			
			f = FileWrapper(path)
			lines = f.getLines()
			
			loadEntData = True
			
			
			print("\nLoading entities...")
			# print(len(lines))
			# print(ent_cache.fullID)
			
			for i, line in enumerate(lines):
				pLine = ParsedLine(line)
				part = pLine.next()
				if part is None : continue
				if part.lower() == 'know' or part.lower() == 'load':
					# print(pLine.line, pLine.getNumberOfParts())
					if(pLine.getNumberOfParts() < 3) :
						logging.debug('Incomplete line : ' + pLine.line)
					else:
						name = pLine.next().lower()
						Entity.AVAILABLE_MODELS.append(name)
						path = pLine.next()
						
						
						type = 'none'
						icon = None
						
						
						
						if loadEntData:
							if name in ent_cache.data :
								ent_data = ent_cache.data[name]
								type = ent_data['type']
								icon = ent_data['icon']
							else :
						
								fullPath = os.path.join(FileSelector.ROOT_PATH, path)
								if not os.path.exists(fullPath) : continue
								# print(fullPath)
								f = FileWrapper(fullPath)
								lines2 = f.getLines()
								
								
								for i, line2 in enumerate(lines2):
									pLine2 = ParsedLine(line2)
									part = pLine2.next()
									if part == 'type':
										type = pLine2.next().lower()
									if part == 'icon':
										icon = pLine2.next()
										
									if i > 100:
										break
										
								ent_cache.data[name] = {'type':type, 'icon':icon}
						
						#print(name, type)
						currentData = {'pos':i, 'label':name, 'path':path, 'type':type, 'icon':icon}
						data.append(currentData)
				
			categories = ['player', 'enemy', 'npc', 'obstacle', 'panel', 'none', 'text', 'endlevel', 'trap', 'item', 'unknown']
			categorieNodes = {}
			for i, c in enumerate(categories):
				categorieNodes[c] = self.append([c, c, i, None, 'icons/' + c +'.png', None])
				
				
			for i, d in enumerate(data):
				#print(d)
				#if d['type'] != 'player':
					#pass
				path = os.path.join(FileSelector.ROOT_PATH, d['path'])
				fd = File(path)
				if d['icon'] is not None:
					iconPath = os.path.join(FileSelector.ROOT_PATH, d['icon'])
					d['icon'] = iconPath
					fd.iconPath = iconPath
				fd.category = 'Entity'
				if d['type'] in categorieNodes : parentNode = categorieNodes[d['type']]
				else : parentNode = categorieNodes['unknown']
				#parentNode = categorieNodes['unknown']
				self.append((d['label'], d['label'], i, path, d['icon'], fd), parentNode)
			
			self.libraryModels[self.libraryMode].modelReset.emit()
			
			# update cache
			ent_cache.save()
			self.mainEditor.entitiesHaveBeenReloaded()
			
				
		elif self.libraryMode == 'Levels':
			path = os.path.join(FileSelector.ROOT_PATH, 'data', 'levels.txt')
			if not os.path.isfile(path): return
			f = open(path)
			lines = f.read().split('\n')
			f.close()
			
			levelsAlreadyAdded = []
			for i, line in enumerate(lines):
				pLine = ParsedLine(line)
				part = pLine.next()
				if part is None : continue
				if part.lower() == 'set':
					name = pLine.next()
					parentNode = self.append((name, name, i, None, None, None), None)
					#print(name)
				elif part.lower() == 'file':
					path = pLine.next()
					if(path in levelsAlreadyAdded): continue
					levelsAlreadyAdded.append(path)
					path = os.path.join(FileSelector.ROOT_PATH, path)
					fd = File(path)
					fd.category = 'Level'
					self.append((os.path.basename(path), os.path.basename(path), i, path, None, fd), parentNode)
					
			self.libraryModels[self.libraryMode].modelReset.emit()
					
		elif self.libraryMode == 'Scripts':
			def scanDir(dir, parentNode):
				for name in os.listdir(dir):
					path = os.path.join(dir, name)
					if os.path.isdir(path):
						node = self.append((name, name, 0, path, ':folder', None), parentNode)
						scanDir(path, node)
					else:
						if name.endswith('~'): continue
						node = self.append((name, name, 0, path, None, File(path)), parentNode)
						
			path = os.path.join(FileSelector.ROOT_PATH, 'data', 'scripts')
			if not os.path.exists(path): return
			#node = self.append(('scripts', 'scripts', 0, path, None, None), None)
			scanDir(path, None)
			
			self.libraryModels[self.libraryMode].modelReset.emit()
			
		elif self.libraryMode == 'System':
			
			for name in ('models.txt', 'levels.txt', 'lifebar.txt', 'menu.txt', 'script.txt', 'video.txt'):
				
				path = os.path.join(FileSelector.ROOT_PATH, 'data', name)
				if not os.path.isfile(path): continue
				node = self.append((name, name, 0, path, None, File(path)), None)
				
			self.libraryModels[self.libraryMode].modelReset.emit()
			
		model.isFilled = True
		
		if(self.mode == 'library'):
			self.filterModel.setSourceModel(model)
			self.restoreExpandedState()
	
	
	def loadItem(self, index):
		item = index.data(FileModel.itemRole)
		fd = item.fd
		if fd is None or (fd.path is not None and os.path.isdir(fd.path)): return
		#if self.openedItem is not None:
			#self.openedItem.state = 0

		fd.state = 1
		self.updateStates(exception=fd)
		

		self.openedItem = fd
		#print(fd, fd.path, os.path.isdir(fd.path))
		
		#print(fd)
		if not fd.isLoaded() : fd.loadFromDisk()
		self.mainEditor.loadFile(fd, False)
		
		if self.mode == 'library':
			self.addFromLibrary(fd)
		
		self.setMode('opened')
		self.saveExpandedStateWithoutFilters()
		self.searchEntry.setText('')
		self.search()
		
		
		
	def mouseReleaseEvent(self, e):
		
		if e.button() == Qt.MidButton:
			i = self.treeView.indexAt(QtCore.QPoint(e.x(), e.y()))
			if(i.column() != 0):
				i= i.sibling(i.row(), 0)
			self.treeView.setExpanded(i, not self.treeView.isExpanded(i))
		else:
			QtWidgets.QTreeView.mouseReleaseEvent(self.treeView, e)

			
			
	def reloadFilesModel(self, expandedFolders=[], reset=False):
		def match(pattern):
			nb = 0
			for f1 in folders:
				if f1 == f: continue
				if pattern in f1:
					nb += 1
			#print(nb)
			return nb
		
		#self.mode = 'library'

		#self.openedModel.rootItem.childItems = []
		self.openedModel.reset()
	
		if reset:
			folderNodes = {'':None}
			previousFolderNodes = {}
		else:
			previousFolderNodes = self.folderNodes
			
			#self.openedModel.rootItem.empty()
			for n in previousFolderNodes.values(): # We'll reuse previous items, so we must empty them
				if n is not None:
					#n.index = None
					n.empty()
					
			#self.openedModel.rootItem.emptyTree() # Nodes still exist
			folderNodes = {'':None}
		iconPath = None
		folders = []
		
		#self.loadedFiles = [
		      #'/home/piccolo/workspace/OpenBOR/data/scripts/dcancel.c', '/home/piccolo/workspace/OpenBOR/data/chars/zangief/zangief.txt', '/home/piccolo/workspace/OpenBOR/data/chars/amingo/amingo.txt']

		filesToAdd = []
		for path in self.loadedPaths:
			filesToAdd.append(path)
			if path.startswith('New'): # Rather check if fd.orginalLines is None
				continue
			
			folders.append(os.path.dirname(path))
			#if not reset and self.loadedFiles[path].isAddedToAView : continue
			#if reset or not self.loadedFiles[path].isAddedToAView:
			
		folders = list(set(folders))
		#folders = sorted(folders, key=len)
		folders.sort(key=lambda x: x.count(os.path.sep))
		#folders = sorted(folders, key=lambda p: (-p.count(os.path.sep), p))
		# print(folders)
		
		for f in folders:
			# print('\n*** Processing folder ***', f)
			# How to handle a folder ?
			if f in folderNodes : continue # Already present as a node, pass
		
			# Will any of my parent folders be present somewhere else ?
			# Goal : find the highest parent that will be needed as a node (global approach, prepare roots)
			
			parent = os.path.dirname(f)
			parentNode = None
			parentsToAdd = []
			# Tant que pas de node trouvée ET pas à la racine ET une différence de match avec son parent
			currentMatch = match(f)
			while parentNode is None and parent != os.path.dirname(parent) and match(parent) != currentMatch:
				
				if parent in folderNodes:
					parentNode = folderNodes[parent]
				else:
					parentsToAdd.append(parent)
					currentMatch = match(parent)
					parent = os.path.dirname(parent)
					
			
			
			# print('Reason left', parent, '[parentNode exists :', parentNode is not None, '] [parent is root :', parent == os.path.dirname(parent), '] [same match with pParent:', match(parent) == match(os.path.dirname(parent)))
			#if(parent not in parentsToAdd and parent not in folderNodes and  match(parent) > 0): # and match(parent) != match(os.path.dirname(parent)
				#parentsToAdd.append(parent)
				
			
			if len(parentsToAdd) > 0:
				parentsToAdd.reverse()
				# print('toADD', parentsToAdd)
				#print(parent, parentNode)
				parentOfFirst = os.path.dirname(parentsToAdd[0])

				# print(folderNodes)
				if parentOfFirst in folderNodes:
					parentNode = folderNodes[parentOfFirst]

				# print('parentOfFirst', parentOfFirst, parentNode)
				
				for parent in parentsToAdd:
					if parent in previousFolderNodes : 
						node = previousFolderNodes[parent]
						self.appendNode(node, parentNode, self.openedModel)
					else :
						node = self.append((os.path.basename(parent), os.path.basename(parent), 0, parent, ':folder', None), parentNode, self.openedModel)
						if parent in expandedFolders : node.isExpanded = True
					folderNodes[parent] = node
					parentNode = node
				# print(folderNodes)
		
			#return
		
			# Local approach, gap filling (branch to root)
			parentNode = None
			parent = os.path.dirname(f)
			parents = []
			parentsToAdd = []
			while parentNode is None and parent != os.path.dirname(parent):
				if parent in folderNodes:
					parentNode = folderNodes[parent]
				else:
					parents.append(parent)
				parent = os.path.dirname(parent)
			# print('PARENTS PHASE 2', parentNode, parents)		
			#print(parents)
			
			if parentNode is not None: # A noded parent found
				# parents contains not "noded" parents folder, so we node them
				parents.reverse()
				for parent in parents:
					if parent in previousFolderNodes : 
						node = previousFolderNodes[parent]
						self.appendNode(node, parentNode, self.openedModel)
					else :
						node = self.append((os.path.basename(parent), os.path.basename(parent), 0, parent, ':folder', None), parentNode, self.openedModel)
						if parent in expandedFolders : node.isExpanded = True
					folderNodes[parent] = node
					parentNode = node
			
			if f in previousFolderNodes : 
				node = previousFolderNodes[f]
				self.appendNode(node, parentNode, self.openedModel)
			else :
				node = self.append((os.path.basename(f), os.path.basename(f), 0, f, ':folder', None), parentNode, self.openedModel)
			folderNodes[f] = node
			if f in expandedFolders : node.isExpanded = True
		
		for path in filesToAdd:
			parentNode = folderNodes[os.path.dirname(path)]
			fd = self.loadedFiles[path]
			fd.isAddedToAView = True
			#if fd.isVisible : # DEPRECATED?
				#parentNode.isExpanded = True
				#self.expandedFolders.add(parentNode.path)
			node = self.append((os.path.basename(path), os.path.basename(path), 0, path, iconPath, fd), parentNode, self.openedModel)
			fd.node = node
			
		self.folderNodes = folderNodes
		
		self.openedModel.modelReset.emit()

		if(self.mode == 'opened'):
			#self.treeView.update()
			self.filterModel.setSourceModel(self.openedModel)
			
			#print('****')
			#def trav(parentIndex):
				#print('GOING THROUGH', self.filterModel.rowCount(parentIndex))
				#for i in range(self.filterModel.rowCount(parentIndex)):
					#print('in child ', end="")
					#index = self.filterModel.index(i, 0, parentIndex)
					#item = index.data(FileModel.itemRole)
					#print(item.label, item.childItems)
					#trav(index)
				
			#trav(QtCore.QModelIndex())
			#print('****')
			self.restoreExpandedState()
			#WARNING self.treeView.expandAll()

			
			
	def remove(self, path):
		if path in self.loadedPaths:
			self.loadedPaths.remove(path)
			self.mainEditor.remove(self.loadedFiles[path])
			del self.loadedFiles[path]
			
		
	def saveExpandedStateWithoutFilters(self, parentIndex=QtCore.QModelIndex()):
		for i in range(self.filterModel.rowCount(parentIndex)):
			index = self.filterModel.index(i, 0, parentIndex)
			item = index.data(FileModel.itemRole)
			item.isExpandedWithoutFilter = item.isExpanded
			self.saveExpandedStateWithoutFilters(index)
			
	def restoreExpandedState(self, parentIndex=QtCore.QModelIndex(), level=0):
		# if(level == 0): print('\nrestoreExpandedState', parentIndex)
		for i in range(self.filterModel.rowCount(parentIndex)):
			index = self.filterModel.index(i, 0, parentIndex)
			item = index.data(FileModel.itemRole)
			# print(i, item.label, item.isExpanded)
			if item.isExpanded:
				self.treeView.setExpanded(index, item.isExpanded)
			self.restoreExpandedState(index, level+1)
		# if(level == 0): print('\n\n')
	
	def restoreExpandedStateWithoutFilters(self, parentIndex=QtCore.QModelIndex()):
		# print('restoreExpandedState', parentIndex)
		for i in range(self.filterModel.rowCount(parentIndex)):
			index = self.filterModel.index(i, 0, parentIndex)
			item = index.data(FileModel.itemRole)
			# print(i, item.isExpanded)
			# if item.isExpandedWithoutFilter:
			self.treeView.setExpanded(index, item.isExpandedWithoutFilter)
			self.restoreExpandedStateWithoutFilters(index)

			
			
	def setMode(self, mode):
		if mode == 'library':
			#self.treeView.setModel(self.model)
			self.filterModel.setSourceModel(self.libraryModels[self.libraryMode])
			self.libraryButton.setChecked(True)
		else:
			if self.mode != 'opened':
				#self.treeView.setModel(self.openedModel)
				self.filterModel.setSourceModel(self.openedModel)
			#self.treeView.expandAll()
			#self.libraryButton.setChecked(False)
			self.openedButton.setChecked(True)
			
		self.restoreExpandedState()
		self.mode = mode
	
	def setLibraryMode(self, index):
		selectedMode = self.tabs[index]
		if selectedMode == self.libraryMode:
			if self.mode == 'library':
				self.setMode('opened')
			else:
				self.setMode('library')
		else:
			self.libraryMode = selectedMode
			self.loadLibrary()
			self.setMode('library')
	
	def setSelectedFile(self, fd):
		pass
		#Method 2 
		# selectionModel = self.treeView.selectionModel()
		# selectionModel.select(self.openedModel.indexOfNode(fd.node), QtCore.QItemSelectionModel.Select) # , 
		
		# Method 1
		# self.treeView.setCurrentIndex(self.openedModel.indexOfNode(fd.node))
	
	def search(self):
		txt = self.searchEntry.text()
		if(txt != ''):
			self.saveExpandedStateWithoutFilters()
			
		
		self.treeView.model().setFilterRole(Qt.DisplayRole)
		regExp = QtCore.QRegExp(txt, QtCore.Qt.CaseInsensitive)
		self.treeView.model().setFilterRegExp(regExp)
		if(txt == ''):
			self.restoreExpandedStateWithoutFilters()
		else:
			self.restoreExpandedState() # not really a restoring but a matching of visual expanding with expanded state in data
		#self.treeView.expandAll()
		
		
	def saveSession(self, name=None):
		if self.isSavingSession:
			return
			
		
		import datetime
		now = datetime.datetime.now()
		
			
		# >>> now
		# datetime.datetime(2009, 1, 6, 15, 8, 24, 78915)
			
		self.isSavingSession = True
		if name is None:
			name = self.sessionName
		if name is None:
			name = 'Default'
		logging.debug(str(now) + ' STARTING SAVE SESSION : ' + str(name))
		
		
		ts = now.timestamp()
		if(name == self.lastSaveName and ts < self.lastSaveTime + 2):
			logging.debug(str(now) + ' SAVE CANCEL because too close to last save')
			self.isSavingSession = False
			return
		
		self.lastSaveTime = ts
		self.lastSaveName = name
		settings.set_option('general/last_session', name)
		
		if name is None:
			self.isSavingSession = False
			return # TODO dialog for saving
		
		f = open(os.path.join(xdg.get_data_home(), 'sessions') + os.sep + name, 'w')
		
		#output = '\n'.join(map(str, self.loadedFiles.values()))
		
		toSave = []
		for fd in self.loadedFiles.values():
			if fd.path is not None and os.path.exists(fd.path):
				fd.isVisible = os.path.dirname(fd.path) in self.expandedFolders
				toSave.append(fd)
		
		logging.debug('FILES TO SAVE : ' + str(toSave))
		output = '\n'.join(map(str, toSave))
		
		output += '\n\n'
		
		
		for fd in self.folderNodes.values():
			if fd is not None and fd.isExpanded:
				logging.debug(fd.path)
				output += fd.path + '\n'
		
		#for path in self.loadedFiles:
			#f.write(path + "\n")
		f.write(output)
		f.close()
		logging.debug('END OF SAVE SESSION : ' + name)
		self.isSavingSession = False
		
	def showContextMenu(self, pos):
		index = self.sender().indexAt(pos)
		if not index.isValid() : return
		item = index.data(FileModel.itemRole) #internalPointer()
		
		popMenu = QtWidgets.QMenu(self)
		delete = popMenu.addAction(QtGui.QIcon.fromTheme('list-remove'), _("Close"))
		action = popMenu.exec_(self.sender().mapToGlobal(pos))
		if action == delete:
			self.deleteItem(index)
			
			
	def updateStates(self, exception=None):
		
		self.treeView.clearSelection()
		self.openedModel.layoutAboutToBeChanged.emit();
		
		
		
		
		
		for oFd in self.loadedFiles.values():
			if(oFd == exception):continue
		
			if oFd.state != 0:
				if oFd.state == 10:
					oFd.state = 0
				else:
					oFd.state += 1
					
		self.openedModel.layoutChanged.emit();

		
class Item(TreeItem):
	def __init__(self, parent, data, model):
		TreeItem.__init__(self, data[1], parent)
		self.ID = data[0]
		self.label = data[1]
		self.pos = data[2]
		self.path = data[3]
		self.fd = data[5]
		if(self.fd != None):
			self.fd.node = self

		self.subelements = []
		self.iconPath =  data[4]
		self.icon = None
		
		self.model = model
		
	def __str__( self ):
		return self.label
		
	def __repr__(self):
		return self.label
	
	
	def copy(self):
		new = Item(self, [self.ID, self.label, self.pos, self.path, self.iconPath, self.fd], self.parent(), self.model)
		
	def getFilter(self):
		'''
			ex : {"artist":"AC/DC", "album":"Back In Black", "title":"You Shook Me All Night Long"}
		'''
		dic = {}
		item = self
		while(item.parent() != None): # Don't  eval rootItem 
			dic[item.type] = item.label
			item = item.parent()
		return dic
		
class FileModel(TreeModel):
	icon_size = 25
	unsavedIcon = None
	bigFont = None
	
	itemRole = Qt.UserRole+2
	expandedRole = Qt.UserRole+1
	expandedRoleWithoutFilter = Qt.UserRole+3
	
	def __init__(self):
		TreeModel.__init__(self)
		self.columnsFields = ('pos', 'ID', 'label')
		if FileModel.unsavedIcon is None:
			FileModel.unsavedIcon = QtGui.QIcon.fromTheme('document-save').pixmap(self.icon_size-5)
			FileModel.bigFont = QtGui.QFont()
			FileModel.bigFont.setPointSize(12)
			
		


	def columnCount(self, parent):
		return 2

	def data(self, index, role):
		if not index.isValid():
			return None
		item = index.internalPointer()
		
		if role == self.itemRole:
			return item
		elif role == self.expandedRole:
			return item.isExpanded
		elif role == self.expandedRoleWithoutFilter:
			return item.isExpandedWithoutFilter
		elif role == Qt.DisplayRole:
			if index.column() == -1:
				return item.pos
			elif index.column() == 0:
				return item.label
				
		elif role == Qt.DecorationRole and index.column() == 0:
			if item.fd is not None and item.fd.saved is False:
				return self.unsavedIcon
			if(item.icon is None):
				#try:
				path = None
				if item.fd is not None:
					path = item.fd.iconPath
				if item.iconPath is not None:
					path = item.iconPath
					
				if path is not None:
					if path[0] == ':':
						item.icon = QtGui.QIcon.fromTheme('folder').pixmap(self.icon_size)
						
					else:
						
						item.icon =  QtGui.QPixmap.fromImage(loadSprite(path))
						if(item.icon.isNull()):
							#item.icon = self.icons[item.type]
							pass
						else:
							if(item.path is None):
								size = 40
							else:
								size = self.icon_size
							item.icon = item.icon.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation) #scaledToHeight(icon_size)
								
						#except:
							pass
						#item.icon = self.icons[item.label]
				
			return item.icon

		elif role == Qt.ToolTipRole:
			return item.path
		
		elif role == Qt.BackgroundRole and (item.fd is not None and item.fd.state > 0):
			def tint(x):
				return int(x + factor * (255-x))

			
			if(item.fd.state == 1): # top of the chain (~ selected)
				color = SELECTED_COLOR
			else:
			
				factor = item.fd.state * 0.1
				color = [215,223,1]
				color = map(tint, color)

			return QtGui.QBrush(QtGui.QColor(*color))
		elif role == Qt.FontRole and item.path is None:
			return FileModel.bigFont
		elif role == Qt.ForegroundRole and (item.fd is not None and item.fd.state > 0):
			if(item.fd.state == 1):
				color = [255,255,255]
			else:
				color = [0,0,0]
			return QtGui.QBrush(QtGui.QColor(*color))
		return None

	def flags(self, index):
		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled
	
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			if section == 0:
				return '#'
			elif section == 1:
				return 'ID'
			elif section == 2:
				return 'Label'
			
		return None
		
	def mimeData(self, indexes):
		'''
			What is passed during drag operations
		'''
		data = QtCore.QMimeData()
		selection = []
		for i in indexes:
			selection.append(i.internalPointer().getFilter())
		data.setData('bullseye/library.items', str(selection))
		return data
		
	def mimeTypes(self):
		'''
			FIXME Not used, didn't manage to find out how to automatically serialize items (tddhus overrided mimeData instead)
		'''
		return ('bullseye/library.items',)
	
	def setData(self, index, value, role):
		if not index.isValid():
			return None
		item = index.internalPointer()
		
		if role == self.expandedRole:
			item.isExpanded = value
			return 1
		elif role == self.expandedRoleWithoutFilter:
			item.isExpandedWithoutFilter = value
			return 1
		else:
			return TreeModel.setData(self, index, value, role)
			
		
	def sort(self, columnIndex, order):
		self.layoutAboutToBeChanged.emit()
		if(order == QtCore.Qt.AscendingOrder):
			reverse = False
		else:
			reverse = True
		reverse = True
			
		def sort(elt, reverse):
			elt.childItems = sorted(elt.childItems, key=attrgetter(self.columnsFields[columnIndex]), reverse=reverse)
			for childElt in elt.childItems:
				sort(childElt, reverse)
				
		sort(self.rootItem, reverse)
		
		self.layoutChanged.emit()

class UnsavedFileDialog(QtWidgets.QDialog):
	def __init__(self, files):
		self.files = files
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QVBoxLayout()
		layout.addWidget(QtWidgets.QLabel(_('The following documents have been modified. Do you want to save them before closing ?')), 0)
		tableView = QtWidgets.QTableView()
		tableView.setMinimumWidth(400)
		
		tableView.verticalHeader().hide()
		self.foldersModel = QtGui.QStandardItemModel(0, 2)
		self.foldersModel.setHorizontalHeaderLabels([_("Documents"), _("Location")])
		for fd in files:
			checkBox = QtGui.QStandardItem(fd.name)
			checkBox.setCheckable(True)
			checkBox.setCheckState(QtCore.Qt.Checked)
			#if dig:
				#checkBox.setCheckState(QtCore.Qt.Checked)
			self.foldersModel.appendRow([checkBox, QtGui.QStandardItem(fd.getLongText())])
		
		tableView.setModel(self.foldersModel)
		tableView.horizontalHeader().setSectionResizeMode (1, QtWidgets.QHeaderView.Stretch)
		tableView.horizontalHeader().setSectionResizeMode (0, QtWidgets.QHeaderView.Fixed)
		tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
		
		layout.addWidget(tableView, 1)
		
		selectAll = QtWidgets.QPushButton(_('Select All'))
		selectAll.pressed.connect(self.selectAll)
		layout.addWidget(selectAll, 0)
		
		buttonLayout = QtWidgets.QHBoxLayout()
		buttonLayout.addStretch()
		#annuler abandonner enregistrer
		cancelButton = QtWidgets.QPushButton(_('Cancel Closing'))
		cancelButton.pressed.connect(self.reject)
		saveButton = QtWidgets.QPushButton(_('Save'))
		saveButton.pressed.connect(self.save)
		dontsaveButton = QtWidgets.QPushButton(_('Don\'t save'))
		dontsaveButton.pressed.connect(self.accept)
		buttonLayout.addWidget(cancelButton, 0)
		buttonLayout.addWidget(dontsaveButton, 0)
		buttonLayout.addWidget(saveButton, 0)
		
		layout.addLayout(buttonLayout)
		
		self.setLayout(layout)
		
	def save(self):
		lookFolder = os.path.dirname(settings.get_option('general/data_path'))
		toActuallySave = []
		for i in range(self.foldersModel.rowCount()):
			if self.foldersModel.item(i, 0).checkState() == QtCore.Qt.Checked:
				toActuallySave.append(self.foldersModel.item(i, 1).text())
			
		for fd in self.files:
			if fd.getLongText() in toActuallySave:
				if fd.path is None:
					path = QtWidgets.QFileDialog.getSaveFileName(self, caption=_('Save As') + ' (' + fd.getLongText() + ')', directory=lookFolder)[0]
					if path is None or path  == '': return
					else : 
						lookFolder = os.path.dirname(path) # Change lookFolder for next files
						fd.path = path
				fd.save()
		self.accept()
		
	def selectAll(self):
		for i in range(self.foldersModel.rowCount()):
			self.foldersModel.item(i, 0).setCheckState(QtCore.Qt.Checked)
