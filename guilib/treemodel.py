from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt

expandedRole = Qt.UserRole+1
itemRole = Qt.UserRole+2
expandedRoleWithoutFilter = Qt.UserRole+3
containsRole = Qt.UserRole+4
expandWithoutContainsRole = Qt.UserRole+5 # for nodes that contains a parent that contains filter, and that are expanded despite themselves not containing filter

class FilterModel(QtCore.QSortFilterProxyModel):
	
	def __init__(self):
            QtCore.QSortFilterProxyModel.__init__(self)
            self.expandResults = 0

	def filterAcceptsRow(self, sourceRow, sourceParent):
		col0 = self.sourceModel().index(sourceRow, 0, sourceParent)
		
		
		data = self.sourceModel().data(col0, Qt.DisplayRole)
		
		# item = self.sourceModel().data(col0, itemRole)
		# print(data)
		if data is None : return False
		# if data is None : return True
		# contains = self.filterRegExp().pattern() in data
		contains = self.filterRegExp().indexIn(data) != -1
		# contains = data.contains(self.filterRegExp())
		
		
		
		
		self.sourceModel().setData(col0, contains, containsRole)
		self.sourceModel().setData(col0, 0, expandWithoutContainsRole) # reset
		
		
		# do bottom to top filtering
		if (self.sourceModel().hasChildren(col0)):
			
			for i in range(self.sourceModel().rowCount(col0)):
				if (self.filterAcceptsRow(i, col0)):
                                        # WARNING the following line alter nodes state
					if(self.filterRegExp().pattern() != ''):
						# isExpanded = self.sourceModel().data(col0, expandedRole)
						# self.sourceModel().setData(col0, isExpanded, expandedRoleWithoutFilter) # saving general state (without filter)
						self.sourceModel().setData(col0, True, expandedRole)
						# pass
					else:
						# wasExpanded = self.sourceModel().data(col0, expandedRoleWithoutFilter)
						# print(self.sourceModel().data(col0, Qt.DisplayRole), wasExpanded)
						# self.sourceModel().setData(col0, wasExpanded, expandedRole)
						pass
					return True
					# pass
				#return False
		else:
			pass

		
		
		
		
		
		# if(data == "chars"): print("chars", self.sourceModel().data(col0, containsRole),  self.sourceModel().data(col0, expandWithoutContainsRole))
		
		
		
		parent_expandWithoutContains = self.sourceModel().data(sourceParent, expandWithoutContainsRole)
		if(parent_expandWithoutContains == None):parent_expandWithoutContains = 0
		
		
		# print(data)
		
		
		# if(data == "chars"): print("chars parent", self.sourceModel().data(sourceParent, containsRole),  parent_expandWithoutContains)
		
		
		
		if(contains and self.filterRegExp().pattern() != '') :
			# print(data)
			self.sourceModel().setData(col0, True, expandedRole)
			
		
		
		# and item.parentItem != None
		
		# NOTE this is a cool feature to allow to expand folder level 1 when you search for a term and it matches a folder
		elif self.expandResults > 0  and self.sourceModel().data(sourceParent, containsRole) == True:
			self.sourceModel().setData(col0, 1, expandWithoutContainsRole)
			self.sourceModel().setData(col0, True, expandedRole)
			return True # means we show it (don't filter out)
		elif parent_expandWithoutContains >= 1 and  self.expandResults > parent_expandWithoutContains:
		# elif self.sourceModel().data(sourceParent, expandWithoutContainsRole) < self.expandResults:
			print("parent_expandWithoutContains was", parent_expandWithoutContains, self.expandResults, self.sourceModel().data(col0, Qt.DisplayRole))
			self.sourceModel().setData(col0, parent_expandWithoutContains+1, expandWithoutContainsRole)
			self.sourceModel().setData(col0, True, expandedRole)
			return True
			# return False
		else:
			self.sourceModel().setData(col0, 0, expandWithoutContainsRole) # reset
			# print("parent value was", data, parent_expandWithoutContains, self.expandResults)
                #else:
                    #print(self.sourceModel().data(sourceParent, Qt.DisplayRole))
                    
		#print(contains, self.sourceModel().data(col0, Qt.DisplayRole))
		return contains
		# return True

class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.isExpanded = False
        self.isExpandedWithoutFilter = False
        self.containsFilter = False
        self.expandWithoutContains = 0
        self.childItems = []

    def append(self, item):
        self.childItems.append(item)
        return item

    def empty(self):
	    self.childItems = []
	    
    def emptyTree(self):
        for child in self.childItems:
            child.emptyTree()
        self.empty()
    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0

class TreeModel(QtCore.QAbstractItemModel):
    def __init__(self, parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(("Title", "Summary"))
        #self.setupModelData(data.split('\n'), self.rootItem)

    def append(self, parentNode, item, parentIndex=None):
	    #print(parentIndex.isValid())
	    if parentIndex is None:
		    parentIndex = QtCore.QModelIndex()
	    if(parentNode is None):
		    parentNode = self.rootItem
	    #rowCount = self.rowCount(QtCore.QModelIndex())
	    rowCount = parentNode.childCount()
	    
	    #i = QtCore.QModelIndex()
	    self.beginInsertRows(parentIndex, rowCount, rowCount)
	    #self.beginInsertRows(QtCore.QModelIndex(), rowCount, rowCount)
	    res = parentNode.append(item)
	    i = self.createIndex(parentNode.childCount(), 0)
	    #i = parentIndex.child(parentNode.childCount(), 0)
	    res.index = i 
	    
	    self.endInsertRows()
	    return res
    
    def indexOfNode(self, node):
        return self.createIndex(node.row(), 0, node.parent());
        nb = 0
        #print('PASSING')
        while node != self.rootItem:
                node = node.parent()
                nb+=1
        #print('PASSING')
        index = QtCore.QModelIndex()#self.createIndex(0, 0)
        #index = self.createIndex(0, 0)
        for i in range(nb):
                print('PASSING')
                index =index.child(0,0, node)
                node = node.child(0)
        return index
		
    
    
    def clear(self, ):
        self.rootItem = TreeItem(("Title", "Summary"))
    
    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != QtCore.Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return QtCore.Qt.NoItemFlags

        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if childItem is None : return QtCore.QModelIndex()
        parentItem = childItem.parent()

        if parentItem == self.rootItem or parentItem == None:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):

        if parent.column() > 0:
            return 0

        #print('valid', parent.isValid())
        if not parent.isValid():
            
            
            parentItem = self.rootItem
        else:
           
            parentItem = parent.internalPointer()
            #if(parentItem is not None) : print(parentItem.itemData)

            
        if(parentItem is None) : return 0

        #if parentItem.childCount() > 1 : return 1
        return parentItem.childCount()
        
    def reset(self):
        self.beginResetModel()
        #self.beginRemoveRows(QtCore.QModelIndex(), 0, 0)
        self.rootItem = TreeItem(("Title", "Summary"))
        #self.endRemoveRows()
        self.endResetModel()
        

    def setupModelData(self, lines, parent):
        parents = [parent]
        indentations = [0]

        number = 0

        while number < len(lines):
            position = 0
            while position < len(lines[number]):
                if lines[number][position] != ' ':
                    break
                position += 1

            lineData = lines[number][position:].strip()

            if lineData:
                # Read the column data from the rest of the line.
                columnData = [s for s in lineData.split('\t') if s]

                if position > indentations[-1]:
                    # The last child of the current parent is now the new
                    # parent unless the current parent has no children.

                    if parents[-1].childCount() > 0:
                        parents.append(parents[-1].child(parents[-1].childCount() - 1))
                        indentations.append(position)

                else:
                    while position < indentations[-1] and len(parents) > 0:
                        parents.pop()
                        indentations.pop()

                # Append a new item to the current parent's list of children.
                parents[-1].appendChild(TreeItem(columnData, parents[-1]))

            number += 1
            
            
            
            
            
            
class SimpleTreeItem(TreeItem):
	def __init__(self, parent, key, icon, label):
		TreeItem.__init__(self, label, parent)
		self.key = key
		self.label = label
		self.iconPath = icon
		self.icon = None
		self.subelements = []
		
	def __str__( self ):
		return self.label
		
	def __repr__(self):
		return self.label



class SimpleTreeModel(TreeModel):
	def __init__(self):
		TreeModel.__init__(self)


	def columnCount(self, parent):
		return 1

	def data(self, index, role):
		if not index.isValid():
			return None
		item = index.internalPointer()
		if role == Qt.DisplayRole:
			if index.column() == 0:
				return item.label
		elif role == Qt.DecorationRole and index.column() == 0:
			if(item.icon is None):
				try:
					path = item.iconPath
					item.icon = QtGui.QPixmap(path)
					#item.icon = item.icon.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation) #scaledToHeight(icon_size)
						
				except:
					item.icon = None
			
			return item.icon
		return None

	#def flags(self, index):
		#return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled
	
	#def headerData(self, section, orientation, role):
		#if orientation == Qt.Horizontal and role == Qt.DisplayRole:
			#if section == 0:
				#return 'Icon'
			#elif section == 1:
				#return 'Label'
			#elif section == 2:
				#return _('Count')
			
		#return None
