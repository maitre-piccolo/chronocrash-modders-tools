from PySide import QtCore, QtGui

import os, time
import re
import shutil
from common import settings, util
from gui.portrait import IconViewer, Portrait
from gui.imagewidget import SimpleImageWidget
from gui.util import FileInput
     
class SpriteSorterWidget(QtGui.QWidget):
	def __init__(self):
		QtGui.QWidget.__init__(self)
		layout = QtGui.QVBoxLayout()
		
		self.imageWidget = SimpleImageWidget()
		self.iconViewer = IconViewer(self)
		self.iconViewer.activated.connect(self.onIconActivated)
		self.iconViewer.middleClick.connect(self.onIconMClick)
		#self.iconViewer.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
		
		layout.addWidget(self.imageWidget, 1)
		layout.addWidget(self.iconViewer, 0)
		
		dataPath = settings.get_option('general/datapath', '')
		self.spriteFolder = FileInput(self, 'folder', settings.get_option('sprite_sorter/folder', ''), 'Select sprite folder', dataPath)
		
		loadButton = QtGui.QPushButton(_('Load'))
		loadButton.clicked.connect(self.loadSprites)
		
		playButton = QtGui.QPushButton(_('Play'))
		playButton.clicked.connect(self.playAnimation)
		
		renameButton = QtGui.QPushButton(_('Rename'))
		renameButton.clicked.connect(self.renameSprites)
		
		clearButton = QtGui.QPushButton(_('Clear'))
		clearButton.clicked.connect(self.clear)
		
		controlWidget = QtGui.QWidget()
		controlLayout = QtGui.QHBoxLayout()
		controlLayout.addWidget(loadButton, 0)
		controlLayout.addWidget(self.spriteFolder, 1)
		controlLayout.addWidget(playButton)
		controlLayout.addWidget(renameButton)
		controlLayout.addWidget(clearButton)
		controlWidget.setLayout(controlLayout)
		
		layout.addWidget(controlWidget, 0)
		self.setLayout(layout)
		
	def clear(self):
		self.iconViewer.clear()
		
	def loadSprites(self):
		self.iconViewer.clear()
		folder = self.spriteFolder.text()
		settings.set_option('sprite_sorter/folder', folder)
		
		self.originalPaths = []
		for f in sorted(os.listdir(folder)):
			if f[0] != '.':
				self.originalPaths.append(f)
				if os.path.isfile(os.path.join(folder, f)):
					(shortname, extension) = os.path.splitext(f)
					extension = extension.lower()
					#checkFileInterest(folder, f, extension.lower())
					self.iconViewer.model.append(Portrait(folder, f))
				#else:
					#if(dig):
						#scanFolder(folder + os.sep + f, dig, files)
						
	def onIconActivated(self, index):
		self.imageWidget.loadFile(self.iconViewer.getItemAt(index))
		
	def onIconMClick(self, index):
		self.imageWidget.loadFile(self.iconViewer.getItemAt(index))

	def playAnimation(self):
		items = self.iconViewer.model.items
		self.imageWidget.playFiles(items)
		
	def renameSprites(self):
		self.originalPaths = []
		
		items = self.iconViewer.model.items
		folder = self.spriteFolder.text()
		numbers = []
		for item in items:
			self.originalPaths.append(item.path)
			os.rename(item.path, item.path + '.BACK')
			
		self.originalPaths = sorted(self.originalPaths)
		i = 0
		for item in items:
			newPath = os.path.join(folder, self.originalPaths[i])
			os.rename(item.path + '.BACK', newPath)
			item.file = self.originalPaths[i]
			item.path = newPath
			i+=1

		
