import os, re, time, mimetypes

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from common import util
from common import settings
from gui.util import FileInput, getSpriteShowingPath, loadSprite

from gui import modales

from gui.portrait import IconViewer, Portrait

from qutepart import EverydayPart

from data import ParsedLine

from gui.main.fileselector import FileSelector, File
from gui.entity import EntityEditorWidget
from gui.entity.animselector import AnimSelector

from gui.level import LevelEditorWidget

ROOT_PATH = '/home/piccolo/workspace/OpenBOR/'

from qutepart.syntax.colortheme import ColorTheme



class AbstractEverydayEditor(QtWidgets.QWidget):
	def __init__(self, parent):
		self.parent = parent
		
		QtWidgets.QWidget.__init__(self)
		
		
	def current(self):
		return self.editor.fd
		
		
	def comment(self):
		#print (self.editor._highlighter.syntax().comment)
		with self.editor:
			start, end = self.editor.selectedPosition
			
			
			if (end[0] < start[0]) or (end[0] == start[0] and end[1] < start[1]):

				tmp = end
				end = start
				start = tmp
			print(start, end)
			
			startCol = start[1]
			start = start[0]
			endCol = end[1]+2
			end = end[0]
			
			
			
			
				
				#tmp = endCol
				#endCol = startCol
				#startCol = tmp
			#print(start, end)
			
			cs = self.getCommentString(start)
			multiLine = False
			if(cs == '/*'):
				closeCS = '*/'
				multiLine = True
				
			
		
				
			
				
			if(multiLine):
				if(start == end and startCol == endCol-2):
					lineContent = self.editor.lines[start]
					self.editor.lines[start] = cs + lineContent + closeCS
					return
				
				
				lineContent = self.editor.lines[start]
				j = startCol
				lineContent = lineContent[0:j] + cs + lineContent[j:] # insert(j, '#')
				self.editor.lines[start] = lineContent
				
				lineContent = self.editor.lines[end]
				j = endCol
				lineContent = lineContent[0:j] + closeCS + lineContent[j:] # insert(j, '#')
				self.editor.lines[end] = lineContent
				
				return
			
			for i in range(start, end+1):
				lineContent = self.editor.lines[i]
				if len(lineContent) == 0:
					continue
				j = 0
				while j < len(lineContent) and lineContent[j] in (' ', '	'):
					j+=1
				if j != len(lineContent):
					lineContent = lineContent[0:j] + cs + lineContent[j:] # insert(j, '#')
					self.editor.lines[i] = lineContent
			
		
	def uncomment(self):
		with self.editor:
			start, end = self.editor.selectedPosition
			
			if (end[0] < start[0]) or (end[0] == start[0] and end[1] < start[1]):

				tmp = end
				end = start
				start = tmp
			print(start, end)
			
			startCol = start[1]
			start = start[0]
			endCol = end[1]+2
			end = end[0]
				
			cs = self.getCommentString(start)
			multiLine = False
			if(cs == '/*'):
				closeCS = '*/'
				multiLine = True
			
			if(multiLine):
				lineContent = self.editor.lines[start]
				lineContent = lineContent.replace(cs, '', 1)
				self.editor.lines[start] = lineContent
				
				lineContent = self.editor.lines[end]
				lineContent = lineContent[::-1]
				lineContent = lineContent.replace(cs, '', 1)
				lineContent = lineContent[::-1]
				self.editor.lines[end] = lineContent
				
				
				
				
				return
				
			
			for i in range(start, end+1):
				lineContent = self.editor.lines[i]
				if len(lineContent) == 0:
					continue
				j = 0
				while j < len(lineContent) and lineContent[j] in (' ', '	'):
					j+=1
				if j != len(lineContent) and lineContent[j:j+len(cs)] == cs:
					lineContent = lineContent[0:j] + lineContent[j+len(cs):]
					self.editor.lines[i] = lineContent
	
	
	def getLines(self):
		return self.editor.lines
		
	def focusForSearch(self):
		print('focusForSearch');
		self.editor.initialSearchPos = None # so that it will takes cursor current position
		self.searchEntry.setFocus()
		selection = self.editor.selectedText

		if selection != '':
			text = selection
			self.searchEntry.setText(text)
		self.searchEntry.selectAll()
		
	def focusForReplace(self):
		self.replaceEntry.setFocus()
		# selection = self.editor.selectedText
  # 
		# if selection != '':
		# 	text = selection
		# 	self.searchEntry.setText(text)
		self.replaceEntry.selectAll()
		
	def getCommentString(self, blockNumber):
		lang = self.editor.language()
		#print('langage', lang)
		if lang is None : return '#'
		if lang == 'Entity':
			context = self.editor.getContext(blockNumber)
			#print('context', context, context == 'Script')
			if context == 'Script' : return '//'
			else : return '#'
		elif lang is 'C':
			return '//'
		else:
			try:
				#print('here', self.editor._highlighter.syntax().__dir__())
				#print('here', vars(self.editor._highlighter.syntax()))
				return self.editor._highlighter.syntax().comment
			except:
				pass
		return '#'
	
	def notifyChange(self):
		if self.updating : return
		# if self.editor.fd.saved:
		self.updateFD()
		self.editor.fd.checkSave()
			
	def refresh(self):
		fd = self.current()
		if fd.path is None : return
		if(QtWidgets.QMessageBox.question(self, _('Refresh file'), _('Are you sure you want to reload the current file ?'), defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
			fd.loadFromDisk()
			self.setLines(fd.lines)
			
	def replace(self):
		replaceEntry = self.replaceEntry
		if(self.editor.selectedText != ''):
			self.editor.selectedText = replaceEntry.text()
			self.search()
		
	def replaceAll_OLD(self):
		
		self.editor.updatingCursor = True
		text = self.searchEntry.text()
		replaceWith = self.replaceEntry.text()
		lines = self.editor.lines
		newLines = []
		for line in lines:
			newLines.append(line.replace(text, replaceWith))
		
		self.editor.lines = newLines
		self.editor.updatingCursor = False
		
		
		
	def replaceAll(self):
		
		
		
		replaceEntry = self.replaceEntry
		newTxt = replaceEntry.text()
		
		if(self.editor.selectedText != ''):
			self.editor.replaceAllRaw(self.searchEntry.text(), newTxt)
			return
		
		self.editor.initialSearchPos = self.editor.textCursor()
		self.editor.moveCursor(QtGui.QTextCursor.Start)
		i= 0
		while self.search(True, False):
			
			self.editor.selectedText = newTxt
			i+=1
			# self.search(True, False)
			
		QtWidgets.QMessageBox.information(self, _('Replaced'), _(str(i) + " entries replaced"))
		
	def search(self, searchForward=True, loop=True):
		self.editor.setCenterOnScroll(True)
		
		print('editor', self.editor.initialSearchPos)
		if(self.editor.initialSearchPos == None):
			self.editor.initialSearchPos = self.editor.textCursor()
			
		text = self.searchEntry.text()
		print('text', text)
		if(text == ''): 
			self.searchEntry.setStyleSheet("")
			self.editor.setTextCursor(self.editor.initialSearchPos)
			self.editor.initialSearchPos = None
			return False

		if searchForward:
			options = QtGui.QTextDocument.FindFlags()
		else:
			options = QtGui.QTextDocument.FindBackward
		result = self.editor.find(text, options) # first try to search from cursor to end of document
		
		if(result):
			if(not self.dark):
				self.searchEntry.setStyleSheet("QLineEdit { background: rgb(175, 255, 175); }");
			else:
				self.searchEntry.setStyleSheet("QLineEdit { background: rgb(60, 145, 60); }");
			return True
		
		elif(loop and not result):
			self.editor.moveCursor(QtGui.QTextCursor.Start)
			if not self.editor.find(text, options): # then try to search from start to end of document
			
			
				# self.editor.moveCursor(self.editor.initialSearchPos)
				self.editor.setTextCursor(self.editor.initialSearchPos)
				self.editor.initialSearchPos = None
			
				if(not self.dark):
					self.searchEntry.setStyleSheet("QLineEdit { background: rgb(255, 175, 175); }");
				else:
					self.searchEntry.setStyleSheet("QLineEdit { background: rgb(120, 50, 50); }");
				 # selection-background-color: rgb(233, 99, 0);
				 
				return False
			else:
				
				if(not self.dark):
					self.searchEntry.setStyleSheet("QLineEdit { background: rgb(175, 255, 175); }");
				else:
					self.searchEntry.setStyleSheet("QLineEdit { background: rgb(60, 145, 60); }");
				return True
	
			
				
			

			
	def searchPrevious(self):
		self.search(False)
		
	def searchTextChanged(self):
		if(self.editor.initialSearchPos != None):
			self.editor.setTextCursor(self.editor.initialSearchPos)
		
		self.search()
			
		
		
			
	def setLines(self, lines):
		self.updating = True
		self.editor.lines = lines
		self.updating = False
		
	def scrollTo(self, text):
		self.editor.setCenterOnScroll(True)
		self.editor.find(text)

	
	
	
class EverydayEditor(AbstractEverydayEditor):
	def __init__(self, parent):
		AbstractEverydayEditor.__init__(self, parent)
		
		mainLayout = QtWidgets.QHBoxLayout()
		
		self.animSelector = AnimSelector(self, ['hideUpperBar'])
		
		
		
		
		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(5, 0, 5, 5)
		# layout.setSpacing(0)
		
		editorContainerWidget = QtWidgets.QWidget()
		
		editorContainerWidget.setLayout(layout)
		
		if(settings.get_option('editor/anim_selector_on_left', False)):
			
			mainLayout.addWidget(self.animSelector, 0)
			mainLayout.addWidget(editorContainerWidget, 1)
		else:
			mainLayout.addWidget(editorContainerWidget, 1)
			mainLayout.addWidget(self.animSelector, 0)
		
		self.animSelector.hide()
		
		self.setLayout(mainLayout)
		
		
		self.stack1 = QtWidgets.QStackedWidget()
		self.stack1.fd_list = {}
		self.stack2 = QtWidgets.QStackedWidget()
		self.stack2.hide()
		self.stack2.fd_list = {}
		
		
		self.themeData = None
		self.editor = self.addToStack(File(), self.stack1)
		self.addToStack(File(), self.stack2)
		
		
		#selection = QtWidgets.QTextEdit.ExtraSelection()
		#selection.cursor = self.editor.textCursor()
		##selection.format.setBackground(lineColor)
		#selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
		#self.editor.setExtraSelections([selection])

		# Initialize current FileData
		
		
		
		editorLayout = QtWidgets.QSplitter()
		
		editorLayout.addWidget(self.stack1)
		editorLayout.addWidget(self.stack2)
		
		theme = settings.get_option('gui/widgets_theme', None)
		
		if(theme == "Dark"):
			self.dark = True
		else:
			self.dark = False
		
		
		self.buttonBar = QtWidgets.QToolBar()
		# self.buttonBar.setContentsMargins(0, 0, 0, 0)
		self.setStyleSheet("QToolBar { margin:0px; padding:0px; }");
		 # border-top:1px solid #c9c9c9;
		# saveIcon = QtGui.QIcon.fromTheme('document-save')
		saveImage = QtGui.QImage('icons/save.svg')
		if(theme == "Dark"): saveImage.invertPixels()
		
		saveIcon = QtGui.QIcon(QtGui.QPixmap.fromImage(saveImage))
		
		save = self.buttonBar.addAction(saveIcon, _('Save file (Ctrl+S)'), self.save)
		
		saveImage = QtGui.QImage('icons/undo.svg')
		if(theme == "Dark"): saveImage.invertPixels()
		
		undoIcon = QtGui.QIcon(QtGui.QPixmap.fromImage(saveImage))
		save = self.buttonBar.addAction(undoIcon, _('Undo (Ctrl+Z)'), self.undo)
		
		saveImage = QtGui.QImage('icons/redo.svg')
		if(theme == "Dark"): saveImage.invertPixels()
		
		redoIcon = QtGui.QIcon(QtGui.QPixmap.fromImage(saveImage))
		save = self.buttonBar.addAction(redoIcon, _('Redo (Ctrl+Shift+Z)'), self.redo)
		
		
		genPaths = self.buttonBar.addAction( _('Generate paths'), self.generatePaths)
		
		viewRevisions = self.buttonBar.addAction( _('View revisions'), self.viewRevisions)
		
		self.boldButton = self.buttonBar.addAction( _('Bold'), self.toggleBold)
		self.boldButton.setCheckable(True)
		self.boldButton.setChecked(settings.get_option('editor/force_bold', True))
		
		layout.addWidget(self.buttonBar, 0)
		
		layout.addWidget(editorLayout, 1)
		
		actionBox = QtWidgets.QHBoxLayout()
		# findNext = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-down'), None)
		# findPrevious = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-up'), None)
		findNext = QtWidgets.QPushButton(redoIcon, None)
		findPrevious = QtWidgets.QPushButton(undoIcon, None)
		findNext.pressed.connect(self.search)
		findPrevious.pressed.connect(self.searchPrevious)
		searchEntry = QtWidgets.QLineEdit()
		searchEntry.returnPressed.connect(self.search)
		self.searchEntry = searchEntry
		# searchEntry.textChanged.connect(self.filter)
		searchEntry.textChanged.connect(self.searchTextChanged)
		actionBox.addWidget(QtWidgets.QLabel(_('Search') + ' :'), 0)
		
		actionBox.addWidget(searchEntry, 1)
		actionBox.addWidget(findNext, 0)
		actionBox.addWidget(findPrevious, 0)
		
		layout.addLayout(actionBox, 0)
		
		actionBox = QtWidgets.QHBoxLayout()
		replace = QtWidgets.QPushButton(_('&Replace'))
		replaceAll = QtWidgets.QPushButton(_("Replace &All"))
		replace.pressed.connect(self.replace)
		replaceAll.pressed.connect(self.replaceAll)
		#scrollToCurrentButton.clicked.connect(self.scrollToCurrent)
		replaceEntry = QtWidgets.QLineEdit()
		replaceEntry.returnPressed.connect(self.replace)
		#searchEntry.textChanged.connect(self.filter)
		actionBox.addWidget(QtWidgets.QLabel(_('Replace') + ' :'), 0)
		actionBox.addWidget(replaceEntry, 1)
		actionBox.addWidget(replace, 0)
		actionBox.addWidget(replaceAll, 0)
		
		layout.addLayout(actionBox, 0)
		
		self.replaceEntry = replaceEntry
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F5", "Refresh")), self, self.refresh)
		self.updating = False
		# self.setAcceptDrops(True)
		
		
		
		self.setTabOrder(self.searchEntry, self.replaceEntry)
		
		
	#@util.threaded
	def detectSyntax(self, editor, path):
		if(path is not None):
			extension = os.path.splitext(path)[1]
		else:
			extension = None
			
		if extension == '.txt':
			#self.editor.detectSyntax(xmlFileName='c.xml')
			theme = settings.get_option('gui/editor_theme', None)
			print("checking theme")
			if(theme != None and 'dark' in theme.lower()):
				print("theme is dark")
				editor.detectSyntax(xmlFileName='entity-dark.xml')
			else:
				editor.detectSyntax(xmlFileName='entity.xml')
		else:
			editor.detectSyntax(sourceFilePath=path)

				
	def addToStack(self, fd, stack=None):
		
				
		
		if stack is None: # Take current stack
			stack = self.editor.parent()
		
		editor = EverydayPart()
		editor.setTheme(self.themeData)
		
		editor.fd = fd
		
		
		self.initSettings(editor)
		stack.fd_list[fd] = editor
		stack.addWidget(editor)
		
		if fd.path is not None:
			extension = os.path.splitext(fd.path)[1]
			#mt = mimetypes.guess_type(path)[0]
			#print(mt)
		else:
			extension = None
		self.detectSyntax(editor, fd.path)
		if fd.lines != None:
			editor.lines = list(fd.lines)
		editor.textChanged.connect(self.notifyChange)
		editor.toolTipEvent.connect(self.showToolTip)
		editor.installEventFilter(self)
		return editor

		
		
	def initSettings(self, editor):
		fontFamily = settings.get_option('editor/font_family', 'Courier')
		fontSize = settings.get_option('editor/font_size', 12)
		font = QtGui.QFont(fontFamily)
		font.setPointSize(fontSize)
		editor.setFont(font)
		editor.currentFont = font
		
		editor.drawIncorrectIndentation = False
		editor.indentUseTabs = True
		

		
	# def dropEvent(self,e):
	# 	print("\nEditor Drop Event")
	# 	super().dropEvent(e)
		
	def eventFilter(self, obj, e):
		#print(e.type(), e.FocusIn)
		if(e.type() == e.FocusIn and type(obj) == EverydayPart):
			if self.stack1.indexOf(obj) != -1:
				self.parent.headerWidget.setInfo(obj.fd)
			elif self.stack2.indexOf(obj) != -1:
				self.parent.headerWidget.setInfo(obj.fd)
			
			#self.editor.fd.state = 0
			obj.fd.state = 1
			if(hasattr(self, "fileSelector")):
				self.fileSelector.updateStates(obj.fd)
			self.editor = obj
			#return True
			
			self.checkChangeOutside()
		#else:
		return False
	
	def checkChangeOutside(self):
		fd = self.editor.fd
		if not fd.checkMTime():
			if(QtWidgets.QMessageBox.question(self, _('Refresh file'), _('This file was changed outside CMT, would you like to reload it ?'), defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
				fd.loadFromDisk()
				self.setLines(fd.lines)
			else:
				fd.updateMTime()

	def keyPressEvent(self, e):
		
				
		if e.key() == QtCore.Qt.Key_Escape:
			print('escape pressed')
			self.editor.initialSearchPos = None
		else:
			AbstractEverydayEditor.keyPressEvent(self, e)
	


	def updateTheme(self):
		for fd in self.stack1.fd_list:
			editor = self.stack1.fd_list[fd]
			self.detectSyntax(editor, fd.path)
	
	def getEditors(self):
		return list(self.stack1.fd_list.values()) + list(self.stack2.fd_list.values())
	
	
	def generatePaths(self):
		res = modales.GeneratePathsDialog(self.editor).exec()
		
		#self.editor.selectedText = res
	
	
	def loadAnim(self, ID):
		#self.scrollTo(QtCore.QRegExp("anim(\\s)"+ID))
		self.editor.search(QtCore.QRegExp("anim(\\s)"+ID))
	
	def notifyChange(self):
		if self.updating : return
		AbstractEverydayEditor.notifyChange(self)
		fd = self.editor.fd
		self.updating = True
		# syncing content if file opened in multiple views
		if self.stack1.indexOf(self.editor) != -1:
			
			if fd in self.stack2.fd_list:
				toSyncEditor = self.stack2.fd_list[fd]
				#pos = toSyncEditor.cursorPosition
				toSyncEditor.saveScroll()
				toSyncEditor.lines = list(self.editor.lines)
				#toSyncEditor.setCenterOnScroll(True)
				#toSyncEditor.cursorPosition = pos
				
				#toSyncEditor.moveCursor(QtGui.QTextCursor.Start)
				toSyncEditor.restoreScroll()
				
		if self.stack2.indexOf(self.editor) != -1:
			
			if fd in self.stack1.fd_list:
				toSyncEditor = self.stack1.fd_list[fd]
				toSyncEditor.saveScroll()
				
				#pos = toSyncEditor.cursorPosition
				toSyncEditor.lines = list(self.editor.lines)
				#toSyncEditor.cursorPosition = pos
				toSyncEditor.restoreScroll()
		self.updating = False
	
	
	def redo(self):
		self.editor.redo()
	
	def remove(self, fd):
		if fd in self.stack1.fd_list:
			
			editor = self.stack1.fd_list[fd]
			wasCurrent = False
			if(editor == self.editor):
				wasCurrent = True
			self.stack1.removeWidget(editor)
			del self.stack1.fd_list[fd]
			if(wasCurrent):
				self.editor = self.stack1.currentWidget()
				self.parent.headerWidget.setInfo(self.editor.fd)

		
		if fd in self.stack2.fd_list:
			editor = self.stack2.fd_list[fd]
			wasCurrent = False
			if(editor == self.editor):
				wasCurrent = True
			
			self.stack2.removeWidget(editor)
			del self.stack2.fd_list[fd]
			if(wasCurrent):
				self.editor = self.stack2.currentWidget()
				self.parent.headerWidget.setInfo(self.editor.fd)
			
		
			


			
			
	def setDoubleView(self, doubleView):
		if doubleView:
			self.stack1.show()
			self.stack2.show()
			self.editor.setFocus()
		else:
			self.stack2.hide()
			self.editor = self.stack1.currentWidget()
			self.editor.setFocus()
			
	def setCurrent(self, fd, stack=None):
		if stack is None: # Take current stack
			stack = self.editor.parent()
		
		print('stack is', stack)
		if fd not in stack.fd_list:
			print('was not in stack')
			editor = self.addToStack(fd, stack)
		else:
			print('was in stack')
			editor = stack.fd_list[fd]

		stack.setCurrentWidget(editor)
		editor.setFocus()
		
		if(fd.category == 'Entity'):
			self.animSelector.show()
			self.animSelector.loadFrom(editor.lines)
		else:
			self.animSelector.hide()
		
		
		#self.editor.current.lines = list(self.editor.lines)
		#self.updating = True
		#editor.lines = fd.lines
		#self.editor.current = fd
		#self.updating = False
		
	def extractData(self, command, pLine):
		if(command not in('bglayer', 'fglayer', 'background', 'panel', 'frontpanel')):
			return ''
		params = {
	    'bglayer':["path" ,"xratio" ,"zratio" ,"xposition" ,"zposition" ,"xspacing" ,"zspacing" ,"xrepeat" ,"zrepeat" ,"transparency" ,"alpha" ,"watermode" ,"amplitude" ,"wavelength" ,"wavespeed" ,"bgspeedratio"],
	    
	    'fglayer':['path' ,"z" ,"xratio" ,"zratio" ,"xposition" ,"zposition" ,"xspacing" ,"zspacing" ,"xrepeat" ,"zrepeat" ,"transparency" ,"alpha" ,"watermode" ,"amplitude" ,"wavelength" ,"wavespeed" ,"bgspeedratio"],
	    
	    'background':["path" ,"xratio" ,"zratio" ,"xposition" ,"zposition" ,"xspacing" ,"zspacing" ,"xrepeat" ,"zrepeat" ,"transparency" ,"alpha"],
	    	
	    'panel':['path'],
	    'frontpanel':['path']
	    	
	    
		}
		
		i = 1
		txt = '<ul>'

		while(pLine.next() != None and i < len(params[command])):
			print('command', command, pLine.current(), params[command])
			txt += '<li>' + params[command][i] + ' = ' + pLine.current() + '</li>'
			i+= 1
			
		notSet = params[command][i:]
		if(len(notSet) > 0):
			txt += '<li>Not set : ' + ', '.join(notSet) + '</li>'
		return txt
	
	

	
	
	def showToolTip(self, lineNumber, text, e):
		try:
			if text.count('\n') > 0:
				lines = text.split('\n')
				frameCount = 0
				for line in lines:
					pLine = ParsedLine(line)
					part = pLine.next()
					if part == 'frame':
						frameCount += 1
						
				output = 'Selected "frame" count : ' + str(frameCount)
				QToolTip.showText(e.globalPos(), output)
				return
			elif text != '':
				pLine = ParsedLine(text)
				part = pLine.next()
				if part in ('frame', 'bglayer', 'fglayer', 'background', 'panel', 'frontpanel'):
					p = pLine.next()
					if(p is None): return
					print('tooltip', part, p)
					data_path = settings.get_option('general/data_path', '')
					path = os.path.join(os.path.dirname(data_path), p)
					print(path)
					
					
					com = pLine.getCom()
				
				
					transp = 0
					if('transp=' in com):
						parts = com.split('transp=')
						part = parts[1]
						parts = part.split(';')
						transp = parts[0]
					
					
					
					
					
					img = loadSprite(path, transp)
					data = QtCore.QByteArray()
					buffer = QtCore.QBuffer(data)
					#buffer.open(QtCore.QIODevice.WriteOnly);
					img.save(buffer, 'PNG')
					#print('ELIA', data.toBase64())
					b64 =  str(data.toBase64())[2:-1]
					text = "<div><img alt='Embedded Image' src='data:image/png;base64," + b64 + "' />"
					#text += "<img src='" + getSpriteShowingPath(path) + "'></div>"
					text += self.extractData(part, pLine)
					
					if(part == 'frame'):
						frameCount = 0
						part = None
						lineNumber = lineNumber -1
						while lineNumber >= 0 and part != 'anim':
							line = self.editor.lines[lineNumber]
							pLine = ParsedLine(line)
							part = pLine.next()
							if part == 'frame' :
								frameCount += 1
							lineNumber -=1
							
						text += '<br /><div>Frame number : ' + str(frameCount) + '</div>'
					
					QToolTip.showText(e.globalPos(), text)
					return
			QToolTip.hideText()
		except IndexError:
			print('TOOL TIP INDEX ERROR')
		
	def save(self):
		self.updateFD()
		current = self.current()
		if current is None or current.path is None:
			self.parent.saveAs()
		else:
			current.lines = self.getLines()
			current.save()
	
	
	
	def toggleBold(self):
		checked = self.boldButton.isChecked()
		settings.set_option('editor/force_bold', checked)
		QtWidgets.QMessageBox.information(self, _('Please restart'), _("This setting will be applied on next restart"))
	
	def updateFD(self):
		self.editor.fd.lines = list(self.editor.lines)
		self.editor.fd.checkSave()
		#self.editor2.current.lines = list(self.editor2.lines)
			


	def undo(self):
		self.editor.undo()
		
	def viewRevisions(self):
		self.parent.core.setMode('backupViewer', {'path':self.current().path})
		

'''
	A version that use a single instance of editor widget
'''
class EverydayEditorLight(AbstractEverydayEditor):
	def __init__(self, parent):
		AbstractEverydayEditor.__init__(self, parent)
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
		findNext = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-down'), None)
		findPrevious = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-up'), None)
		#scrollToCurrentButton.clicked.connect(self.scrollToCurrent)
		searchEntry = QtWidgets.QLineEdit()
		searchEntry.returnPressed.connect(self.search)
		self.searchEntry = searchEntry
		#searchEntry.textChanged.connect(self.filter)
		actionBox.addWidget(findNext, 0)
		actionBox.addWidget(findPrevious, 0)
		actionBox.addWidget(searchEntry, 1)
		
		layout.addLayout(actionBox, 0)
		
		actionBox = QtWidgets.QHBoxLayout()
		scrollToCurrentButton = QtWidgets.QPushButton(QtGui.QIcon.fromTheme('go-jump'), None)
		replaceAll = QtWidgets.QPushButton(_("Replace &All"), self.replaceAll)
		#scrollToCurrentButton.clicked.connect(self.scrollToCurrent)
		replaceEntry = QtWidgets.QLineEdit()
		replaceEntry.returnPressed.connect(self.replace)
		#searchEntry.textChanged.connect(self.filter)
		actionBox.addWidget(scrollToCurrentButton, 0)
		actionBox.addWidget(replaceEntry, 1)
		
		layout.addLayout(actionBox, 0)
		
		self.replaceEntry = replaceEntry
		self.updating = False
		
		


		
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
	

	
	
	def getEditors(self):
		return [self.editor1, self.editor2]
	
	

		
		

		

			
	def setDoubleView(self, doubleView):
		if doubleView:
			self.editor1.show()
			self.editor2.show()
			self.editor.setFocus()
		else:
			self.editor2.hide()
			self.editor = self.editor1
			self.editor.setFocus()
			
	def setCurrent(self, fd):
		self.editor.current.lines = list(self.editor.lines)
		self.updating = True
		self.editor.lines = fd.lines
		self.editor.current = fd
		self.updating = False
		self.editor.setFocus()
		
		
	def updateFD(self):
		self.editor1.current.lines = list(self.editor1.lines)
		self.editor2.current.lines = list(self.editor2.lines)

