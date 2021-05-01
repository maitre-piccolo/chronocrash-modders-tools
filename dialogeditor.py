import os, re
from PyQt5 import QtCore, QtGui, QtWidgets

from common import settings
from gui.portrait import PortraitViewer

STRING_MAX_LENGTH = 75

class TextEditor(QtWidgets.QPlainTextEdit):
	doubleClick = QtCore.pyqtSignal(object)
	click = QtCore.pyqtSignal(object)
	
	def __init__(self, parent, role, size):
		QtWidgets.QPlainTextEdit.__init__(self)
		self.parent = parent
		self.role = role
		self.size = size
		
		self.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
		self.cursorPositionChanged.connect(self.positionChanged)
		
		self.verticalScrollBar().valueChanged.connect(self.scrollChanged)
		
	def appendText(self, text, newLine=True):
		if(newLine):
			text += '\n'
		if(self.toPlainText() == ''):
			self.moveCursor(QtGui.QTextCursor.Start)
			self.insertPlainText(text)
			self.moveCursor(QtGui.QTextCursor.End)
		else:
			self.moveCursor(QtGui.QTextCursor.End)
			self.insertPlainText(text)
			self.moveCursor(QtGui.QTextCursor.End)
			
	def getCurrentLineText(self):
		return self.textCursor().block().text()
		
	def keyPressEvent(self, event):
		if event.key() == QtCore.Qt.Key_Backtab or event.key() == QtCore.Qt.Key_Tab:
			QtWidgets.QWidget.keyPressEvent(self, event)
		else:
			if(event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter):
				cursor = self.textCursor()
				if(self.role == 'name' and cursor.atBlockStart()):
					self.parent.createNewLine(cursor.blockNumber(), False, cursor.atEnd())
					return
				elif(self.role == 'dialog2' and cursor.atBlockEnd()):
					self.parent.createNewLine(cursor.blockNumber(), True, cursor.atEnd())
					return
				else:
					self.parent.createNewLine(cursor.blockNumber(), True, cursor.atEnd())
					return
				# TODO la meme mais pour effacer les lignes (upa)
			if(event.key() == QtCore.Qt.Key_Backspace or len(self.textCursor().block().text()) < STRING_MAX_LENGTH):
				QtWidgets.QPlainTextEdit.keyPressEvent(self, event)
			
	def focusInEvent(self, event):
		QtWidgets.QPlainTextEdit.focusInEvent(self, event)
		
		cursor = self.textCursor()
		
		# Change line when tabbing from dialog
		if event.reason() is QtCore.Qt.TabFocusReason and self.parent.checkFocusSender('last'):
			newBlock = self.parent.focusSender.textCursor().blockNumber() + 1
			self.appendPlainText('')
			cursor.setPosition(self.document().findBlockByLineNumber(newBlock).position())
			#cursor.select(QtWidgets.QTextCursor.LineUnderCursor)
			
		#cursor.movePosition(QtWidgets.QTextCursor.NextBlock)
		#cursor.movePosition(QtWidgets.QTextCursor.End)
		self.setTextCursor(cursor)
		
	def focusOutEvent(self, event):
		QtWidgets.QPlainTextEdit.focusOutEvent(self, event)
		self.parent.focusSender = self
		
	def highlightCurrentLine(self):

		extraSelections = []

		if (not self.isReadOnly()):
			selection = QtWidgets.QTextEdit.ExtraSelection()

			lineColor = QtGui.QColor(QtCore.Qt.yellow).lighter(160)

			selection.format.setBackground(lineColor)
			selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
			selection.cursor = self.textCursor()
			selection.cursor.clearSelection()
			extraSelections.append(selection)

		self.setExtraSelections(extraSelections)
		
	def mouseDoubleClickEvent(self, event):
		QtWidgets.QPlainTextEdit.mouseDoubleClickEvent(self, event)
		self.doubleClick.emit(event)
		
	def mousePressEvent(self, event):
		QtWidgets.QPlainTextEdit.mousePressEvent(self, event)
		self.click.emit(event)
		
	def positionChanged(self):
		self.highlightCurrentLine()
		self.parent.highlightCurrentLine(self)
		
	def scrollChanged(self, position):
		self.parent.scrollTo(position, self)
		
	def sizeHint(self):
		return self.size
		
		
     
class LineNumberArea(QtWidgets.QWidget):
	def __init__(self, editor):
		QtWidgets.QWidget.__init__(self, editor)
		self.editor = editor
		
	def sizeHint(self):
		return QtCore.QSize(self.editor.lineNumberAreaWidth(), 0)
	
	def paintEvent(self, event):
		self.editor.lineNumberAreaPaintEvent(event)
		
		

class DialogEditor(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		
		dialogFormat = settings.get_option('dialog/format', 0)
		if dialogFormat == 0: # Volcanic & CRxTRDude format
			fields = ('name', 'side', 'dialog1', 'dialog2', 'portrait')
		elif dialogFormat == 1: # Piccolo format
			fields = ('name', 'portrait', 'side', 'dialog1', 'dialog2')
		self.fields = fields
		
		mainLayout = QtWidgets.QVBoxLayout()
		upperWidget = QtWidgets.QWidget()
		layout = QtWidgets.QHBoxLayout()
		upperWidget.setLayout(layout)
		self.setLayout(mainLayout)
		mainLayout.addWidget(upperWidget, 1)
		
		self.editors = {}
		self.labels = {'name':('Name', 'or Command'), 'portrait':('Portrait', 'or Expression'), 'side':('Side 0/1', 'or Param'), 'dialog1':('', 'First dialog line'), 'dialog2':('', 'Additional dialog line')}
		self.sizeHints = {'name':(160, 300, 0), 'portrait':(100, 300, 0), 'side':(10, 300, 0), 'dialog1':(200, 300, 1), 'dialog2':(200, 300, 1)}
		

		
		
		for field in fields:
			width, height, stretch = self.sizeHints[field]
			if(field == 'name'):
				editor = CodeEditor(self, field, QtCore.QSize(width, height))
				self.lineNumberArea = editor.lineNumberArea
			else:
				editor = TextEditor(self, field, QtCore.QSize(width, height))
			
			w = QtWidgets.QWidget()
			l1, l2 = self.labels[field]
			label1 = QtWidgets.QLabel(l1)
			label2 = QtWidgets.QLabel(l2)
			l = QtWidgets.QVBoxLayout()
			l.setSpacing(0)
			l.setContentsMargins(0, 0, 0, 0)
			w.setLayout(l)
			l.addWidget(label1, 0)
			l.addWidget(label2, 0)
			l.addWidget(editor, 1)
			
			layout.addWidget(w, stretch)
			self.editors[field] = editor
			

		self.editors['portrait'].click.connect(self.filterPortraits)
		self.editors['portrait'].doubleClick.connect(self.selectPortraitDialog)
		
		self.inModification = False
		self.focusSender = None
		self.currentPath = None
		self.portraitSelectorD = None
		self.initTabOrder()
		self.editors['name'].updateLineNumberAreaWidth(0)
		self.highlightCurrentLine()
		
		
		self.portraitSelector = PortraitViewer(self)
		self.portraitSelector.doubleClick.connect(self.selectPortrait)
		mainLayout.addWidget(self.portraitSelector, 0)
		
	def clear(self):
		for key, editor in self.editors.items():
			editor.clear()
		
	def checkFocusSender(self, toCheck):
		if toCheck == 'last':
			toCheck = self.fields[-1]
		if self.editors[toCheck] is self.focusSender:
			return True
		else:
			return False
		
	def createNewLine(self, blockNumber, down=True, atEnd=True):
		print(str(atEnd))
		if(not atEnd and down):
			blockNumber += 1
		for key, editor in self.editors.items():
			if atEnd and key != 'name': # Warning
				pass
			cursor = editor.textCursor()
			pos = editor.document().findBlockByLineNumber(blockNumber).position()
			if(atEnd) : pos+=editor.document().findBlockByLineNumber(blockNumber).length()-1
			
			
			cursor.setPosition(pos)
			editor.setTextCursor(cursor)
			cursor.insertBlock()
			
			cursor.setPosition(editor.document().findBlockByLineNumber(blockNumber).position())
			
			
	def highlightCurrentLine(self, callingEditor=None):
		if(not self.inModification):
			self.inModification = True
			if callingEditor is None:
				blockNumber = 0
			else:
				blockNumber = callingEditor.textCursor().blockNumber()

			for key, editor in self.editors.items():
				if editor is not callingEditor:
					cursor = editor.textCursor()
					cursor.setPosition(editor.document().findBlockByLineNumber(blockNumber).position())
					editor.setTextCursor(cursor)
					editor.highlightCurrentLine()
			self.inModification = False
			
	def filterPortraits(self):
		name = self.editors['name'].getCurrentLineText().lower()
		self.portraitSelector.loadFiles(name)
		
	def lineNumberAreaPaintEvent(self, event):
		self.editors['name'].lineNumberAreaPaintEvent(event)
		
	def lineNumberAreaWidth(self):
		digits = 1
		vmax = max(1, self.editors['name'].blockCount())
		while (vmax >= 10):
			vmax /= 10;
			digits += 1

		#space = 3 + self.fontMetrics().width(QtCore.QLatin1Char('9')) * digits
		space = 3 + self.fontMetrics().width('9') * digits

		return space
	
	def loadFile(self, path):
		self.clear()
		self.currentPath = path
		f = open(path, 'rU')
		lines = f.readlines()
		f.close()
		
		self.inModification = True
		for line in lines:
			line = line.replace('\n', '')
			line = line.replace('\r', '')
			line = line.replace('  ', ' ')
			line = line.replace('	', ' ')

			data = line.split(' ')

			i = 0
			for field in self.fields:
				try:
					string = data[i]
					if(string[0] != '_'):
						string = string.replace('_', ' ')
					self.editors[field].appendText(string)
					
				except IndexError:
					print('Error while parsing file')
					self.editors[field].appendText('')
				i+=1
		self.inModification = False
		
	def openFile(self):
		path = QtWidgets.QFileDialog.getOpenFileName(self, directory=os.path.join(settings.get_option('general/data_path', ''), 'story'))
		if(path is not None):
			self.loadFile(path[0])
		
	def initTabOrder(self):
		dialogFormat = settings.get_option('dialog/format', 0)
		keys = self.fields
		for i in range(len(self.fields)-1):
			self.setTabOrder(self.editors[keys[i]], self.editors[keys[i+1]])
		self.setTabOrder(self.editors[keys[len(self.fields)-1]], self.editors[keys[0]])
		
	def resizeEvent(self, e):
		QtWidgets.QWidget.resizeEvent(self, e)

		cr = self.contentsRect()
		self.lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
		
	def save(self):
		if self.currentPath is None:
			self.saveAs()
		else:
			self.toFile()
		
	def saveAs(self):
		path = QtWidgets.QFileDialog.getSaveFileName(self, directory=os.path.join(settings.get_option('general/data_path', ''), 'story'))[0]
		if(path is not None and path != ''):
			self.toFile(path)
		
		
	def selectPortrait(self, filename):
		if(filename is not None):
			editor = self.editors['portrait']
			cursor = editor.textCursor()
			cursor.select(QtGui.QTextCursor.LineUnderCursor)
			cursor.removeSelectedText()
			editor.insertPlainText(filename)
			
	def selectPortraitDialog(self, event=None):
		if(self.portraitSelectorD is None):
			self.portraitSelectorD = PortraitSelector(self)
		dialog = self.portraitSelectorD
		filename = dialog.exec_()
		self.selectPortrait(filename)
		
	def scrollTo(self, position, callingEditor=None):
		for key, editor in self.editors.items():
			if(editor is not callingEditor):
				editor.verticalScrollBar().setValue(position)
		
	def toFile(self, path=None):
		if(path is not None):
			self.currentPath = path
		
		if(self.currentPath is None):
			return
		
		data = {}
		for key, editor in self.editors.items():
			text = editor.toPlainText()
			data[key] = text.split('\n')
			
		fullText = ''
		count = max(1, self.editors['name'].blockCount())
		for i in range(count):
			fullText += data['name'][i].replace(' ', '_')
			for field in self.fields[1:]:
				try:
					currentText = data[field][i]
					if currentText == '':
						currentText = '_'
						
					fullText += ' ' + currentText.replace(' ', '_')
				except IndexError:
					fullText += ' -'
			fullText += '\n'
		if(self.currentPath is not None):
			f = open(self.currentPath, 'w')
			f.write(fullText)
		
	def updateLineNumberArea(self, rect, dy):
		if (dy):
			self.lineNumberArea.scroll(0, dy)
		else:
			self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

		if (rect.contains(self.rect())):
			self.updateLineNumberAreaWidth(0)
			
	def updateBlocks(self, newBlockCount):
		if(not self.inModification):
			self.inModification = True
			for key, editor in self.editors.items():
				#print('new count = %i ; blockcount = %i' % (newBlockCount, editor.blockCount()))
				for i in range (newBlockCount - editor.blockCount()):
					if(editor.toPlainText() == ''):
						editor.appendPlainText('\n')
					else:
						editor.appendPlainText('')
				#print('updated count = %i ;' % (editor.blockCount()))
			#self.setContentsMargins(self.lineNumberAreaWidth(), 0, 0, 0)
			self.inModification = False


class CodeEditor(TextEditor):
	def __init__(self, parent, role, size):
		TextEditor.__init__(self, parent, role, size)

		self.lineNumberArea = LineNumberArea(self)
		
		#connect(this, SIGNAL(updateRequest(QRect,int)), this, SLOT(updateLineNumberArea(QRect,int)));
		self.updateRequest.connect(self.updateLineNumberArea)
		self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
		#connect(this, SIGNAL(blockCountChanged(int)), this, SLOT(updateLineNumberAreaWidth(int)));
		
		#connect(this, SIGNAL(cursorPositionChanged()), this, SLOT(highlightCurrentLine()));
		
		
	def lineNumberAreaPaintEvent(self, event):
		painter = QtGui.QPainter(self.lineNumberArea)
		painter.fillRect(event.rect(), QtCore.Qt.lightGray)


		block = self.firstVisibleBlock()
		blockNumber = block.blockNumber()
		top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
		bottom = top + int(self.blockBoundingRect(block).height())

		while (block.isValid() and top <= event.rect().bottom()):
			if (block.isVisible() and bottom >= event.rect().top()):
				number = str(blockNumber + 1)
				painter.setPen(QtCore.Qt.black);
				painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(), QtCore.Qt.AlignRight, number)

			block = block.next()
			top = bottom
			bottom = top + int( self.blockBoundingRect(block).height())
			blockNumber += 1


	def lineNumberAreaWidth(self):
		digits = 1
		vmax = max(1, self.blockCount())
		while (vmax >= 10):
			vmax /= 10;
			digits += 1

		#space = 3 + self.fontMetrics().width(QtCore.QLatin1Char('9')) * digits
		space = 3 + self.fontMetrics().width('9') * digits

		return space
	
	def updateLineNumberArea(self, rect, dy):
		if (dy):
			self.lineNumberArea.scroll(0, dy)
		else:
			self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

		if (rect.contains(self.rect())):
			self.updateLineNumberAreaWidth(0)
	
	def updateLineNumberAreaWidth(self, newBlockCount):
		#self.parent.updateBlocks(newBlockCount)
		self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)




