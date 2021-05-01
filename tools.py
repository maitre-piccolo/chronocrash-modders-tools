from PyQt5 import QtCore, QtGui, QtWidgets

import os
import re
import shutil
from common import settings
from gui.pak import PakWidget
from gui.mugen import MugenWidget
from gui.volnorm import VolNormWidget
from gui.commandgen import CommandListGenerator
     
class ToolWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QHBoxLayout()
		
		self.actionPanel = QtWidgets.QWidget()
		actionsLayout = QtWidgets.QVBoxLayout()
		actionsLayout.setSpacing(0)
		actionsLayout.setContentsMargins(0, 0, 0, 0)
		button = QtWidgets.QPushButton(_('Shift offsets'))
		button.clicked.connect(lambda: self.loadSection('shift_offsets'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Scale offsets'))
		button.clicked.connect(lambda: self.loadSection('scale_offsets'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Generate command list'))
		button.clicked.connect(lambda: self.loadSection('gen_command_list'))
		actionsLayout.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Prepare PAK'))
		button.clicked.connect(lambda: self.loadSection('prepare_pak'))
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
			elif section == 'scale_offsets':
				newWidget = ScaleWidget()
			elif(section == 'prepare_pak'):
				newWidget = PakWidget()
			elif(section == 'gen_command_list'):
				newWidget = CommandListGenerator()
			elif(section == 'mugen'):
				newWidget = MugenWidget()
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



		
