from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from common import settings

from guilib.treemodel import TreeModel, TreeItem
from operator import attrgetter

import re

from data import ParsedLine



class MultiFilterMode:
    AND = 0
    OR = 1


class MultiFilterProxyModel(QtCore.QSortFilterProxyModel):    
    def __init__(self, *args, **kwargs):
        QtCore.QSortFilterProxyModel.__init__(self, *args, **kwargs)
        self.filters = {}
        self.multi_filter_mode = MultiFilterMode.AND

    def setFilterByColumn(self, column, regex):
        if isinstance(regex, str):
            regex = re.compile(regex, re.IGNORECASE)
        self.filters[column] = regex
        self.invalidateFilter()

    def clearFilter(self, column):
        del self.filters[column]
        self.invalidateFilter()

    def clearFilters(self):
        self.filters = {}
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filters:
            return True

        results = []
        for key, regex in self.filters.items():
            text = ''
            index = self.sourceModel().index(source_row, key, source_parent)
            if index.isValid():
                text = self.sourceModel().data(index, Qt.DisplayRole)
                if text is None:
                    text = ''
            # results.append(regex.match(text))
            results.append(regex.search(text))

        if self.multi_filter_mode == MultiFilterMode.OR:
            return any(results)
        return all(results)


class AnimSelector(QtWidgets.QWidget):
	def __init__(self, parent, options=['noRefresh']):
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
		trueLayout.addWidget(w, 1)
		trueLayout.addStretch()
		self.setLayout(trueLayout)
		
		self.cacheLabel = label
		self.cacheLabel.hide()
		self.content = w
		
		
		actionGroup = QtWidgets.QActionGroup(self)
		self.buttonBar = QtWidgets.QToolBar()
		addIcon = QtGui.QIcon.fromTheme('list-add')
		addAnim = self.buttonBar.addAction(addIcon, _('Add animation'), self.createAnim)
		
		#removeIcon = QtGui.QIcon.fromTheme('edit-delete')
		removeIcon = QtGui.QIcon.fromTheme('list-remove')
		addAnim = self.buttonBar.addAction(removeIcon, _('Delete animation'), self.deleteAnim)
		self.buttonBar.addSeparator()
		#deleteIcon = QtGui.QIcon.fromTheme('list-remove')
		#deleteAnim = self.buttonBar.addAction(libraryIcon, 'Remove', self.deleteAnim)
		
		if not'hideUpperBar' in options:
			layout.addWidget(self.buttonBar, 0)
		
		
		
		self.treeView = QtWidgets.QTreeView(self)
		self.model = AnimModel()
		self.filterModel = MultiFilterProxyModel()
		self.filterModel.setSourceModel(self.model)
		self.treeView.setSortingEnabled(True)
		self.treeView.setModel(self.filterModel)
	
		self.treeView.activated.connect(self.loadAnim)
		
		header = self.treeView.header()
		header.setStretchLastSection(False)
		#header.setDefaultSectionSize(60)
		header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
		header.setSectionResizeMode (1, QtWidgets.QHeaderView.Stretch)
		header.setSectionResizeMode (2, QtWidgets.QHeaderView.Stretch)
		
		
		theme = settings.get_option('gui/widgets_theme', None)
		
		#searchButton = QtWidgets.QToolButton()
		searchButton = QtWidgets.QPushButton()
		searchIcon = QtGui.QImage('icons/search.svg')
		if(theme == "Dark"): searchIcon.invertPixels()
		searchIcon = QtGui.QIcon(QtGui.QPixmap.fromImage(searchIcon))
		searchButton.setIcon(searchIcon)
		#searchButton.setIcon(QtGui.QIcon.fromTheme('search'))
		searchButton.clicked.connect(self.search)
		
		hboxSearch = QtWidgets.QHBoxLayout()
		w = QtWidgets.QWidget()
		w.setLayout(hboxSearch)
		self.searchEntry = QtWidgets.QLineEdit()
		self.searchEntry.setPlaceholderText(_('Search (press F3 to focus)'))
		self.searchEntry.returnPressed.connect(self.search)
		
		if settings.get_option('misc/search_on_text_change', False):
			self.searchEntry.textChanged.connect(self.search)
		
		
		hboxSearch.addWidget(self.searchEntry, 1)
		hboxSearch.addWidget(searchButton)
		
		if not'noRefresh' in options:
			reloadIcon = QtGui.QImage('icons/reload.svg')
			if(theme == "Dark"): reloadIcon.invertPixels()
			reloadIcon = QtGui.QIcon(QtGui.QPixmap.fromImage(reloadIcon))
			
			refreshButton = QtWidgets.QPushButton()
			refreshButton.setIcon(reloadIcon)
			refreshButton.clicked.connect(self.refresh)
			
			
			hboxSearch.addWidget(refreshButton)
		
		
		layout.addWidget(w, 0)
		layout.addWidget(self.treeView)
		
		
		self.timeLine = QtCore.QTimeLine(400, self)
		self.timeLine.setUpdateInterval(20)
		
		#connect(timeLine, SIGNAL(frameChanged(int)), progressBar, SLOT(setValue(int)));
		self.timeLine.frameChanged.connect(self.tmp)
		
		QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("F3", "Edit|Search Anim")), self, self.focusForSearch)
		
		
		
		
		
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
			self.append((text, '' , 999, text))
			
	def deleteAnim(self):
		if(self.currentAnimID == "idle"):
			return
		if(self.currentAnimName == None):
				QtWidgets.QMessageBox.warning(self, _('Load an animation first'), _('Load an animation before deleting it'))
				return
		
		if(QtWidgets.QMessageBox.question(self, _('Delete animation'), _('Are you sure you want to delete animation' + ' ' + self.currentAnimName + ' ?'), defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
			self.currentAnimName = "idle";
			self.mainEditor.deleteAnim(self.currentAnimID)
			self.mainEditor.loadAnim("idle")
		
		
	def enterEvent(self, e):
		if(not hasattr(self.mainEditor, 'mainSplitter')):return
		
		if self.content.isVisible() and not settings.get_option('gui/auto_collapse', True) : return # Do not expand if already expanded
		self.content.show()
		self.cacheLabel.hide()
		self.timeLine.setFrameRange(self.mainEditor.mainSplitter.sizes()[0], 300);
		self.timeLine.start()
		
		
	def focusForSearch(self):
		print('focus for search - Anim')
		self.enterEvent(None)
		
		self.searchEntry.setFocus()
		self.searchEntry.selectAll()
		
	def leaveEvent(self, e):
		if(not hasattr(self.mainEditor, 'mainSplitter')):return
		if self.rect().contains(self.mapFromGlobal(QtGui.QCursor.pos())):
			return
		
		if not settings.get_option('gui/auto_collapse', True) : return
		self.cacheLabel.show()
		self.content.hide()
		self.timeLine.setFrameRange(self.mainEditor.mainSplitter.sizes()[0], 100);
		self.timeLine.start()
		
	def load(self, data):
		self.currentAnimName = None
		for i, d in enumerate(data):
			ID_edited = d['ID']
			if 'ID_edited' in d:
				ID_edited = d['ID_edited']
			self.append((d['ID'], d['label'], i, ID_edited))
		
		
	def refresh(self):
		self.loadFrom()
			
	def loadFrom(self, lines=None):
		
		if lines == None:
			lines = self.mainEditor.editor.lines
		
		self.updating = True
		self.currentAnim = None
		
		sectionLines = []
		data = {'ID':'header', 'label':'', 'lines':sectionLines}
		dicData = {'header':data}
		fullData = [data]
		
		
		#ent_cache = Cache('entities_data', EntityEditorWidget.ROOT_PATH)
		
		name = None
		
		for line in lines:
			pLine = ParsedLine(line)
			part = pLine.next()
			if part != None : part = part.lower()
			if part == 'anim':
				label = pLine.getCom()
				#print(pLine.parts, pLine.pos)
				animID = pLine.next()
				sectionLines = []
				data = {'ID':animID, 'label':label, 'lines': sectionLines}
				fullData.append(data)
				dicData[animID] = data
			#elif part == 'name':
				#name = pLine.next().lower()
				#if(model is None): model = name
			#elif part == 'type':
				#type = pLine.next().lower()
				#if model is not None:
					#try:
						##ent_cache.data[model]['type'] = type
						##ent_cache.save()
						#pass
					#except:
						#print("no model named ", model)
			#elif part == 'icon':
				#icon = pLine.next()
				#if model is not None:
					#try:
						#ent_cache.data[model]['icon'] = icon
						#ent_cache.save()
					#except:
						#print("no model named ", model)
			sectionLines.append(line)
			
		self.dicData = dicData
		self.fullData = fullData
		#print(fullData)
		for key in dicData:
			print(key)
			
		self.clear()
		self.load(fullData)

		
		
	
	def loadAnim(self, index):
		self.currentAnimID = index.data(AnimModel.itemRole).ID
		self.currentAnimName = self.currentAnimID
		
		# ???
		#if(self.currentAnimID.lower() == 'idle'):
			#return
		
		label = index.data(AnimModel.itemRole).label
		if(label != ''): self.currentAnimName += '(' + label + ')'
		
		self.mainEditor.loadAnim(index.data(AnimModel.itemRole).ID)
		
		
	def search(self):
		txt = self.searchEntry.text()
		
		# QT original filter function
		# self.treeView.model().setFilterRole(Qt.DisplayRole)
		# self.treeView.model().setFilterKeyColumn(1)
		
		#self.treeView.model().setFilterRegExp(text)
		# regExp = QtCore.QRegExp(txt, QtCore.Qt.CaseInsensitive)
		# self.treeView.model().setFilterRegExp(regExp)
		
		# custom model filter function
		self.treeView.model().multi_filter_mode = MultiFilterMode.OR
		self.treeView.model().setFilterByColumn(1, txt)
		self.treeView.model().setFilterByColumn(2, txt)
		
		#self.treeView.model().setFilterRegExp('/(.*)' + txt +'(.*)/i')
		
class AnimItem(TreeItem):
	def __init__(self, parent, data):
		TreeItem.__init__(self, data[1], parent)
		self.ID = data[0]
		self.label = data[1]
		self.pos = data[2]
		self.ID_edited = data[3]

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
				if(hasattr(item, 'ID_edited')):
				   return item.ID_edited
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
