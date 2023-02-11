# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

import os
from common import settings, xdg
from gui.util import loadSprite

class PortraitSelectorD(QtWidgets.QDialog):
	
	def __init__(self, parent, name='Portrait selector'):
		QtWidgets.QDialog.__init__(self)
		layout = QtWidgets.QVBoxLayout()
		self.iconViewer = PortraitViewer(self)
		self.iconViewer.doubleClick.connect(self.accept)
		layout.addWidget(self.iconViewer)
		self.setLayout(layout)
	def accept(self, elt=None):
		path = elt.file
		self.value = path
		
		QtWidgets.QDialog.accept(self)
		
	def exec_(self):
		if QtWidgets.QDialog.exec_(self) and QtWidgets.QDialogButtonBox.Ok:
			return self.value
		else:
			return None
		
class PortraitSelectorW(QtWidgets.QWidget):
	
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QVBoxLayout()
		self.iconViewer = PortraitViewer(self)
		layout.addWidget(self.iconViewer)
		self.setLayout(layout)

		
		

class IconViewer(QtWidgets.QListView):
	
	currentChange = QtCore.pyqtSignal(object)
	middleClick = QtCore.pyqtSignal(object)
	
	def __init__(self, parent, viewMode='icons'):
		QtWidgets.QListView.__init__(self, parent)
		
		#self.setUniformItemSizes(True)
		self.parent = parent
		self.model = ThumbnailModel()
		

		self.setAcceptDrops(True)
		self.setDropIndicatorShown(True)
		
		self.viewMode = ''
		self.setMode(viewMode)
		#self.setMovement(QtWidgets.QListView.Free)
		self.setMovement(QtWidgets.QListView.Snap)
		
		self.setModel(self.model)

		

		self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		

		#self.setDragEnabled(True)
		#self.setViewMode(QtWidgets.QListView.ListMode)
		
		#self.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
		#self.setDragDropOverwriteMode(False)
		#self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
		
		
		self.setSpacing(10)
		self.setStyleSheet('QListView::item::selected::active {border-radius:5px; background-color: palette(highlight)}')
		#self.setStyleSheet('QListView::icon { border-radius:10px; background-color:orange;}');
		#self.setMinimumHeight(170)
		self.setMaximumHeight(100)

		self.setWrapping(False)
		
		
	def currentChanged(self, current, previous):
		QtWidgets.QListView.currentChanged(self, current, previous)
		self.currentChange.emit(current)

	def clear(self):
		self.model.items = []
		
	def dragEnterEvent(self, e):
		data = e.mimeData()
		if data.hasUrls():
			e.accept()
		else:
			QtWidgets.QListView.dragEnterEvent(self, e)
			
	def dragMoveEvent(self, e):
		QtWidgets.QListView.dragMoveEvent(self, e)
		e.accept()
		#e.acceptProposedAction()
		# Must reimplement this otherwise the drag event is not spread
		# But at this point the event has already been checked by dragEnterEvent

	def getItemAt(self, index):
		return self.model.items[index.row()]

	def contextMenuEvent(self, event):
		from qt.gui.menus import  SpecialEltMenu
		elt = self.getEltAt(self.indexAt(event.pos()).row())
		menu = SpecialEltMenu(elt, self.mapToGlobal(event.pos()))
		
	def dropEvent(self, e):
		#print('DROP EVENT')
		data = e.mimeData()
		#print data.formats()
		
		
		if(data.hasFormat('portraits')):
			indexes = self.selectedIndexes()

			movedTracks = []
			if len(indexes) > 0:
				dropTarget = self.indexAt(QtCore.QPoint(e.pos().x(), e.pos().y()))

				first = indexes[0]
				last = indexes[-1]
				
				self.model.items[first.row()]
				r = first.row()
				
				#row = -1
				for index in indexes:
					movedTracks.append(self.model.items.pop(r))
				#self.model.items.insert(dropTarget.row(), movedTracks)
				
				selection = self.selectionModel()
				selection.clear()
				if(dropTarget.row() != -1):
					self.model.items[dropTarget.row():0] = movedTracks
				
					for i in range(len(movedTracks)):	
						selection.select(self.model.index(dropTarget.row()+i), QtWidgets.QItemSelectionModel.Select)
				else:
					self.model.items.extend(movedTracks)
					end = len(self.model.items)
					for i in range(end - len(movedTracks), end):
						print(i)
						selection.select(self.model.index(i), QtWidgets.QItemSelectionModel.Select)
					#if(index.row() != row):
						#track = self.getTrackAt(index)
						#if(targetedTrack == track):
							#return
						#movedTracks.append(track)
						#self.model.removeTrack(track)
						#row = index.row()
				
				#if (first.row() > targetedRow) and targetedRow != -1: # Move up
					#self.model.insertBefore(movedTracks, targetedTrack)
				#else: # Move down
					#self.model.insertAfter(movedTracks, targetedTrack)
				
				## Set selection on the right position
				#if targetedRow != -1:
					#self.selectRow(targetedRow)
				#else:
					#self.selectRow(len(self.model.tracks)-1)
			
			QtWidgets.QListView.dropEvent(self, e)
			self.setMovement(QtWidgets.QListView.Snap)
			
		elif data.hasUrls():
			paths = []
			tracks = []
			for url in data.urls():
		
				paths.append(url.toLocalFile())

			for path in sorted(paths):
				track = Portrait.fromPath(path)
				
				if track is not None:
					tracks.append(track)
			row = self.indexAt(QtCore.QPoint(e.pos().x(), e.pos().y())).row()
			if(row == -1):
				row = 0
			self.model.insert(tracks, row)

		
	def getEltAt(self, i):
		return self.model.items[i]
	
	def mousePressEvent(self, event):
		if(event.button() == QtCore.Qt.RightButton or event.button() == QtCore.Qt.MiddleButton):
			self.middleClick.emit(self.indexAt(QtCore.QPoint(event.pos().x(), event.pos().y())))
		QtWidgets.QListView.mousePressEvent(self, event)
	
	def setMode(self, mode):
		if(mode != self.viewMode):
			self.viewMode = mode
			if(mode == 'icons'):
				self.model.icon_size = 128
				self.model.max_length = 20
				#self.setIconSize(QtCore.QSize())
				self.setViewMode(QtWidgets.QListView.IconMode)
				self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
				#self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
				self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
				self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
				#self.setSelectionRectVisible(True)
				#self.setBatchSize(3)
				#self.setLayoutMode(QtWidgets.QListView.Batched)
			else:
				self.model.icon_size = 48
				self.model.max_length = 120
				#self.setIconSize(QtCore.QSize(48, 48))
				self.setViewMode(QtWidgets.QListView.ListMode)
				self.setDragEnabled(True)
				self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		
	def wheelEvent(self, e):
		if(self.viewMode == 'icons'):
			if e.angleDelta().y() > 0:
				self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition() - self.horizontalScrollBar().singleStep())
			else:
				self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition() + self.horizontalScrollBar().singleStep())
		else:
			QtWidgets.QListView.wheelEvent(self, e)
			

					
	def sizeHint(self):
		return QtCore.QSize(800, 200)


class PortraitViewer(IconViewer):
	doubleClick = QtCore.pyqtSignal(object)
	
	def __init__(self, parent, filter=None, viewMode='icons'):
		IconViewer.__init__(self, parent, viewMode)

		
		#if(filter is not None):
		self.loadFiles(filter)
		self.activated.connect(self.onActivated)

		
	def loadFiles(self, filter):
		self.clear()
		dataPath = settings.get_option('general/data_path', '')
		dialogFormat = settings.get_option('dialog/format', 0)
		if(dialogFormat == 0):
			folder = os.path.join(dataPath, 'story' + os.sep + 'portrait')
		elif(dialogFormat == 1):
			folder = os.path.join(dataPath, 'story' + os.sep + 'pro')
			
			
		if not os.path.exists(folder) : return
			
		for f in sorted(os.listdir(folder)):
			if f[0] != '.':
				if os.path.isfile(os.path.join(folder, f)):
					(shortname, extension) = os.path.splitext(f)
					extension = extension.lower()
					if(filter is not None and filter in f):
					#checkFileInterest(folder, f, extension.lower())
						self.model.append(Portrait(folder, f))
				#else:
					#if(dig):
						#scanFolder(folder + os.sep + f, dig, files)
		
	def contextMenuEvent(self, event):
		from qt.gui.menus import  SpecialEltMenu
		elt = self.getEltAt(self.indexAt(event.pos()).row())
		menu = SpecialEltMenu(elt, self.mapToGlobal(event.pos()))
		
	
		
	def onActivated(self, index):
		self.doubleClick.emit(self.getEltAt(index.row()).file)
		
	def getEltAt(self, i):
		return self.model.items[i]
	
	def setMode(self, mode):
		if(mode != self.viewMode):
			self.viewMode = mode
			if(mode == 'icons'):
				self.model.icon_size = 128
				self.model.max_length = 20
				#self.setIconSize(QtCore.QSize())
				self.setViewMode(QtWidgets.QListView.IconMode)
				self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
				#self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
				self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
				self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
				#self.setSelectionRectVisible(True)
				#self.setBatchSize(3)
				#self.setLayoutMode(QtWidgets.QListView.Batched)
			else:
				self.model.icon_size = 48
				self.model.max_length = 120
				#self.setIconSize(QtCore.QSize(48, 48))
				self.setViewMode(QtWidgets.QListView.ListMode)
				self.setDragEnabled(True)
				self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
		
	def wheelEvent(self, e):
		if(self.viewMode == 'icons'):
			if e.delta() > 0:
				self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition() - self.horizontalScrollBar().singleStep())
			else:
				self.horizontalScrollBar().setSliderPosition(self.horizontalScrollBar().sliderPosition() + self.horizontalScrollBar().singleStep())
		else:
			QtWidgets.QListView.wheelEvent(self, e)
			

					
	def sizeHint(self):
		return QtCore.QSize(800, 200)					
	

class Portrait():
	
	count = 0
	def __init__(self, folder, f):
		self.ID = self.count
		self.count += 1
		self.module = 'portrait'
		self.folder = folder
		self.file = f
		self.thumbnail_path = os.path.join(folder, f)
		self.path = self.thumbnail_path
		self.icon = None
		self.loadingIconFailed = False
		
	@staticmethod
	def fromPath(path):
		return Portrait(os.path.dirname(path), os.path.basename(path))
		
class ThumbnailModel(QtCore.QAbstractListModel):
	def __init__(self):
		QtCore.QAbstractListModel.__init__(self)
		self.items = []
		self.icon_size = 48
		self.max_length = 20
		self.max_length = 120
	
	def append(self, elt):
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount()+1)
		self.items.append(elt)
		self.endInsertRows()
		
	def insert(self, data, pos):
		if type(data).__name__=='list':
			self.beginInsertRows(QtCore.QModelIndex(), pos, pos + len(data)-1)
			if(pos == len(self.items)):
				self.items.extend(data)
			else:
				for item in data:
					self.items.insert(pos, item)
		else:
			self.beginInsertRows(QtCore.QModelIndex(), pos, pos +1)
			self.items.insert(data, pos)
			
		self.endInsertRows()
		
		
	def data(self, index, role):
		item = self.items[index.row()]
		if not index.isValid():
			return None
		elif role == QtCore.Qt.DisplayRole:
			if item.module != 'picture':
				return item.file[:self.max_length] + (item.file[self.max_length:] and '..')
			else:
				return None
		elif role == QtCore.Qt.DecorationRole:
			try:
				if(not item.loadingIconFailed and item.icon is None):
					#item.icon = QtGui.QPixmap(item.thumbnail_path)
					item.icon = QtGui.QPixmap.fromImage(loadSprite(item.thumbnail_path))
					
			except OSError:
				item.icon = None
				item.loadingIconFailed = True
			except:
				#item.icon = QtGui.QPixmap(item.thumbnail_path)
				item.icon = QtGui.QPixmap.fromImage(loadSprite(item.thumbnail_path))
				
			if item.icon is None or item.icon.isNull():
				item.icon = QtGui.QPixmap(xdg.get_data_dir() + os.sep + 'icons' + os.sep + item.module + '.png')
			
			#item.icon = item.icon.scaled(self.icon_size, self.icon_size, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
			
			item.icon = item.icon.scaledToHeight(72, QtCore.Qt.SmoothTransformation)
			return item.icon
	
	def flags(self, index):
		if (index.isValid()):
			return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
		else:
			return QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDropEnabled
		
	def lastIndex(self):
		return self.index(len(self.items)-1, 0)

	def mimeData(self, indexes):
		'''
			What is passed during drag operations
		'''
		data = QtCore.QMimeData()
		selection = []
		for i in indexes:
			selection.append(self.items[i.row()].ID)
		data.setData('portraits', str(selection))
		return data
		
	def mimeTypes(self):
		return ('portraits',)
		
	def supportedDropActions(self):
		return QtCore.Qt.CopyAction | QtCore.Qt.MoveAction
	
	def reset(self):
		self.beginResetModel()
		self.items = []
		self.endResetModel()
		
	def rowCount(self, parent=None):
		return len(self.items)
