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

		self.currentPath = None

		
		#self.loadProject()
		
		rightSide = QtWidgets.QWidget()
		rightLayout = QtWidgets.QVBoxLayout()
		rightSide.setLayout(rightLayout)
		
		self.headerWidget = HeaderWidget(self)
		rightLayout.addWidget(self.headerWidget, 0)
		rightLayout.addWidget(self.editor, 1)
		
		self.entityEditor = EntityEditorWidget()
		self.levelEditor = LevelEditorWidget()
		rightLayout.addWidget(self.entityEditor, 1)
		rightLayout.addWidget(self.levelEditor, 1)
		self.entityEditor.hide()
		self.levelEditor.hide()
		
		
		
		
		splitter.addWidget(self.fileSelector)
		splitter.addWidget(rightSide)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+D", "Edit|Comment")), self, self.editor.comment)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Shift+Ctrl+D", "Edit|Uncomment")), self, self.editor.uncomment)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+F", "Edit|Find")), self, self.editor.focusForSearch)
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+R", "Edit|Replace")), self, self.editor.replaceEntry.setFocus)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+W", "File|Close")), self, self.fileSelector.close)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+H", "File|Close")), self, self.editor.editor.highlightCurrentWord)
				
		self.splitter.setStretchFactor(0,0)
		self.splitter.setStretchFactor(1,1)
		
		self.currentView = 'text'
		
	def close(self, all=False):
		return self.fileSelector.close(all)
		
		
	def editNew(self):
		fd = self.fileSelector.addFile('New')
		fd.lines = []
		self.loadFile(fd, False)
		
		
	def loadProject(self, path=None):
	
		if path is None:
			path = settings.get_option('general/data_path', '')
		
		global ROOT_PATH
		ROOT_PATH = os.path.dirname(path)
		FileSelector.ROOT_PATH = ROOT_PATH
		EntityEditorWidget.ROOT_PATH = ROOT_PATH
		
				
		self.fileSelector.loadLibrary()
		
	def loadFile(self, fd, rel=True):
		#if(type(f) == str) : path = f
		path = fd.path
		self.headerWidget.setInfo(fd)
		#@util.threaded
		def detectSyntax():
			if extension == '.txt':
				#self.editor.detectSyntax(xmlFileName='c.xml')
				self.editor.editor.detectSyntax(xmlFileName='entity.xml')
			else:
				self.editor.editor.detectSyntax(sourceFilePath=path)
			
		if rel:
			path = ROOT_PATH + path
		
		
		if path is not None:
			extension = os.path.splitext(path)[1]
			#mt = mimetypes.guess_type(path)[0]
			#print(mt)
		else:
			extension = None
		detectSyntax()
		
		self.editor.setCurrent(fd)
		if self.currentView in ('anim', 'frame'):
			self.entityEditor.loadLines(fd.lines)
		elif self.currentView == 'level':
			self.levelEditor.loadLines(fd.lines)
			
		


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
			 
	def save(self):
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
			
			
	
	
	def setView(self, view):
		self.updateFD()
	
		if view == 'text':
			self.editor.editor2.hide()
			self.editor.editor = self.editor.editor1
			self.editor.editor.setFocus()
			self.editor.show()
			
			self.entityEditor.hide()
			self.levelEditor.hide()
			
			
		elif view == 'text|text':
			
			self.editor.editor1.show()
			self.editor.editor2.show()
			self.editor.show()
			self.entityEditor.hide()
			self.levelEditor.hide()
			self.editor.editor.setFocus()
		elif view == 'anim':
			self.editor.hide()
			self.levelEditor.hide()
			self.entityEditor.loadLines(self.editor.getLines())
			self.entityEditor.show()
		elif view == 'level':
			self.editor.hide()
			self.entityEditor.hide()
			self.levelEditor.show()
			self.levelEditor.loadLines(self.editor.getLines())

			
		self.currentView = view
		

	def setTheme(self):
		import themes
		data1 = dict(themes.EDITOR_THEME.items('Editor Colors'))
		data2 = dict(themes.EDITOR_THEME.items('Default Item Styles'))
		fontColor = data2['Normal'].split(',')

		css = ["background-color:rgb(" + str( data1['Color Background']) + ")",
			"selection-background-color: rgb(" + str( data1['Color Selection']) + ")",
			"color: #" + str( fontColor[0]),
			"selection-color: #" + str( fontColor[1])
			]
		

		selectionColor = data1['Color Highlighted Line']
		r, g, b = map(int, selectionColor.split(','))
		#'color:#ff839496;selection-color:#ff839496;"
		for editor in (self.editor.editor1, self.editor.editor2, self.entityEditor.editor):
			editor.setStyleSheet('QPlainTextEdit {' + ';'.join(css) + '}')
			
			editor.highlightColor = QtGui.QColor(r, g, b)
			editor._updateExtraSelections()
		
		
		ColorTheme.setThemeDescr(data2, dict(themes.EDITOR_THEME.items('Highlighting C - Schema ' + themes.EDITOR_THEME.name)))
		
		
	def updateFD(self):
		# TODO update data from current editor (eg entityEditor) in main editor if view is not text
		if(self.currentView == 'anim'):
			self.editor.setLines(self.entityEditor.getFullLines())
		elif(self.currentView == 'level'):
			lines = self.levelEditor.rebuildText()
			self.editor.setLines(lines)
		self.editor.updateFD()
		
	
class EverydayEditor(QtWidgets.QWidget):
	def __init__(self, parent):
		self.parent = parent
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		self.editor1 = EverydayPart()
		self.editor2 = EverydayPart()
		self.editor2.hide()
		self.editor = self.editor1
		#font = QtGui.QFont("Monospace")
		font = QtGui.QFont("Courier")
		font.setPointSize(12)
		self.editor.setFont(font)
		self.editor.currentFont = font
		
		self.editor.drawIncorrectIndentation = False
		self.editor.indentUseTabs = True
		
		font = QtGui.QFont("Courier")
		font.setPointSize(12)
		self.editor2.setFont(font)
		self.editor2.currentFont = font
		
		
		
		#selection = QtWidgets.QTextEdit.ExtraSelection()
		#selection.cursor = self.editor.textCursor()
		##selection.format.setBackground(lineColor)
		#selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
		#self.editor.setExtraSelections([selection])

		# Initialize current FileData
		self.editor1.current = File()
		self.editor2.current = File()
		
		self.editor1.installEventFilter(self)
		self.editor2.installEventFilter(self)
		
		self.editor1.textChanged.connect(self.notifyChange)
		
		editorLayout = QtWidgets.QSplitter()
		
		editorLayout.addWidget(self.editor1)
		editorLayout.addWidget(self.editor2)
		
		layout.addWidget(editorLayout, 1)
		
		actionBox = QtWidgets.QHBoxLayout()
		scrollToCurrentButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-jump'), None)
		#scrollToCurrentButton.clicked.connect(self.scrollToCurrent)
		searchEntry = QtWidgets.QLineEdit()
		searchEntry.returnPressed.connect(self.search)
		self.searchEntry = searchEntry
		#searchEntry.textChanged.connect(self.filter)
		actionBox.addWidget(scrollToCurrentButton, 0)
		actionBox.addWidget(searchEntry, 1)
		
		layout.addLayout(actionBox, 0)
		
		actionBox = QtWidgets.QHBoxLayout()
		scrollToCurrentButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-jump'), None)
		#scrollToCurrentButton.clicked.connect(self.scrollToCurrent)
		replaceEntry = QtWidgets.QLineEdit()
		replaceEntry.returnPressed.connect(self.replace)
		#searchEntry.textChanged.connect(self.filter)
		actionBox.addWidget(scrollToCurrentButton, 0)
		actionBox.addWidget(replaceEntry, 1)
		
		layout.addLayout(actionBox, 0)
		
		self.replaceEntry = replaceEntry
		self.updating = False
		
		
	def current(self):
		return self.editor.current
		
	def comment(self):
		start, end = self.editor.selectedPosition
		start = start[0]
		end = end[0]
		if end < start:
			tmp = end
			end = start
			start = tmp
		print(start, end)
		for i in range(start, end+1):
			lineContent = self.editor.lines[i]
			if len(lineContent) == 0:
				continue
			j = 0
			while j < len(lineContent) and lineContent[j] in (' ', '	'):
				j+=1
			if j != len(lineContent):
				lineContent = lineContent[0:j] + '#' + lineContent[j:] # insert(j, '#')
				self.editor.lines[i] = lineContent
			
		
	def uncomment(self):
		start, end = self.editor.selectedPosition
		start = start[0]
		end = end[0]
		if end < start:
			tmp = end
			end = start
			start = tmp
		for i in range(start, end+1):
			lineContent = self.editor.lines[i]
			if len(lineContent) == 0:
				continue
			j = 0
			while j < len(lineContent) and lineContent[j] in (' ', '	'):
				j+=1
			if j != len(lineContent) and lineContent[j] == '#':
				k = j-1
				if k < 0 : k = 0
				lineContent = lineContent[0:j] + lineContent[j+1:]
				self.editor.lines[i] = lineContent
		
	def eventFilter(self, obj, e):
		#print(e.type(), e.FocusIn)
		if(e.type() == e.FocusIn and (obj == self.editor1 or obj == self.editor2)):
			if obj == self.editor1:
				self.parent.headerWidget.setInfo(self.editor2.current)
				self.editor2.current.state = 0
			else:
				self.parent.headerWidget.setInfo(self.editor1.current)
				self.editor1.current.state = 0
			obj.current.state = 1
			self.editor = obj
			#return True
		#else:
		return False
	
	
	def focusForSearch(self):
		self.searchEntry.setFocus()
		selection = self.editor.selectedText

		if selection != '':
			text = selection
			self.searchEntry.setText(text)
	
	def getLines(self):
		return self.editor.lines
	
	
	def notifyChange(self):
		if self.updating : return
		self.editor.current.saved = False
		
		
	def replace(self):
		replaceEntry = self.sender()
		self.editor.selectedText = replaceEntry.text()
		self.search()
		
	def search(self):
		self.editor.setCenterOnScroll(True)
		

		text = self.searchEntry.text()

		if not self.editor.find(text):
			self.editor.moveCursor(QtGui.QTextCursor.Start)
			
	def setCurrent(self, fd):
		self.editor.current.lines = list(self.editor.lines)
		self.updating = True
		self.editor.lines = fd.lines
		self.editor.current = fd
		self.updating = False
		
		
	def updateFD(self):
		self.editor1.current.lines = list(self.editor1.lines)
		self.editor2.current.lines = list(self.editor2.lines)
			
	def setLines(self, lines):
		self.editor.lines = lines
		



class HeaderWidget(QtWidgets.QWidget):
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
		
		self.label = QtWidgets.QLabel('-')
		font = QtGui.QFont()
		font.setPointSize(16)
		self.label.setFont(font)

		layout.addWidget(self.label, 0)
		layout.addSpacing(100)
		
		
		#buttonGroup = QtWidgets.QButtonGroup()
		actionGroup = QtWidgets.QActionGroup(self)
		self.buttonBar = QtWidgets.QToolBar()
		
		b1 = self.buttonBar.addAction('Text', lambda:self.parent.setView('text'))
		b1bis = self.buttonBar.addAction('Text|Text', lambda:self.parent.setView('text|text'))
		b2 = self.buttonBar.addAction('Animation', lambda:self.parent.setView('anim'))
		#b3 = self.buttonBar.addAction('Frame', lambda:self.parent.setView('frame'))
		b4 = self.buttonBar.addAction('Scripts', lambda:self.parent.setView('scripts'))
		b5 = self.buttonBar.addAction('Level', lambda:self.parent.setView('level'))
		
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
		
	def setInfo(self, fd):
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
		self.setText('[' + fd.category + '] ' + txt)
		if fd.iconPath is not None:
			print(fd.iconPath)
			self.pic.load(fd.iconPath)
			self.iconWidget.setPixmap(self.pic)
		else:
			self.iconWidget.setPixmap(QtGui.QPixmap())
		
	def setText(self, text):
		self.label.setText(text)
		