from PyQt5 import QtCore, QtGui, QtWidgets
import os
from common import settings, xdg
import PIL.Image
#from PIL import Image

class FileInput(QtWidgets.QWidget):
	
	changed = QtCore.pyqtSignal()
	
	def __init__(self, mode='openFile', default='', title=None, lookFolder=None, filters=None):
		QtWidgets.QWidget.__init__(self)
		self.textEdit = QtWidgets.QLineEdit()
		self.textEdit.setText(default)
		
		button = QtWidgets.QPushButton('...')
			
		button.clicked.connect(self.setPath)
		
		self.textEdit.textChanged.connect(self.changeOccured)
		
		l = QtWidgets.QHBoxLayout()
		self.setLayout(l)
		l.addWidget(self.textEdit, 1)
		l.addWidget(button, 0)
		
		self.mode = mode
		self.lookFolder = lookFolder
		self.title = title
		self.filters = filters
		
		l.setContentsMargins(0,0,0,0)
		
	def clear(self):
		self.textEdit.clear()
		
	def changeOccured(self, *args):
		self.changed.emit()
		
	def text(self):
		return self.textEdit.text()
	
	def setText(self, text):
		self.textEdit.setText(text)
	
	def setPath(self):
		if(self.mode == 'openFile'):
			path = QtWidgets.QFileDialog.getOpenFileName(self, _(self.title), self.lookFolder, self.tr(self.filters))[0]
		elif(self.mode == 'saveFile'):
			path = QtWidgets.QFileDialog.getSaveFileName(self, directory=self.lookFolder)[0]
		elif(self.mode == 'folder' or self.mode == 'directory'):
			path = QtWidgets.QFileDialog.getExistingDirectory(self, _(self.title), self.lookFolder)
		self.textEdit.setText(path)
	
	
'''
	Qt can't show .pcx
	This function return path if not .pcx
	Or converted path (png path) if .pcx.
'''
def getSpriteShowingPath(path):
	mainPath, extension = os.path.splitext(path)
	if extension == '.pcx':
		imagesDir = os.path.join(xdg.get_data_home(), 'images')
		mainPath = mainPath.replace('/', '')
		mainPath = mainPath.replace('\\', '')
		mainPath = mainPath.replace(':', '')
		newPath = imagesDir + os.sep + mainPath + '.png'
		
		if not os.path.isfile(newPath):
			im = PIL.Image.open(path)
			im.save(newPath)
		path = newPath
	return path
		
def loadSprite(path):
	path = getSpriteShowingPath(path)

		
	image = QtGui.QImage(path)
	#print('BITPLANE', image.bitPlaneCount())
	if(image.bitPlaneCount() < 32 or len(image.colorTable()) != 0):
		#print(image.colorTable())
		image = image.convertToFormat(QtGui.QImage.Format_Indexed8)
		#table = image.colorTable()
		#print(img.colorCount())
		#print('FIRST COLOR', table[0])
		image.setColor(0, QtGui.qRgba(255, 255, 255, 0))
		#image.setColor(1, QtGui.qRgba(255, 255, 255, 0))
		#image.setColor(len(table), QtGui.qRgba(255, 255, 255, 0))
	#image = image.createMaskFromColor(image.color(0), QtCore.Qt.MaskOutColor)
	return image
