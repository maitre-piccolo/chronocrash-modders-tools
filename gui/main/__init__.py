import os, re, time, mimetypes

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from common import util
from common import settings
from gui.util import FileInput

from gui.portrait import IconViewer, Portrait

from qutepart import EverydayPart

from data import ParsedLine

from gui.main.fileselector import FileSelector, File
from gui.main.everydayeditor import EverydayEditor
from gui.entity import EntityEditorWidget
from gui.level import LevelEditorWidget

ROOT_PATH = '/home/piccolo/workspace/OpenBOR/'

from qutepart.syntax.colortheme import ColorTheme




class MainEditorWidget(QtWidgets.QWidget):
	
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QHBoxLayout()
		splitter = QtWidgets.QSplitter(self)
		self.splitter = splitter
		layout.addWidget(splitter)
		self.setLayout(layout)
		layout.setContentsMargins(0, 0, 0, 0)
		
		
		self.fileSelector = FileSelector(self)

		self.editor = EverydayEditor(self)
		
		
		self.setupFavorites()

		self.currentPath = None

		
		#self.loadProject()
		
		rightSide = QtWidgets.QWidget()
		rightLayout = QtWidgets.QVBoxLayout()
		rightLayout.setContentsMargins(0, 0, 0, 0)
		rightSide.setLayout(rightLayout)
		
		self.headerWidget = HeaderWidget(self)
		rightLayout.addWidget(self.headerWidget, 0)
		rightLayout.addWidget(self.editor, 1)
		
		self.entityEditor = EntityEditorWidget()
		self.levelEditor = LevelEditorWidget()
		rightLayout.addWidget(self.entityEditor, 1)
		rightLayout.addWidget(self.levelEditor, 1)
		rightLayout.addWidget(self.favEditor, 1)
		self.entityEditor.hide()
		self.levelEditor.hide()
		self.favEditor.hide()
		
		
		
		
		splitter.addWidget(self.fileSelector)
		splitter.addWidget(rightSide)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+D", "Edit|Comment")), self, self.editor.comment)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Shift+Ctrl+D", "Edit|Uncomment")), self, self.editor.uncomment)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+F", "Edit|Find")), self, self.editor.focusForSearch)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+R", "Edit|Replace")), self, self.editor.replaceEntry.setFocus)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+W", "File|Close")), self, self.fileSelector.close)

		
		#QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+H", "File|Close")), self, self.editor.editor.highlightCurrentWord)
				
		self.splitter.setStretchFactor(0,0)
		self.splitter.setStretchFactor(1,1)
		
		self.currentView = 'text'
		
	def close(self, all=False):
		self.levelEditor.looping = False
		return self.fileSelector.close(all)
		
		
	def editNew(self):
		fd = self.fileSelector.addFile('New')
		fd.lines = []
		self.loadFile(fd, False)
		

	def entitiesHaveBeenReloaded(self):
		self.entityEditor.frameEditor.bindingEditor.reloadModels()
		
		
	def loadProject(self, path=None):

		if path is None:
			path = settings.get_option('general/data_path', '')
		
		global ROOT_PATH
		print('loading project', path)
		ROOT_PATH = os.path.dirname(path)
		print('root path = ', ROOT_PATH)
		FileSelector.ROOT_PATH = ROOT_PATH
		EntityEditorWidget.ROOT_PATH = ROOT_PATH
		
				
		self.fileSelector.loadLibrary(True)
		
	def loadFile(self, fd, rel=True):
		#if(type(f) == str) : path = f
		path = fd.path
		self.headerWidget.setInfo(fd)

		
		self.editor.setCurrent(fd)
		if self.currentView in ('anim', 'frame'):
			self.entityEditor.loadLines(fd.lines)
		elif self.currentView == 'level':
			self.levelEditor.loadLines(fd.lines)
			
			
		if self.currentView == "favorite":
			self.setView("text")
			
		


	def openFile(self, path=None):
		
		if path is None:
			current = self.editor.current()
			if current is None or current.path is None:
				lookFolder = ROOT_PATH
			else:
				lookFolder = os.path.dirname(self.editor.current().path)
			path = QtWidgets.QFileDialog.getOpenFileName(self, directory=lookFolder)[0]
			
		
		if(path is not None and path != ''):
			
			fd = self.fileSelector.addFile(path)
			fd.loadFromDisk()
			
			self.loadFile(fd, False)
		
	def remove(self, fd):
		self.editor.remove(fd)

			 
	def save(self):
		if self.currentView == 'favorite':
			self.favEditor.updateFD()
			current = self.favEditor.current()
			current.save()
		else:
			self.updateFD()
			current = self.editor.current()
			if current is None or current.path is None:
				self.saveAs()
			else:
				current.lines = self.editor.getLines()
				current.save()
			
	def saveAs(self):
		current = self.editor.current()
		if current is None or current.path is None:
			lookFolder = ROOT_PATH
		else:
			lookFolder = os.path.dirname(self.editor.current().path)
			
		path = QtWidgets.QFileDialog.getSaveFileName(self, directory=lookFolder)[0]
		if(path is not None and path != ''):
			self.fileSelector.remove(current.getLongText()) # Old replaced

			self.editor.current().path = path
			self.save()
			fd = self.fileSelector.addFile(path)
			fd.category = current.category
			
			
	
	def setupFavorites(self):
		
		self.favorites = {}
		self.favEditor = EverydayEditor(self)
		
		
		
		data_path = settings.get_option('general/data_path', '')
		logPath = os.path.join(os.path.dirname(data_path), 'Logs', 'OpenBorLog.txt')
		todoPath = os.path.join(data_path, 'TODO.txt')
		#self.favEditor.setCurrent(fd)
		
		
		
		favorites = {'Log': logPath, 'Todo':todoPath}
		
		for key, path in favorites.items():
			fd = File(path)
			fd.loadFromDisk()
			self.favorites[key] = fd
	
	
	'''
		Change the current view
	
	'''
	def setView(self, view):
		self.updateFD()
		self.headerWidget.setInfo( self.editor.current())
		
		widgets = [self.editor, self.entityEditor, self.levelEditor, self.favEditor]
	
		if view == 'text':
			self.editor.setDoubleView(False)
			
			
			for w in widgets : w.hide()
			self.editor.show()
			
			
		elif view == 'text|text':
			
			self.editor.setDoubleView(True)
			
			
			
			for w in widgets : w.hide()
			self.editor.show()

		elif view == 'anim':
			for w in widgets : w.hide()
			lines = self.editor.getLines()
			self.entityEditor.loadLines(lines)
			
			# Load anim we were editing in text view
			lineNumber, c = self.editor.editor.cursorPosition
			while lineNumber > 0:
				pLine = ParsedLine( lines[lineNumber])
				part = pLine.next()
				if part == 'anim':
					part = pLine.next()
					self.entityEditor.loadAnim(part)
					break
				lineNumber -= 1
				
			self.entityEditor.show()
			
			
		elif view == 'level':
			for w in widgets : w.hide()
			self.levelEditor.show()
			self.levelEditor.loadLines(self.editor.getLines())
		elif view == 'favorite':
			for w in widgets : w.hide()
			self.favEditor.show()
			self.favEditor.setCurrent(self.favorites[self.sender().data()])
			#self.favEditor.editor.setFocus()

			
		self.currentView = view
		

	def setTheme(self):
		import themes
		data1 = dict(themes.EDITOR_THEME.items('Editor Colors'))
		data2 = dict(themes.EDITOR_THEME.items('Default Item Styles'))
		fontColor = data2['Normal'].split(',')

		css = ["background-color:rgb(" + str( data1['Color Background']) + ")",
			"selection-background-color: rgb(" + str( data1['Color Selection']) + ")",
			"color: #" + str( fontColor[0]),
			"selection-color: #" + str( fontColor[1]),
			"font-family:" + settings.get_option("editor/font_family", "Courier")
			]
		

		selectionColor = data1['Color Highlighted Line']
		searchColor = data1['Color Search Highlight']
		
		r, g, b = map(int, selectionColor.split(','))
		rS, gS, bS = map(int, searchColor.split(','))
		#'color:#ff839496;selection-color:#ff839496;"
		
		self.editor.themeData = {'css':css, 'searchColor':QtGui.QColor(rS, gS, bS), 'currentLine':QtGui.QColor(r, g, b)}
		
		for editor in (self.editor.getEditors() + [self.entityEditor.editor]):
			editor.setStyleSheet('QPlainTextEdit {' + ';'.join(css) + '}')
			editor.searchColor = QtGui.QColor(rS, gS, bS)
			editor.highlightColor = QtGui.QColor(r, g, b)
			editor._updateExtraSelections()
		
		
		ColorTheme.setThemeDescr(data2, dict(themes.EDITOR_THEME.items('Highlighting C - Schema ' + themes.EDITOR_THEME.name)))
		
		
	def updateFD(self):
		# TODO update data from current editor (eg entityEditor) in main editor if view is not text
		if(self.currentView == 'anim'):
			self.editor.setLines(self.entityEditor.getFullLines())
			if self.entityEditor.currentAnim != None:
				self.editor.scrollTo(QtCore.QRegExp("anim(\\s)"+self.entityEditor.currentAnim))
		elif(self.currentView == 'level'):
			self.levelEditor.looping = False
			lines = self.levelEditor.rebuildText()
			self.editor.setLines(lines)
		self.editor.updateFD()
		


class HeaderWidget(QtWidgets.QWidget):
	
	TYPE_FIELDS = (('File', _('File')), ('Entity', _('Entity')), ('Level', _('Level')), ('Script', _('Script')))
	
	TYPE_FIELDMODEL = QtGui.QStandardItemModel()
	for key, label in TYPE_FIELDS:
		TYPE_FIELDMODEL.appendRow([QtGui.QStandardItem(key), QtGui.QStandardItem(label)])
	
	def __init__(self, parent):
		self.parent = parent
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QHBoxLayout()
		self.setLayout(layout)
		
		self.pic = QtGui.QIcon.fromTheme('accessories-text-editor').pixmap(32)
		self.pic = QtGui.QPixmap('icons/oxygen/accessories-text-editor.png')
		#self.pic = self.pic.scaled(150, 150, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
		self.iconWidget= QtWidgets.QLabel()
		self.iconWidget.setStyleSheet("border: 1px solid black");
		self.iconWidget.setPixmap(self.pic)
		
		layout.addWidget(self.iconWidget, 0)
		
		self.fileTypeCB = QtWidgets.QComboBox()
		self.fileTypeCB.setModel(self.TYPE_FIELDMODEL)
		self.fileTypeCB.setModelColumn(1)
		self.fileTypeCB.setToolTip(_('Change file category'))
		
		self.fileTypeCB.currentIndexChanged[int].connect(self.setFileType)
		
		self.fileTypeCB.setObjectName("fileTypeCB")
		

		layout.addWidget(self.fileTypeCB)
		
		self.label = QtWidgets.QLabel('-')
		font = QtGui.QFont()
		font.setPointSize(16)
		self.label.setFont(font)

		layout.addWidget(self.label, 0)
		layout.addSpacing(100)
		
		
		#buttonGroup = QtWidgets.QButtonGroup()
		actionGroup = QtWidgets.QActionGroup(self)
		self.buttonBar = QtWidgets.QToolBar()
		
		smallScreenMode = settings.get_option('gui/small_screen', False)
		if smallScreenMode:
			self.buttonBar.setStyleSheet('QToolButton#MainToolButton {  margin:0px 0px; padding: 0px 0px; }')
			labels = {'Text':'T', 'Text|Text':'T|T', 'Animation':'A', 'Scripts':'S', 'Level':'L'}
		else:
			labels = {'Text':'Text', 'Text|Text':'Text|Text', 'Animation':'Animation', 'Scripts':'Scripts', 'Level':'Level'}
		b1 = self.buttonBar.addAction(labels['Text'], lambda:self.parent.setView('text'))
		b1.setToolTip(_('Text'))
		b1bis = self.buttonBar.addAction(labels['Text|Text'], lambda:self.parent.setView('text|text'))
		b1bis.setToolTip('Text|Text')
		b2 = self.buttonBar.addAction(labels['Animation'], lambda:self.parent.setView('anim'))
		b2.setToolTip('Animation')
		#b3 = self.buttonBar.addAction('Frame', lambda:self.parent.setView('frame'))
		b4 = self.buttonBar.addAction(labels['Scripts'], lambda:self.parent.setView('scripts'))
		b4.setToolTip('Scripts')
		b5 = self.buttonBar.addAction(labels['Level'], lambda:self.parent.setView('level'))
		b5.setToolTip('Level')
		
		self.animationAction = b2
		self.levelAction = b5
	
		#b3.setCheckable(True)
		b4.setEnabled(False)
		
		
		
		font.setPointSize(12)
		for b in (b1, b1bis, b2, b4, b5):
			b.setCheckable(True)
			for w in b.associatedWidgets():
				w.setObjectName( "MainToolButton" )
			#import style
			#b.setStyleSheet(style.STYLE_SHEET)
			b.setFont(font)
			actionGroup.addAction(b)
		b1.setChecked(True)
		#buttonGroup.addButton(self.buttonBar.widgetForAction(b1))
		#buttonGroup.addButton(self.buttonBar.widgetForAction(b2))
		#buttonGroup.addButton(self.buttonBar.widgetForAction(b3))
		
		
		
		layout.addWidget(self.buttonBar)
		
		
		layout.addStretch(1)
		self.quickAccessBar = QtWidgets.QToolBar()
		
		for key in sorted(self.parent.favorites):
			b = self.quickAccessBar.addAction(key, lambda:self.parent.setView('favorite'))
			b.setData(key)
			b.setCheckable(True)
			actionGroup.addAction(b)

		layout.addWidget(self.quickAccessBar)
		self.settingType = False
		
		
		
	def setInfo(self, fd):
		self.window().setWindowTitle(settings.get_option('general/last_session', 'Default') + ': ' + fd.name + ' — CMT')
		if fd.category == 'Entity':
			self.animationAction.setEnabled(True)
		else:
			self.animationAction.setEnabled(False)
			
		if fd.category == 'Level':
			self.levelAction.setEnabled(True)
		else:
			self.levelAction.setEnabled(False)
		txt = fd.getLongText()
		if len(txt) > 20 : txt = '...' + txt[-20:]
		self.setText(txt)
		if fd.iconPath is not None:
			print(fd.iconPath)
			self.pic.load(fd.iconPath)
			self.pic = self.pic.scaledToWidth(25)
			self.iconWidget.setPixmap(self.pic)
		else:
			self.iconWidget.setPixmap(QtGui.QPixmap())
			
		
		toMatch = fd.category
		pos = 0

		self.settingType = True
		while pos < len(self.TYPE_FIELDS) and not self.TYPE_FIELDS[pos][0] == toMatch :
			pos += 1
		if pos < len(self.TYPE_FIELDS) and self.TYPE_FIELDS[pos][0] == toMatch:
			self.fileTypeCB.setCurrentIndex(pos)
		self.settingType = False
			
			
	def setFileType(self, pos=None):
		if self.settingType: return
		if pos is None:
			pos = self.fileTypeCB.currentIndex()

		key = self.TYPE_FIELDS[pos][0]
		
		fd = self.parent.editor.current()
		fd.category = key
		self.setInfo(fd)
		
	def setText(self, text):
		self.label.setText(text)
