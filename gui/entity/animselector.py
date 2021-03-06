from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from common import settings

from guilib.treemodel import TreeModel, TreeItem
from operator import attrgetter

class AnimSelector(QtWidgets.QWidget):
	def __init__(self, parent):
		self.mainEditor = parent
		QtWidgets.QWidget.__init__(self)
		
		trueLayout = QtWidgets.QHBoxLayout()
		trueLayout.setContentsMargins(0, 0, 0, 0)
		w = QtWidgets.QWidget()
		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		w.setLayout(layout)
		
		txt = _('ANIMATIONS')
		txt = '\n'.join(txt)
		label = QtWidgets.QLabel(txt)
		trueLayout.addStretch()
		trueLayout.addWidget(label)
		trueLayout.addWidget(w)
		trueLayout.addStretch()
		self.setLayout(trueLayout)
		
		self.cacheLabel = label
		self.cacheLabel.hide()
		self.content = w
		
		
		actionGroup = QtWidgets.QActionGroup(self)
		self.buttonBar = QtWidgets.QToolBar()
		addIcon = QtGui.QIcon.fromTheme('list-add')
		addAnim = self.buttonBar.addAction(addIcon, _('Add animation'), self.createAnim)
		self.buttonBar.addSeparator()
		#deleteIcon = QtGui.QIcon.fromTheme('list-remove')
		#deleteAnim = self.buttonBar.addAction(libraryIcon, 'Remove', self.deleteAnim)
		layout.addWidget(self.buttonBar, 0)
		
		
		
		self.treeView = QtWidgets.QTreeView(self)
		self.model = AnimModel()
		self.filterModel = QtCore.QSortFilterProxyModel()
		self.filterModel.setSourceModel(self.model)
		self.treeView.setSortingEnabled(True)
		self.treeView.setModel(self.filterModel)
	
		self.treeView.activated.connect(self.loadAnim)
		
		header = self.treeView.header()
		header.setStretchLastSection(False)
		#header.setDefaultSectionSize(60)
		header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode (1, QtWidgets.QHeaderView.Stretch)
		
		
		self.searchEntry = QtWidgets.QLineEdit()
		self.searchEntry.returnPressed.connect(self.search)
		
		
		layout.addWidget(self.treeView)
		layout.addWidget(self.searchEntry, 0)
		
		self.timeLine = QtCore.QTimeLine(400, self)
		self.timeLine.setUpdateInterval(20)
		
		#connect(timeLine, SIGNAL(frameChanged(int)), progressBar, SLOT(setValue(int)));
		self.timeLine.frameChanged.connect(self.tmp)
		
		
	def tmp(self, val):
		self.mainEditor.mainSplitter.setSizes([val, self.mainEditor.rect().width()])
		
		
	def append(self, dataTuple, parentNode=None):
		if(parentNode == None):
			parentNode = self.model.rootItem
		return self.model.append(parentNode, AnimItem(parentNode, dataTuple))
	
	
	def clear(self):
		self.model.reset()
		
		
	def createAnim(self):
		text = QtWidgets.QInputDialog.getText(self, _("Create animation"), _("Name"))[0]

		if text != '': # TODO make sure animation name is valid (startswith freespecial, etc OR in idle, walk, rise, etc
			self.mainEditor.addAnim(text)
			self.append((text, '' , 999))
		
	def enterEvent(self, e):
		if self.content.isVisible() and not settings.get_option('gui/auto_collapse', True) : return # Do not expand if already expanded
		self.content.show()
		self.cacheLabel.hide()
		self.timeLine.setFrameRange(self.mainEditor.mainSplitter.sizes()[0], 300);
		self.timeLine.start()
		
	def leaveEvent(self, e):
		if self.rect().contains(self.mapFromGlobal(QtGui.QCursor.pos())):
			return
		
		if not settings.get_option('gui/auto_collapse', True) : return
		self.cacheLabel.show()
		self.content.hide()
		self.timeLine.setFrameRange(self.mainEditor.mainSplitter.sizes()[0], 100);
		self.timeLine.start()
		
	def load(self, data):
		for i, d in enumerate(data):
			self.append((d['ID'], d['label'], i))
	
	def loadAnim(self, index):
		self.mainEditor.loadAnim(index.data(AnimModel.itemRole).ID)
		
		
	def search(self):
		txt = self.searchEntry.text()
		self.treeView.model().setFilterRole(Qt.DisplayRole)
		self.treeView.model().setFilterKeyColumn(1)
		#self.treeView.model().setFilterRegExp(text)
		regExp = QtCore.QRegExp(txt, QtCore.Qt.CaseInsensitive)
		self.treeView.model().setFilterRegExp(regExp)
		#self.treeView.model().setFilterRegExp('/(.*)' + txt +'(.*)/i')
		
class AnimItem(TreeItem):
	def __init__(self, parent, data):
		TreeItem.__init__(self, data[1], parent)
		self.ID = data[0]
		self.label = data[1]
		self.pos = data[2]

		self.subelements = []
		
	def __str__( self ):
		return self.label
		
	def __repr__(self):
		return self.label
		
	def getFilter(self):
		'''
			ex : {"artist":"AC/DC", "album":"Back In Black", "title":"You Shook Me All Night Long"}
		'''
		dic = {}
		item = self
		while(item.parent() != None): # Don't  eval rootItem 
			dic[item.type] = item.label
			item = item.parent()
		return dic
		
class AnimModel(TreeModel):
	
	itemRole = Qt.UserRole+2
	
	def __init__(self):
		TreeModel.__init__(self)
		self.columnsFields = ('pos', 'ID', 'label')


	def columnCount(self, parent):
		return 3

	def data(self, index, role):
		if not index.isValid():
			return None
		item = index.internalPointer()
		if role == self.itemRole:
			return item
		elif role == Qt.DisplayRole:
			if index.column() == 0:
				return None
				return item.pos
			elif index.column() == 1:
				return item.ID
			elif index.column() == 2:
				return item.label
				

		return None

	def flags(self, index):
		return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled
	
	def headerData(self, section, orientation, role):
		if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			if section == 0:
				return '#'
			elif section == 1:
				return 'ID'
			elif section == 2:
				return 'Label'
			
		return None
		
	def mimeData(self, indexes):
		'''
			What is passed during drag operations
		'''
		data = QtCore.QMimeData()
		selection = []
		for i in indexes:
			selection.append(i.internalPointer().getFilter())
		data.setData('bullseye/library.items', str(selection))
		return data
		
	def mimeTypes(self):
		'''
			FIXME Not used, didn't manage to find out how to automatically serialize items (thus overrided mimeData instead)
		'''
		return ('bullseye/library.items',)
		
	def sort(self, columnIndex, order):
		self.layoutAboutToBeChanged.emit()
		if(order == QtCore.Qt.AscendingOrder):
			reverse = False
		else:
			reverse = True
			
		def sort(elt, reverse):
			elt.childItems = sorted(elt.childItems, key=attrgetter(self.columnsFields[columnIndex]), reverse=reverse)
			for childElt in elt.childItems:
				sort(childElt, reverse)
				
		sort(self.rootItem, reverse)
		
		self.layoutChanged.emit()
