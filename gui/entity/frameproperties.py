import os, re, time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from data import AttackBox, BBox

class FramePropertiesEditor(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.setMaximumSize(300,2000)
		self.parent = parent
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)
		
		offsetGB = QtWidgets.QGroupBox(_('Off set'))
		layout = QtWidgets.QGridLayout()
		offsetGB.setLayout(layout)
		
		
		self.widgets = {}
		
		xOff = QtWidgets.QSpinBox()
		yOff = QtWidgets.QSpinBox()
		delay = QtWidgets.QSpinBox()
		
		self.widgets['delay'] = delay
		self.widgets['offset'] = {'x':xOff, 'y':yOff}
		
		layout.addWidget(QLabel(_("X")), 0, 0)
		layout.addWidget(xOff, 1, 0)
		layout.addWidget(QLabel(_("Y")), 0, 1)
		layout.addWidget(yOff, 1, 1)
		layout.addWidget(QLabel(_("Delay")), 2, 0)
		layout.addWidget(delay, 3, 0)
		
		self.layout.addWidget(offsetGB, 0)
		
		
		#self.bboxGB = QtWidgets.QGroupBox(_('Body Box'))
		self.bboxGB = CustomGroupBox(_('Body Box'))
		self.bboxGB.addClicked.connect(self.addBox)
		self.bboxGB.deleteClicked.connect(self.deleteBox)
		layout = QtWidgets.QGridLayout()
		self.bboxGB.setLayout(layout)
		
		xB = QtWidgets.QSpinBox()
		yB = QtWidgets.QSpinBox()
		wB = QtWidgets.QSpinBox()
		hB = QtWidgets.QSpinBox()
		self.widgets['bbox'] = {'x':xB, 'y':yB, 'w':wB, 'h':hB}

		
		layout.addWidget(QLabel(_("X")), 0, 0)
		layout.addWidget(QLabel(_("Y")), 0, 1)
		layout.addWidget(xB, 1, 0)
		layout.addWidget(yB, 1, 1)
		
		layout.addWidget(QLabel(_("Width")), 2, 0)
		layout.addWidget(QLabel(_("Height")), 2, 1)
		layout.addWidget(wB, 3, 0)
		layout.addWidget(hB, 3, 1)
		
		self.layout.addWidget(self.bboxGB, 0)
		
		
		# ******     ATTACK BOX       ********
		self.attackGB = CustomGroupBox(_('Attack Box'))
		layout = QtWidgets.QGridLayout()
		
		self.attackGB.setLayout(layout)
		self.attackGB.addClicked.connect(self.addBox)
		self.attackGB.deleteClicked.connect(self.deleteBox)
		
		x = QtWidgets.QSpinBox()
		y = QtWidgets.QSpinBox()
		w = QtWidgets.QSpinBox()
		h = QtWidgets.QSpinBox()
		d = QtWidgets.QSpinBox()
		k = QtWidgets.QSpinBox()
		p = QtWidgets.QSpinBox()
		depth = QtWidgets.QSpinBox()
		depth2 = QtWidgets.QSpinBox()
		self.widgets['attack'] = {'x':x, 'y':y, 'w':w, 'h':h, 'd':d, 'power':k, 'pause':p, 'depth':depth, 'depth2':depth2}

		
		layout.addWidget(QLabel(_("X")), 0, 0)
		layout.addWidget(x, 1, 0)
		layout.addWidget(QLabel(_("Y")), 0, 1)
		layout.addWidget(y, 1, 1)
		
		layout.addWidget(QLabel(_("Width")), 2, 0)
		layout.addWidget(w, 3, 0)
		layout.addWidget(QLabel(_("Height")), 2, 1)
		layout.addWidget(h, 3, 1)
		
		layout.addWidget(QLabel(_("Damage")), 4, 0)
		layout.addWidget(d, 5, 0)
		layout.addWidget(QLabel(_("Knockdown")), 4, 1)
		layout.addWidget(k, 5, 1)
		
		layout.addWidget(QLabel(_("Pause")), 6, 0)
		layout.addWidget(p, 7, 0)
		layout.addWidget(QLabel(_("Depth")), 6, 1)
		layout.addWidget(depth, 7, 1)
		
		
		self.unblockable = QtWidgets.QCheckBox(_('Unblockable'))
		self.noflash = QtWidgets.QCheckBox(_('No flash'))
		layout.addWidget(self.unblockable, 8, 0)
		layout.addWidget(self.noflash, 8, 1)
		
		self.layout.addWidget(self.attackGB, 0)
		
		
		# ******     RANGE BOX       ********
		self.rangeGB = CustomGroupBox(_('Range'))
		layout = QtWidgets.QGridLayout()
		
		self.rangeGB.setLayout(layout)
		self.rangeGB.addClicked.connect(self.addBox)
		self.rangeGB.deleteClicked.connect(self.deleteBox)
		
		xMin = QtWidgets.QSpinBox()
		xMax = QtWidgets.QSpinBox()
		
		self.widgets['range'] = {'xMin':xMin, 'xMax':xMax}
		
		layout.addWidget(QLabel(_("X min")), 0, 0)
		layout.addWidget(xMin, 1, 0)
		layout.addWidget(QLabel(_("X max")), 0, 1)
		layout.addWidget(xMax, 1, 1)
		
		self.layout.addWidget(self.rangeGB, 0)
		
		
		
		#self.layout.addWidget(ButtonGroupBox(), 0)
		
		self.layout.addStretch(1)
		
		
		self.loading = False
		
		for w in list([delay] + list(self.widgets['offset'].values()) + list(self.widgets['bbox'].values()) + list(self.widgets['range'].values()) + list(self.widgets['attack'].values())):
			w.setRange(-1000,1000)
			w.valueChanged.connect(self.valueChanged)
		
		self.unblockable.stateChanged.connect(self.valueChanged)
		self.noflash.stateChanged.connect(self.valueChanged)
		
		self.bboxGB.setDisabled(True)
		self.attackGB.setDisabled(True)
		
		
	def addBox(self):
		if len(self.parent.anim) == 0 : return
		if self.sender() == self.attackGB:
			data = self.parent.frames[self.parent.currentFrame]
			data['attack'] = AttackBox()
		elif self.sender() == self.bboxGB:
			data = self.parent.frames[self.parent.currentFrame]
			data['bbox'] = BBox()
			
		self.parent.rebuildText()
		self.parent.frameEditor.loadFrame()
		
	def deleteBox(self):
		if len(self.parent.anim) == 0 : return
		if self.sender() == self.attackGB:
			data = self.parent.frames[self.parent.currentFrame]
			data['attack'].delete = True
		elif self.sender() == self.bboxGB:
			data = self.parent.frames[self.parent.currentFrame]
			data['bbox'].delete = True
			
		self.parent.rebuildText()
		self.parent.frameEditor.loadFrame()
		
		
	def loadData(self, data):
		self.loading = True
		delay = 0
		if 'delay' in data:
			delay = data['delay']
		self.widgets['delay'].setValue(delay)
		
		
		x, y = 0, 0
		if 'offset' in data:
			x, y = data['offset']

		self.widgets['offset']['x'].setValue(x)
		self.widgets['offset']['y'].setValue(y)
		
		
		if 'bbox' in data:
			self.bboxGB.setDisabled(False)
			x, y, w, h = data['bbox'].getParams()[0:4]
			self.widgets['bbox']['x'].setValue(x)
			self.widgets['bbox']['y'].setValue(y)
			self.widgets['bbox']['w'].setValue(w)
			self.widgets['bbox']['h'].setValue(h)
		else:
			self.bboxGB.setDisabled(True)
			
			
		if 'attack' in data:
			self.attackGB.setDisabled(False)
			abox = data['attack']

			aType, x, y, w, h, d, pow, block, noflash, pausetime, z1 =  abox.getParams()[0:11]
			self.widgets['attack']['x'].setValue(x)
			self.widgets['attack']['y'].setValue(y)
			self.widgets['attack']['w'].setValue(w)
			self.widgets['attack']['h'].setValue(h)
			
			self.widgets['attack']['d'].setValue(d)
			self.widgets['attack']['power'].setValue(pow)
			self.widgets['attack']['pause'].setValue(pausetime)
			self.widgets['attack']['depth'].setValue(z1)
			#self.widgets['attack']['depth2'].setValue(z2)
			
			
			self.unblockable.setChecked(bool(block))
			self.noflash.setChecked(bool(noflash))
		else:
			self.attackGB.setDisabled(True)
			
			
		if 'range' in data:
			self.rangeGB.setDisabled(False)
			xMin, xMax = data['range']
			self.widgets['range']['xMin'].setValue(xMin)
			self.widgets['range']['xMax'].setValue(xMax)
		else:
			self.rangeGB.setDisabled(True)
			
			
			
		self.loading = False
		
		
		
	
	'''
		Fill the data argument with the form values
	
	'''
	def updateData(self, data=None):
		
		def updateNotEmpty(box, key, value):
			if value == 0 and box.data[key] == None:
				return
			
			box.data[key] = value
			
		print('DATA UPDATE')
		if data is None:
			data = self.parent.frames[self.parent.currentFrame]
			
		delay = self.widgets['delay'].value()
		if delay != 0:
			data['delay'] = delay
			
		x = self.widgets['offset']['x'].value()
		y = self.widgets['offset']['y'].value()
		if 'offset' in data:
			data['offset'] = [x, y]
			
		if 'bbox' in data:
			bbox = data['bbox']
			x, y, w, h = bbox.getParams()[0:4]
			x = self.widgets['bbox']['x'].value()
			y = self.widgets['bbox']['y'].value()
			w = self.widgets['bbox']['w'].value()
			h = self.widgets['bbox']['h'].value()
			bbox.x = x
			bbox.y = y
			bbox.width = w
			bbox.height = h
			
		if 'attack' in data:
			abox = data['attack']
			aType, x, y, w, h = abox.getParams()[0:5]
			x = self.widgets['attack']['x'].value()
			y = self.widgets['attack']['y'].value()
			w = self.widgets['attack']['w'].value()
			h = self.widgets['attack']['h'].value()
			d = self.widgets['attack']['d'].value()
			p = self.widgets['attack']['power'].value()
			pause = self.widgets['attack']['pause'].value()
			depth = self.widgets['attack']['depth'].value()
			depth2 = self.widgets['attack']['depth2'].value()
			unblockable = int(self.unblockable.isChecked())
			noflash = int(self.noflash.isChecked())
			
			#abox.damageType = aType
			updateNotEmpty(abox, 'position.x', x)
			updateNotEmpty(abox, 'position.y', y)
			updateNotEmpty(abox, 'size.x', w)
			updateNotEmpty(abox, 'size.y', h)
			
			updateNotEmpty(abox, 'damage.force', d)
			updateNotEmpty(abox, 'reaction.fall.force', p)
			
			updateNotEmpty(abox, 'block.penetrate', unblockable)
			updateNotEmpty(abox, 'reaction.pause.time', pause)
			
			updateNotEmpty(abox, 'effect.hit.flash.disable', noflash)
			updateNotEmpty(abox, 'size.z.1', depth)
			
		
			
		if 'range' in data:
			xMin, xMax = data['range']
			xMin = self.widgets['range']['xMin'].value()
			xMax = self.widgets['range']['xMax'].value()
			data['range'] = [xMin, xMax]


	def valueChanged(self, *args):
		if not self.loading:
			self.updateData()
			self.parent.rebuildText()
			self.parent.frameEditor.loadFrame()
		
class ButtonGroupBox(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(ButtonGroupBox, self).__init__(parent=parent)

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0,24,0,0)
        self.groupBox = QtWidgets.QGroupBox(self)
        self.button = QtWidgets.QPushButton("FOO", parent=self)
        self.layout.addWidget(self.groupBox)

        self.button.move(0, -4)
        
class CustomGroupBox(QtWidgets.QGroupBox):
	
	deleteClicked = QtCore.pyqtSignal()
	addClicked = QtCore.pyqtSignal()
	
	
	def __init__(self, label):
		QtWidgets.QGroupBox.__init__(self, label)
		self.disabled = False
	
	
	def setDisabled(self, disabled):
		for i in range(self.layout().count()):
			widget = self.layout().itemAt(i).widget()
			widget.setEnabled(not disabled)
		self.disabled = disabled
				
	def mouseReleaseEvent(self, e):
		xClick = e.pos().x()
		yClick = e.pos().y()
		
		x = self.width()-32
		y = 2
		print(xClick, yClick, x, y)
		if x <= xClick <= x+16 and y <= yClick <= yClick + 16:
			if self.disabled:
				self.setDisabled(False)
				self.addClicked.emit()
			else:
				self.setDisabled(True)
				self.deleteClicked.emit()
		self.update()
		QtWidgets.QGroupBox.mouseReleaseEvent(self, e)

	def paintEvent(self, e):
		
		QtWidgets.QGroupBox.paintEvent(self, e)
		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.Antialiasing);
		
		if self.disabled:
			painter.setPen(QtCore.Qt.darkGreen);
			x = self.width()-32
			y = 2
			painter.drawRect(x, y, 16, 16);
			painter.drawText(x+3, y+12, '+')
		else:
			painter.setPen(QtCore.Qt.darkRed);
			x = self.width()-32
			y = 2
			painter.drawRect(x, y, 16, 16);
			painter.drawText(x+3, y+12, 'X')
		

		painter.setPen(QtCore.Qt.darkGray);
		painter.drawLine(2, 8, 6, 2);
		
		#label = QtWidgets.QLabel("Hello")
		#label.render(painter)
