import os, re, time, mimetypes

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from common import util
from common import settings
from gui.util import FileInput


class ProjectSelector(QtWidgets.QWidget):
	
	LOAD_TEXT = 'Select a game project\n or register a new one'
	
	def __init__(self, parent):
		self.mainFrame = parent
		QtWidgets.QWidget.__init__(self)
		
		self.layout = QtWidgets.QVBoxLayout()
		
		self.projectLayout = QtWidgets.QVBoxLayout()
		
		buttonLayout = QtWidgets.QHBoxLayout()
		
		
		
		
		addButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('list-add'), _('Add'))
		addButton.pressed.connect(self.addProject)
		delButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('list-remove'), _('Remove'))
		delButton.pressed.connect(self.removeProject)
		
		
		buttonLayout.addWidget(addButton)
		buttonLayout.addWidget(delButton)
		
		self.label = QtWidgets.QLabel(_('Register a game project by clicking the add button\nand selecting the game data folder'))
		font = self.label.font()
		font.setPointSize(32)
		self.label.setFont(font)
		self.label.setContentsMargins(50, 50, 50, 50);
		
		
		self.layout.addWidget(self.label, 0)
		self.layout.addLayout(buttonLayout)
		self.layout.addLayout(self.projectLayout, 1)
		
		self.setLayout(self.layout)
		
		self.layout.setAlignment(self.label, QtCore.Qt.AlignCenter)
		self.layout.setAlignment(buttonLayout, QtCore.Qt.AlignCenter)
		self.layout.setAlignment(self.projectLayout, QtCore.Qt.AlignCenter)
		
		self.projects = settings.get_option('general/projects', [])
		if len(self.projects) > 0:
			self.label.setText(_(self.LOAD_TEXT))
		
		self.loadProjectsList()
		
		self.mode = 'load'
			


	def addProject(self):
		path = QtWidgets.QFileDialog.getExistingDirectory(self, _('Choose a mod data folder'))
		if path == '': return # Canceled
		print(path)
		files = os.listdir(path)
		print(files)
		if 'models.txt' not in map(lambda x:x.lower(), files) or path in self.projects:
			return
		
		self.projects.append(path)
		
		settings.set_option('general/projects', self.projects)
		self.loadProjectsList()
		

		
		
	def loadProject(self, project):
		settings.set_option('general/data_path', project)
		
		self.hide()
		self.mainFrame.meWidget.loadProject(project)
		self.mainFrame.setMode('mainEditor')
		self.mainFrame.setSession(settings.get_option('general/last_session', 'Default'))
		
		
	def loadProjectsList(self):
		def clearLayout(layout):
			while layout.count():
				child = layout.takeAt(0)
				if child.widget() is not None:
					child.widget().deleteLater()
				elif child.layout() is not None:
					clearLayout(child.layout())
		
		#child = True
		#while child != None:
			#child = self.projectLayout.takeAt(0)
			#child.deleteLater()
			
		clearLayout(self.projectLayout)
			

		
		for p in self.projects:
			button = QtWidgets.QPushButton(p)
			button.pressed.connect(self.projectClicked)
			
			self.projectLayout.addWidget(button)
			self.projectLayout.addSpacing(50)
			
			
	def projectClicked(self):
		project = self.sender().text()
		if self.mode == 'load':
			self.loadProject(project)
		elif self.mode == 'remove':
			self.projects.remove(project)
			settings.set_option('general/projects', self.projects)
			self.sender().deleteLater()
			self.mode = 'load' # set click mode back to 'load'
			
	def removeProject(self):
		if self.mode == 'remove':
			self.mode = 'load'
			self.label.setText(_(self.LOAD_TEXT))
		else:
			self.label.setText(_('Click on the project you want to remove\n or click on remove button again to cancel'))
			self.mode = 'remove'
