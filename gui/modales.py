# -*- coding: utf-8 -*-
import os
from common import settings, xdg
from guilib import treemodel
from PyQt5 import QtWidgets, QtGui, QtCore

from gui.util import FileInput
from gui.settings.fontselector import FontSelector

VERSION = '0.3.5 (01/11/20)'



class LevelSettingsWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		lay = QtWidgets.QFormLayout()

		#self.basePath = QtWidgets.QLineEdit()
		#self.basePath.setText(settings.get_option('general/datapath', ''))
		self.lineWeight = QtWidgets.QSpinBox()
		self.dotSize = QtWidgets.QSpinBox()
		self.lineWeight.setValue(settings.get_option('level/line_weight', 2))
		self.dotSize.setValue(settings.get_option('level/dot_size', 10))
		
		lay.addRow(_('Wall/Hole line weight') + ' : ', self.lineWeight)
		lay.addRow(_('Wall/Hole dot size') + ' : ', self.dotSize)
		
		self.setLayout(lay)
		
	def save(self):
		settings.set_option('level/line_weight', self.lineWeight.value())
		settings.set_option('level/dot_size', self.dotSize.value())
		
		
class MiscSettingsWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		lay =  QtWidgets.QGridLayout()
		
		#self.basePath = QtWidgets.QLineEdit()
		#self.basePath.setText(settings.get_option('general/datapath', ''))
		lay.addWidget(QtWidgets.QLabel(_("ImageMagick convert bin")), 0, 0)
		imageMagickPath = settings.get_option('misc/imagemagick_path', 'convert')
		self.imageMagickPath = FileInput('saveFile', '', 'Select ImageMagick convert binary', imageMagickPath, '')
		lay.addWidget(self.imageMagickPath, 0, 1)
		
		self.setLayout(lay)
		
	def save(self):
		settings.set_option('misc/imagemagick_path', self.imageMagickPath.text())
		
		

		

class SettingsEditor(QtWidgets.QDialog):
	def __init__(self, section='general'):
		QtWidgets.QDialog.__init__(self)
		self.setWindowTitle(_('Settings editor'))
		mainLayout = QtWidgets.QVBoxLayout()
		buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)


		self.widgetLayout = QtWidgets.QHBoxLayout()
		
		# --- Sections selector
		treeView = QtWidgets.QTreeView(self)
		treeView.setMinimumWidth(200)
		treeView.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
		self.sections = treemodel.SimpleTreeModel()
		def addSection(key, text, iconPath=None, parent=None):
			node = treemodel.SimpleTreeItem(parent, key, iconPath, text)
			self.sections.append(parent, node)
			return node

		editorNode = addSection('editor', _('Editor'))
		addSection('editor', _('Fonts and colors'), None, editorNode)
		addSection('dialog', _('Dialog editor'))
		addSection('level', _('Level editor'))
		addSection('misc', _('Miscellaneous'))
		treeView.setModel(self.sections)
		treeView.clicked.connect(self.sectionActivated)
		self.widgetLayout.addWidget(treeView, 0)
		
		
		

		
		self.basePath = QtWidgets.QLineEdit()
		self.basePath.setText(settings.get_option('general/datapath', ''))
		
		addFolderButton = QtWidgets.QPushButton('...')
		def add_folder():
				folderPath = QtWidgets.QFileDialog.getExistingDirectory(self)
				self.basePath.setText(folderPath)
		addFolderButton.clicked.connect(add_folder)
		
		w = QtWidgets.QWidget()
		l = QtWidgets.QHBoxLayout()
		w.setLayout(l)
		l.addWidget(self.basePath, 1)
		l.addWidget(addFolderButton, 0)
		
		lay = QtWidgets.QFormLayout()
		lay.addRow(_('Mod data folder') + ' : ', w)
		
		# TODO define dialog files columns order
		self.dialogFormatCB = QtWidgets.QComboBox()
		self.dialogFormatCB.addItem('Volcanic / CRxTRDude')
		self.dialogFormatCB.addItem('Piccolo')
		self.dialogFormatCB.setCurrentIndex(settings.get_option('dialog/format', 0))
		
		lay.addRow(_('Dialog format') + ' : ', self.dialogFormatCB)
		
		w = QtWidgets.QWidget()
		w.setLayout(lay)
		
		self.widgets = {}
		
		self.widgets['dialog'] = w
		self.activeWidget = w
		self.widgetLayout.addWidget(w, 1)
		
		
		w = FontSelector()
		self.widgetLayout.addWidget(w, 1)
		w.hide()
		self.widgets['editor'] = w
		
		w = LevelSettingsWidget()
		self.widgetLayout.addWidget(w, 1)
		w.hide()
		self.widgets['level'] = w
		
		w = MiscSettingsWidget()
		self.widgetLayout.addWidget(w, 1)
		w.hide()
		self.widgets['misc'] = w
		
		mainLayout.addLayout(self.widgetLayout)
		mainLayout.addWidget(buttonBox)
		
		
		
		self.setLayout(mainLayout)
		
	def accept(self):
		#print('TO COMPLETE')
		#settings.set_option('general/datapath', self.basePath.text())
		settings.set_option('dialog/format', self.dialogFormatCB.currentIndex())
		
		self.widgets['editor'].save()
		self.widgets['level'].save()
		self.widgets['misc'].save()
		
		settings.MANAGER.save()
		QtWidgets.QDialog.accept(self)
		
	def loadSection(self, section):
		self.activeWidget.hide()
		self.activeWidget = self.widgets[section]
		self.activeWidget.show()
		
	def sectionActivated(self, index):
		section = index.internalPointer().key
		self.loadSection(section)
		
class AboutDialog(QtWidgets.QDialog):
	def __init__(self):
		QtWidgets.QDialog.__init__(self)
		self.setWindowTitle(_('About ChronoCrash Modders Tools'))
		mainLayout = QtWidgets.QVBoxLayout()
		
		textEdit = QtWidgets.QTextBrowser()
		text = '''<p>Version : ''' + VERSION + '''</p>
		<p>This tool is meant for editing games built with OpenBOR / ChronoCrash engines.</p>
		<p>It is inspired from OpenBOR Stats and Fighter Factory, and is developped by Piccolo (<a href="http://daimao.info">daimao.info</a>).</p>
		
		<p>Special thanks to BeasTie, DJGameFreakTheIguana, Maxman and O Ilusionista for their thorough feedbacks and suggestions.</p>
		<p><a href="http://www.chronocrash.com/">ChronoCrash website</a></p>'''
		
		#<p>Credits to the ChronoCrash community.</p>
		#\nicon\nPresentation ChronoCrash community\nLink to ChronoCrash'
		
		textEdit.setText(text)
		textEdit.setReadOnly(True)
		textEdit.setOpenExternalLinks(True)
		textEdit.setMinimumWidth(400)
		textEdit.setMinimumHeight(300)
		mainLayout.addWidget(textEdit)
		
		self.setLayout(mainLayout)
		
		
class CreateFileDialog(QtWidgets.QDialog):
	
	TYPE_FIELDS = (('file', _('File')), ('entity', _('Entity')), ('level', _('Level')), ('script', _('Script')))
	
	TYPE_FIELDMODEL = QtGui.QStandardItemModel()
	for key, label in TYPE_FIELDS:
		TYPE_FIELDMODEL.appendRow([QtGui.QStandardItem(key), QtGui.QStandardItem(label)])
		
	def __init__(self):
		QtWidgets.QDialog.__init__(self)
		self.setWindowTitle(_('Create a new file'))
		mainLayout = QtWidgets.QGridLayout()
		self.setLayout(mainLayout)
	
		
		mainLayout.addWidget(QtWidgets.QLabel(_("Category")), 0, 0)
		
		self.fileTypeCB = QtWidgets.QComboBox()
		self.fileTypeCB.setModel(self.TYPE_FIELDMODEL)
		self.fileTypeCB.setModelColumn(1)
		
		self.fileTypeCB.currentIndexChanged[int].connect(self.fileTypeChanged)
		
		mainLayout.addWidget(self.fileTypeCB, 0, 1)
		
		
		mainLayout.addWidget(QtWidgets.QLabel(_("Template")), 1, 0)
		self.templateCB = QtWidgets.QComboBox()
		self.templateModel = QtGui.QStandardItemModel()
		self.templateCB.setModel(self.templateModel)
		mainLayout.addWidget(self.templateCB, 1, 1)
		
		mainLayout.addWidget(QtWidgets.QLabel(_("Path")), 2, 0)
		lookPath = settings.get_option('general/data_path', '')
		self.filePath = FileInput('saveFile', '', 'Select a .txt level file', lookPath, 'TXT Files (*.txt)')
		mainLayout.addWidget(self.filePath, 2, 1)
		
		
		buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)
		
		mainLayout.addWidget(buttonBox)
		
	def accept(self):
		
		category = self.TYPE_FIELDS[self.fileTypeCB.currentIndex()][0]
		templateFile = self.templateCB.currentText()
		templatePath = None
		if templateFile != _('Empty'):
			templatePath = os.path.join('templates', category, templateFile)
			
		
		filePath = self.filePath.text()
		if os.path.exists(filePath):
			print('the file is there')
		elif os.access(os.path.dirname(filePath), os.W_OK):
			print('the file does not exists but write privileges are given')
			f = open(filePath, 'w')
			if templatePath != None:
				templateF = open(templatePath, 'r')
				templateContent = templateF.read()
				templateF.close()
				f.write(templateContent)
			f.close()
		else:
			print('can not write there')

		
		self.filePath = filePath
		self.category = category
		QtWidgets.QDialog.accept(self)
		
	def fileTypeChanged(self, pos):
		# Fill templateCB with files from templates folders
		category = self.TYPE_FIELDS[pos][0]
		
		self.templateModel.clear()
		self.templateModel.appendRow([QtGui.QStandardItem(_('Empty'))])
		templateFolder = os.path.join('templates', category)
		if os.path.exists(templateFolder):
			for fName in os.listdir(templateFolder):
				self.templateModel.appendRow([QtGui.QStandardItem(fName)])
		
		if pos == 1:
			self.filePath.lookFolder = os.path.join(settings.get_option('general/data_path', ''), 'chars')
		elif pos == 2:
			self.filePath.lookFolder = os.path.join(settings.get_option('general/data_path', ''), 'levels')
		elif pos == 3:
			self.filePath.lookFolder = os.path.join(settings.get_option('general/data_path', ''), 'scripts')
		else:
			self.filePath.lookFolder = settings.get_option('general/data_path', '')
		pass
		
		
