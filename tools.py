from PyQt5 import QtCore, QtGui, QtWidgets

import os, logging
import re
import shutil
from common import settings
from gui.pak import PakWidget
from gui.orphans import OrphanWidget
from gui.mugen import MugenWidget
from gui.volnorm import VolNormWidget
from gui.commandgen import CommandListGenerator
from data import ParsedLine, FileWrapper


from gui.main.fileselector import FileSelector
     
class ToolWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QHBoxLayout()
		
		self.actionPanel = QtWidgets.QWidget()
		actionsLayout = QtWidgets.QVBoxLayout()
		actionsLayout.setSpacing(0)
		actionsLayout.setContentsMargins(0, 0, 0, 0)
		
		button = QtWidgets.QPushButton(_('Check paths'))
		button.clicked.connect(lambda: self.loadSection('check_paths'))
		#button.clicked.connect(self.checkPaths)
		actionsLayout.addWidget(button)
		
		
		
		
		
		button = QtWidgets.QPushButton(_('Shift offsets'))
		button.clicked.connect(lambda: self.loadSection('shift_offsets'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Scale offsets'))
		button.clicked.connect(lambda: self.loadSection('scale_offsets'))
		actionsLayout.addWidget(button)
		
		
		button = QtWidgets.QPushButton(_('Prepare PAK'))
		button.clicked.connect(lambda: self.loadSection('prepare_pak'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Orphans finder'))
		button.clicked.connect(lambda: self.loadSection('orphans'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Generate command list'))
		button.clicked.connect(lambda: self.loadSection('gen_command_list'))
		actionsLayout.addWidget(button)
		
		
		
		button = QtWidgets.QPushButton(_('Normalize sounds volume'))
		button.clicked.connect(lambda: self.loadSection('norm_sounds'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Convert Mugen character'))
		button.clicked.connect(lambda: self.loadSection('mugen'))
		actionsLayout.addWidget(button)
		
		actionsLayout.addSpacerItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

		self.actionPanel.setLayout(actionsLayout)
		
		
		
		
		layout.addWidget(self.actionPanel, 0)
		
		self.setLayout(layout)
		
		self.widgets = {}
		
	def loadSection(self, section):
		if(section not in self.widgets):
			if(section == 'shift_offsets'):
				newWidget = ShiftWidget()
			if(section == 'check_paths'):
				newWidget = CheckPathsWidget()
				
				
		
			elif section == 'scale_offsets':
				newWidget = ScaleWidget()
			elif(section == 'prepare_pak'):
				newWidget = PakWidget(self)
			elif(section == 'orphans'):
				newWidget = OrphanWidget(self)
			elif(section == 'gen_command_list'):
				newWidget = CommandListGenerator()
			elif(section == 'mugen'):
				newWidget = MugenWidget(self)
			elif(section == 'norm_sounds'):
				newWidget = VolNormWidget()
			self.widgets[section] = newWidget
			self.layout().addWidget(newWidget, 1)
		
		try:
			self.currentWidget.hide()
		except:
			pass
		self.currentWidget = self.widgets[section]

		self.currentWidget.show()
		
		
	
							   
		
class ShiftWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QFormLayout()
		

		self.x = QtWidgets.QLineEdit(str(settings.get_option('shift_tool/x', 0)), self)
		self.y = QtWidgets.QLineEdit(str(settings.get_option('shift_tool/y', 0)), self)
		
		self.x.setValidator(QtGui.QIntValidator(-999, 999, self))
		self.y.setValidator(QtGui.QIntValidator(-999, 999, self))
		
		layout.addRow(_('X shifting') + ' : ', self.x)
		layout.addRow(_('Y shifting') + ' : ', self.y)
		
		self.modelPath = QtWidgets.QLineEdit()
		dataPath = settings.get_option('general/datapath', '')
		self.modelPath.setText(settings.get_option('shift_tool/file', dataPath))
		
		button = QtWidgets.QPushButton('...')
		def setPath():
			path = QtWidgets.QFileDialog.getOpenFileName(self, _('Open Entity File'), os.path.join(settings.get_option('general/datapath', ''), 'chars'), self.tr("Entity Files (*.txt);;All files (*.*)"))[0]
			self.modelPath.setText(path)
		button.clicked.connect(setPath)
		
		w = QtWidgets.QWidget()
		l = QtWidgets.QHBoxLayout()
		w.setLayout(l)
		l.addWidget(self.modelPath, 1)
		l.addWidget(button, 0)
		
		layout.addRow(_('Model file') + ' : ', w)
		
		button = QtWidgets.QPushButton(_('Process file'))
		button.clicked.connect(self.processFile)
		layout.addRow(button)
		
		
		self.editor = QtWidgets.QPlainTextEdit()
		button = QtWidgets.QPushButton(_('Process inline text'))
		button.clicked.connect(self.processText)
		layout.addRow(self.editor)
		layout.addRow(button)
		

		
		self.setLayout(layout)
		
	def getXY(self):
		x = int(self.x.text())
		y = int(self.y.text())
		settings.set_option('shift_tool/x', x)
		settings.set_option('shift_tool/y', y)
		
		return x, y
		
	def processText(self):
		text = self.editor.toPlainText()
		data = text.split('\n')
		
		newText = self.processData(data)
		
		self.editor.clear()
		self.editor.appendPlainText(newText)
		
	def processFile(self):
		path = self.modelPath.text()
		if os.path.isfile(path):
			(start, extension) = os.path.splitext(path)
			shutil.copyfile(path, start + '_back' + extension)
			
			settings.set_option('shift_tool/file', path)
			
			f = open(path, 'rwU')
			data = f.readlines()
			
			newText = self.processData(data, True)

			f = open(start + '_new' + extension, 'w')
			f.write(newText)
			f.close()
			print('SAVED')
		
		
	def processData(self, data, lineBreakTrick=False):
		x, y = self.getXY()
		
		p = re.compile('^([ \s]*)offset(.*)')
		i = 0
		
		newText = ''
		for line in data:
			c = 0
			i += 1
			if p.match(line) != None:
				print('ok')
				#parts = line.split(' ')
				parts = re.split(' |	', line)
				prefix = ''
				while(parts[c] == ' ' or parts[c] == ''):
					prefix += parts[c]
					c+= 1
				line = '	' + parts[c] + ' ' + str(int(parts[c+1]) + x) + ' ' + str(int(parts[c+2]) + y)
			elif lineBreakTrick and i != len(data):
				line = line[:-1]
			newText += line + '\n'
			
		return newText
		
	
		
		
class ScaleWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QFormLayout()
		

		self.x = QtWidgets.QLineEdit(str(settings.get_option('scale_tool/x', 0)), self)
		self.y = QtWidgets.QLineEdit(str(settings.get_option('scale_tool/y', 0)), self)
		
		self.x.setValidator(QtGui.QDoubleValidator(self))
		self.y.setValidator(QtGui.QDoubleValidator(self))
		
		layout.addRow(_('X scaling factor') + ' : ', self.x)
		layout.addRow(_('Y scaling factor') + ' : ', self.y)
		
		self.modelPath = QtWidgets.QLineEdit()
		dataPath = settings.get_option('general/datapath', '')
		self.modelPath.setText(settings.get_option('scale_tool/file', dataPath))
		
		button = QtWidgets.QPushButton('...')
		def setPath():
			path = QtWidgets.QFileDialog.getOpenFileName(self, _('Open Entity File'), os.path.join(settings.get_option('general/datapath', ''), 'chars'), self.tr("Entity Files (*.txt);;All files (*.*)"))[0]
			self.modelPath.setText(path)
		button.clicked.connect(setPath)
		
		w = QtWidgets.QWidget()
		l = QtWidgets.QHBoxLayout()
		w.setLayout(l)
		l.addWidget(self.modelPath, 1)
		l.addWidget(button, 0)
		
		layout.addRow(_('Model file') + ' : ', w)
		
		button = QtWidgets.QPushButton(_('Process file'))
		button.clicked.connect(self.processFile)
		layout.addRow(button)
		
		
		self.editor = QtWidgets.QPlainTextEdit()
		button = QtWidgets.QPushButton(_('Process inline text'))
		button.clicked.connect(self.processText)
		layout.addRow(self.editor)
		layout.addRow(button)
		
		self.setLayout(layout)
		
	def processText(self):
		text = self.editor.toPlainText()
		data = text.split('\n')
		
		newText = self.processData(data)
		
		self.editor.clear()
		self.editor.appendPlainText(newText)
		
	def processFile(self):
		path = self.modelPath.text()
		if os.path.isfile(path):
			(start, extension) = os.path.splitext(path)
			shutil.copyfile(path, start + '_back' + extension)
			
			settings.set_option('scale_tool/file', path)
			
			f = open(path, 'rwU')
			data = f.readlines()
			
			newText = self.processData(data, True)

			f = open(start + '_new' + extension, 'w')
			f.write(newText)
			f.close()
			print('SAVED')
		
		
	def processData(self, data, lineBreakTrick=False):
		scaleX = float(self.x.text())
		scaleY = float(self.y.text())
		settings.set_option('scale_tool/x', scaleX)
		settings.set_option('scale_tool/y', scaleY)
		
		
		p = re.compile('^([ \s]*)offset(.*)')
		i = 0
		
		newText = ''
		for line in data:
			line = re.sub('\s+', ' ', line)
			c = 0
			i += 1
			if p.match(line) != None:
				parts = line.split(' ')
				#print parts
				if parts[0] == ' ' or parts[0] == '':
					c+= 1
				line = parts[c] + ' ' + str(int(round(int(parts[c+1])*scaleX))) + ' ' + str(int(round(int(parts[c+2])*scaleY)))
			elif lineBreakTrick and i != len(data):
				line = line[:-1]
			newText += line + '\n'

		
		return newText


class CheckPathsWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QFormLayout()
		
		button = QtWidgets.QPushButton(_('Check without details'))
		button.clicked.connect(self.checkWithoutDetails)
		layout.addRow(button)
		
		button = QtWidgets.QPushButton(_('Check with details'))
		button.clicked.connect(self.checkWithDetails)
		layout.addRow(button)
		
		self.logWidget = QtWidgets.QPlainTextEdit('Log...')
		layout.addRow(self.logWidget)
		
		self.setLayout(layout)
			
			
	def checkWithoutDetails(self):
		paths_not_exist = self.checkPaths(False)
		text = 'These files do not exist:\n\n' + '\n\n'.join(paths_not_exist)

		
		self.logWidget.setPlainText(text)
		
		
	def checkWithDetails(self):
		paths_not_exist = self.checkPaths(True)
		text = 'These files do not exist:\n\n' + '\n\n'.join(paths_not_exist)

		
		self.logWidget.setPlainText(text)
		
		
	def checkPaths(self, details=False):
		#dataPath = settings.get_option('general/datapath', '')
		ROOT_PATH = FileSelector.ROOT_PATH
		
		txt_files = []
		found_paths = []
		found_paths_output = {}
		
		
		# *** MODELS ***
		path = os.path.join(ROOT_PATH, 'data', 'models.txt')
		print(path)
		if not os.path.isfile(path):
			print('WARNING : no models.txt')
			return
			
		f = FileWrapper(path)
		lines = f.getLines()
		
		
		
		
		
		for i, line in enumerate(lines):
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None : continue
			if part.lower() == 'know' or part.lower() == 'load':
				if(pLine.getNumberOfParts() < 3) :
					logging.debug('Incomplete line : ' + pLine.line)
					
					
				else:
					name = pLine.next().lower()
					#Entity.AVAILABLE_MODELS.append(name)
					path = pLine.next()
					
					fullPath = os.path.join(ROOT_PATH, path)
					if not os.path.exists(fullPath) : continue
					
					
					txt_files.append(fullPath)
					
					
		# *** LEVELS ***
		path = os.path.join(ROOT_PATH, 'data', 'levels.txt')
		print(path)
		if not os.path.isfile(path):
			print('WARNING : no levels.txt')
			return
			
		f = FileWrapper(path)
		lines = f.getLines()
		
		
		
		
		
		for i, line in enumerate(lines):
			pLine = ParsedLine(line)
			part = pLine.next()
			if part is None : continue
			if part.lower() == 'file':
				if(pLine.getNumberOfParts() < 2) :
					logging.debug('Incomplete line : ' + pLine.line)
					
					
				else:
					#name = pLine.next().lower()
					#Entity.AVAILABLE_MODELS.append(name)
					path = pLine.next()
					
					fullPath = os.path.join(ROOT_PATH, path)
					if not os.path.exists(fullPath) : continue
					
					
					txt_files.append(fullPath)
					
					
					
		for fullPath in txt_files:
			# print(fullPath)
			f = FileWrapper(fullPath)
			lines2 = f.getLines()
			
			for i, line2 in enumerate(lines2):
				pLine2 = ParsedLine(line2)
				while(pLine2.next() != None):
					rPath = pLine2.current()
					if(pLine2.current().lower().startswith('data/') and ( details or (pLine2.current() not in found_paths))):
						found_paths.append(pLine2.current())
						if (details is True):
							pass
							found_paths_output[rPath] = pLine2.current() + '	IN : ' + fullPath + '	AT LINE : ' + str(i+1) + '	(FULL LINE : ' + line2 + ')'
							#found_paths_full.append({'path':pLine2.current(), 'output':pLine2.current() + '	IN : ' + fullPath + '	AT LINE : ' + str(i+1) + '	(FULL LINE : ' + line2 + ')'} )
						else:
							found_paths_output[rPath] = rPath
							pass
							#found_paths_full.append({'path':pLine2.current(), 'output':pLine2.current()})
							#found_paths_full.append({'path':pLine2.current(), 'output':pLine2.current()})
						
								
								
								
		#print(found_paths)
		paths_not_exist = []
		for path in found_paths:
			
			output = found_paths_output[path]
			fullPath = os.path.join(ROOT_PATH, path)
			if(not os.path.isfile(fullPath)) : 
				paths_not_exist.append(output)
		#print(paths_not_exist)
		return paths_not_exist
