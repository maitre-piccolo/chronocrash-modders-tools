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

from gui.util import FileInput

from gui.level.items import FontObject



from gui.main.fileselector import FileSelector
     
class FontPreview(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		#layout = QtWidgets.QBoxLayout()
		layout = QtWidgets.QFormLayout()
		
		dataPath = settings.get_option('general/data_path', '')
		
		self.imageReference = FileInput(self, 'openFile', dataPath + '/sprites/font.gif', 'Select font sprite reference', dataPath)
		layout.addRow(_('Font sprite reference') + ' : ', self.imageReference)
		
		
		self.textToPreview = QtWidgets.QLineEdit()
		self.textToPreview.textChanged.connect(self.updateFontObject)
		layout.addRow(_('Text to preview') + ' : ', self.textToPreview)
		
		self.changeBackgroundColorButton = QtWidgets.QPushButton('Change background color')
		self.changeBackgroundColorButton.clicked.connect(self.changeBGColor)
		layout.addRow(self.changeBackgroundColorButton)
		
		self.updateButton = QtWidgets.QPushButton(_('Update'))
		self.updateButton.clicked.connect(self.updateFontObject)
		layout.addRow(self.updateButton)
		
		self.scene = QtWidgets.QGraphicsScene()
		
		self.graphicsView = QtWidgets.QGraphicsView()
		
		self.graphicsView.setScene(self.scene)
		
		layout.addRow(self.graphicsView)
		
		
		self.setWindowTitle('Pixel Font Preview')
		self.setLayout(layout)
		self.show()
		
	def changeBGColor(self):
		color = QtWidgets.QColorDialog.getColor().name() 
		
		print('color', color)
		
		if(color != '#000000' and color != None and color != False):
			self.graphicsView.setBackgroundBrush(QtGui.QColor(color));
		
	def updateFontObject(self):
		text = self.textToPreview.text()
		self.scene.clear()
		self.scene.addItem(FontObject(text, self.imageReference.text()))