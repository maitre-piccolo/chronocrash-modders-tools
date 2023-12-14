import os, re, time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

from common import util
from common import settings

from qutepart import EverydayPart
# from gui.main.everydayeditor import EverydayEditor

from data import FileWrapper



class BackupViewer(QtWidgets.QWidget):
	

	
	def __init__(self, parent):
		self.mainFrame = parent
		
		QtWidgets.QWidget.__init__(self)
		
		self.layout = QtWidgets.QVBoxLayout()
		
		
		splitter = QtWidgets.QSplitter(self)
		self.splitter = splitter
		
		self.layout.addWidget(self.splitter, 1) 
		
		
		w3 = QtWidgets.QWidget()
		l3 = QtWidgets.QHBoxLayout()
		w3.setLayout(l3)
		
		button = QtWidgets.QPushButton(_('Return to main view'))
		button.clicked.connect(self.returnToMainView)
		
		l3.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Delete selected'))
		button.clicked.connect(self.deleteSelected)
		l3.addWidget(button)
		
		button = QtWidgets.QPushButton(_('Delete all'))
		button.clicked.connect(self.deleteAll)
		l3.addWidget(button)
		
		
		
		
		self.backupListWidget = BackupList(self)
		
		
		self.editor = EverydayPart()
		
		w = QtWidgets.QWidget()
		l = QtWidgets.QVBoxLayout()
		w.setLayout(l)
		
		
		w2 = QtWidgets.QWidget()
		l2 = QtWidgets.QHBoxLayout()
		w2.setLayout(l2)
		
		self.filterInput = QtWidgets.QLineEdit()
		self.filterInput.setPlaceholderText(_('Search (press F2 to focus)'))
		self.filterInput.textChanged.connect(self.filter)
		
		l2.addWidget(QtWidgets.QLabel(_('Filter') + ' :'), 0)
		l2.addWidget(self.filterInput, 1)
		
		l.addWidget(w3)
		l.addWidget(w2)
		l.addWidget(self.backupListWidget, 1)
		
		
		splitter.addWidget(w)
		splitter.addWidget(self.editor)
		
		
		
		self.setLayout(self.layout)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F2", "Edit|Search")), self, self.focusForSearch)
		
	
	def deleteSelected(self):
		if(QtWidgets.QMessageBox.question(self, _('Delete SELECTED revisions'), _('Are you sure you want to delete selected revisions ?'), defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
			
			
			indexes = self.backupListWidget.selectedIndexes()
			
			IDS = []
			
			for i in indexes:
				try:
					i = self.backupListWidget.filterModel.mapToSource(i)
				except:
					pass
				# print(self.backupListWidget.getTrackAt(i)['path'])
				IDS.append(self.backupListWidget.getTrackAt(i)['ID'])
			
			if(len(IDS) > 0):
				self.mainFrame.DB.deleteRevisions(IDS)
				self.reload({'path':self.filterInput.text()})
		
		
	def deleteAll(self):
		text = QtWidgets.QInputDialog.getText(self, _("Delete ALL revisions"), _("Type DELETE to confirm"))[0]
		
		if(text.lower() == 'delete'):
			self.mainFrame.DB.deleteAllRevisions()
			self.reload({'path':self.filterInput.text()})
	
	def focusForSearch(self):
		self.enterEvent(None)
		if not self.filterInput.hasFocus():
			
			self.filterInput.setFocus()
			self.filterInput.selectAll()
	
	
	def filter(self, text):
		'''
			Hides visibleQueue tracks that does not match text
		'''
		if(text == ''):
			self.backupListWidget.filterModel = None
			self.backupListWidget.setModel(self.backupListWidget.model)
		else:
			filterModel = QtCore.QSortFilterProxyModel()
			filterModel.setSourceModel(self.backupListWidget.model)
			self.backupListWidget.filterModel = filterModel
			filterModel.setFilterRegExp(QtCore.QRegExp(text, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.FixedString))
			filterModel.setFilterKeyColumn(-1)
			self.backupListWidget.setModel(filterModel)
		
	def reload(self, params={}):
		revisions = self.mainFrame.DB.getAllRevisions()
		
		self.backupListWidget.loadRevisions(revisions)
		
		if('path' in params):
			self.filterInput.setText(params['path'])
			
		
	def returnToMainView(self):
		self.mainFrame.setMode("mainEditor")
		
		
		
class BackupList(QtWidgets.QTableView):
	
	def __init__(self, parent):
		self.parent = parent
		QtWidgets.QTableView.__init__(self)
		
		self.setAlternatingRowColors(True)
		
		
		self.model = BackupListModel()
		
		#self.filterModel.sort = self.model.sort
		self.setModel(self.model)
		
		header = self.horizontalHeader()
		header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
		header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
		
		#self.model.append([{'path':'test', 'birth_date':'20222', 'unsaved':1}])
		
		self.activated.connect(self.onActivated)
	
	
	def getTrackAt(self, i):
		if type(i).__name__ == 'int':
			try:
				return self.model.tracks[i]
			except IndexError:
				return None
		else:
			return self.model.tracks[i.row()]
	
	def onActivated(self, i):
		try:
			i = self.filterModel.mapToSource(i)
		except:
			pass
		elt = self.getTrackAt(i)
		# f = FileWrapper(elt['path'])
		# self.parent.editor.lines = f.getLines()
		print('ID is', elt['ID'])
		content = self.parent.mainFrame.DB.getRevisionContent(elt['ID'])
		if(content != None):
			lines = content.split('\n')
		else:
			lines = []
		self.parent.editor.lines = lines
		pass
	
	def loadRevisions(self, revisions):
		self.model.reset()
		self.model.append(revisions)
		
	
		
		
class BackupListModel(QtCore.QAbstractTableModel):
	def __init__(self, parent=None, *args):
		QtCore.QAbstractTableModel.__init__(self, parent, *args)
		self.tracks = []
		
		self.types = {1:'Sequential', 2:'Day', 3:'Hour'}
	
	def append(self, data, duringInit=False):
		self.insert(data, len(self.tracks), duringInit)
		
	def insert(self, data, pos, duringInit=False):
		# print("BEGIN INSERT ROWS", data, pos, len(data)-1)
		if type(data).__name__=='list' or type(data) is tuple:
			
			
			if(duringInit): self.beginInsertRows(QtCore.QModelIndex(), pos, pos-1) # THIS should be incorrect but prevent bugs
			else: self.beginInsertRows(QtCore.QModelIndex(), pos, pos + len(data)-1) # THIS should always be correct but creates bugs for some reason (view extend for no reason, and it creates freezes)
			
			# print("pos == len", pos == len(self.tracks))
			if(pos == len(self.tracks)):
				self.tracks.extend(data)
			else:
				for track in data:
					self.tracks.insert(pos, track)
			self.endInsertRows()
		else:
			self.beginInsertRows(QtCore.QModelIndex(), pos, pos +1)
			self.tracks.insert(data, pos)
			self.endInsertRows()
			
		# self.endInsertRows()
		#self.dataChanged.emit(QtCore.QModelIndex(), QtCore.QModelIndex())
		
		
	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole and orientation == Qt.Horizontal:
			# print('header', section, orientation)
			if section == 0:
				return _('Path')
			elif section == 1:
				return _('Edit date')
			elif section == 2:
				return _('Unsaved')
			elif section == 3:
				return _('Type')
		
		
	def rowCount(self, parent):
		return len(self.tracks)

	def columnCount(self, parent):
		return 4
		return len(self.tracks[0])
		
	def reset(self):
		self.beginResetModel()
		self.tracks = []
		self.endResetModel()
			
	def data(self, index, role):
		if not index.isValid():
			return None
		track = self.tracks[index.row()]
		if role == Qt.DisplayRole:
			if index.column() == 0:
				return self.tracks[index.row()]['path']
			elif index.column() == 1:
				return self.tracks[index.row()]['birth_date']
			elif index.column() == 2:
				return self.tracks[index.row()]['unsaved'] == 1
			elif index.column() == 3:
				return self.types[ self.tracks[index.row()]['Type_ID'] ]
	
