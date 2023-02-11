from PyQt5 import QtWidgets, QtGui, QtCore

from common import settings

class FontSelector(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		
		db = QtGui.QFontDatabase()
		families = db.families()

		layout = QtWidgets.QVBoxLayout()
		self.setLayout(layout)
		
		listLayout = QtWidgets.QHBoxLayout()
		layout.addLayout(listLayout)
		
		fontW = QtWidgets.QListWidget()
		fontW.addItems(families)
		fontW.currentTextChanged.connect(self.changeFamily)
		self.fontW = fontW
		
		
		sizeW = QtWidgets.QListWidget()
		fontSizes = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,22,24,26,28,32, 48, 64, 72, 80, 96, 128]
		sizeW.addItems(map(str, fontSizes))
		sizeW.currentTextChanged.connect(self.changeSize)
		self.sizeW = sizeW
		
		listLayout.addWidget(fontW)
		listLayout.addWidget(sizeW)
		
		textEdit = QtWidgets.QPlainTextEdit()
		textEdit.setPlainText('José Long est un mage.')
		self.textEdit = textEdit

		layout.addWidget(textEdit)
		
		
		# Load settings
		currentFamily = settings.get_option('editor/font_family', 'Courier')
		if currentFamily in families:
			self.fontW.setCurrentRow(families.index(currentFamily))
			
		self.sizeW.setCurrentRow(fontSizes.index(settings.get_option('editor/font_size', 12)))
		
	def changeFamily(self, family):
		f = self.textEdit.font()
		f.setFamily(family)
		self.textEdit.setFont(f)
		
	def changeSize(self, size):
		f = self.textEdit.font()
		f.setPointSize(int(size))
		self.textEdit.setFont(f)
		
	def save(self):
		settings.set_option('editor/font_family', self.fontW.currentItem().text())
		settings.set_option('editor/font_size', int(self.sizeW.currentItem().text()))
