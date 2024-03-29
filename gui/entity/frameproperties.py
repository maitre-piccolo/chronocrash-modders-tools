import os, re, time, logging

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

from common import settings

from data import AttackBox, BBox, BindData

from gui.level.items import Entity


class AbstractOverlayEditor(QtWidgets.QWidget):
	
	SETTING_KEY = 'opponent'
	
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.setMaximumSize(300,2000)
		self.parent = parent
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)
		
		self.widgets = {}
		
		layout = QtWidgets.QGridLayout()
		
		offsetGB = QtWidgets.QGroupBox(_('Entity'))
		self.showOpponent = QtWidgets.QCheckBox(_('Show entity'))
		self.showOpponent.stateChanged.connect(self.showOpponentChanged)
		layout.addWidget(self.showOpponent, 0, 0)
		
		layout.addWidget(QLabel(_("Entity model")), 1, 0)
		
		self.entityModelEntry = QtWidgets.QComboBox() # get option
		self.entityModelEntry.setEditable(True)
		self.entityModelEntry.setObjectName("entityModelCB")
		
		
		
		self.entityModelEntry.currentTextChanged.connect(self.entityModelEntryChanged)
		
		layout.addWidget(self.entityModelEntry, 2, 0)
		
		layout.addWidget(QLabel(_("Entity animation")), 3, 0)
		
		self.entityAnimation = QtWidgets.QComboBox() # get option
		self.entityAnimation.setEditable(True)
		self.entityAnimation.setCurrentText(settings.get_option('entity/last_' + self.SETTING_KEY + '_animation', 'idle'))
		self.entityAnimation.currentTextChanged.connect(self.entityAnimationChanged)
		self.entityAnimation.setObjectName("entityAnimCB")
		layout.addWidget(self.entityAnimation, 4, 0)
		
		i=4
		
		i+=1
		
		layout.addWidget(QLabel(_("Entity palette")), i, 0)
		i+=1
		self.entityPalette = QtWidgets.QComboBox() # get option
		self.entityPalette.setEditable(True)
		# self.entityPalette.setCurrentText(settings.get_option('entity/last_' + self.SETTING_KEY + '_animation', 'idle'))
		self.entityPalette.currentTextChanged.connect(self.entityPaletteChanged)
		self.entityPalette.setObjectName("entityPaletteCB")
		layout.addWidget(self.entityPalette, i, 0)
		
		
		i+=1
		if (self.SETTING_KEY == 'opponent'):
			showSquareOffset = settings.get_option('entity/binding_show_square_offset', False)
			showCrossOffset = settings.get_option('entity/binding_show_cross_offset', True)
			
			self.showCrossOffset = QtWidgets.QCheckBox(_('Show cross offset'))
			self.showCrossOffset.setChecked(showCrossOffset)
			self.showCrossOffset.stateChanged.connect(self.showCrossOffsetChanged)
			layout.addWidget(self.showCrossOffset, i, 0)
			
			i+=1
			self.showSquareOffset = QtWidgets.QCheckBox(_('Show square offset'))
			self.showSquareOffset.setChecked(showSquareOffset)
			self.showSquareOffset.stateChanged.connect(self.showSquareOffsetChanged)
			layout.addWidget(self.showSquareOffset, i, 0)
			
		else:
			layout.addWidget(QtWidgets.QLabel('Frame'), i, 0)
			self.frameSpinBox = QtWidgets.QSpinBox()
			self.frameSpinBox.valueChanged.connect(self.updateFrame)
			i+=1
			layout.addWidget(self.frameSpinBox, i, 0)
		
		
		
		
		# self.toggleDragEntity = QtWidgets.QPushButton(_('Toggle drag entity'))
		# self.toggleDragEntity.setCheckable(True)
		# layout.addWidget(self.toggleDragEntity, 5, 0)
		
		offsetGB.setLayout(layout)
		
		self.layout.addWidget(offsetGB, 0)
		
		
		
		
		
	def entityModelEntryChanged(self, widget):
		print("entity model entry changed", self.entityModelEntry.currentText())
		if (self.changeEntityModel()):
			if (self.loadingModels):
				
				if(self.SETTING_KEY == "opponent"):
					self.parent.frameEditor.loadOpponent()
					self.reloadAnims()
					self.reloadPalettes()
					self.parent.frameEditor.opponent = None
				else:
					self.parent.frameEditor.loadOnionSkinModel()
					self.reloadAnims()
					self.reloadPalettes()
					self.parent.frameEditor.onionSkinEnt = None
			else:
				self.showOpponent.setChecked(True)
				if(self.SETTING_KEY == "opponent"):
					self.parent.frameEditor.showOpponent(True)
				else:
					self.parent.frameEditor.showOnionSkin(True)
				self.reloadAnims()
				self.reloadPalettes()
	
	def entityAnimationChanged(self, widget):
		print("entity animation changed", self.entityAnimation.currentText())
		if self.loadingAnims : return
		if self.changeEntityAnimation():
			self.showOpponent.setChecked(True)
	
	
	def entityPaletteChanged(self, widget):
		print("entity palette changed", self.entityPalette.currentText())
		if self.loadingAnims : return
		if self.changeEntityPalette():
			self.showOpponent.setChecked(True)
			
	def reloadModels(self):
		self.loadingModels = True
		lastModel = settings.get_option('entity/last_' + self.SETTING_KEY + '_model', '')
		print('last Model', lastModel)
		self.entityModelEntry.clear()
		sortAlpha = settings.get_option('entity/binding_models_sort_alphabetical', False)
		models = Entity.AVAILABLE_MODELS
		if(sortAlpha): models.sort()
		
		self.entityModelEntry.addItems(models)
		# self.entityModelEntry.setEditText(settings.get_option('entity/last_opponent_model', ''))
		self.entityModelEntry.setCurrentText(lastModel)
		self.loadingModels = False
		
	def reloadAnims(self, default=None):
		print('reloading anims')
		self.loadingAnims = True
		if(default == None): default = settings.get_option('entity/last_' + self.SETTING_KEY + '_animation', '')
		self.entityAnimation.clear()
		
		if(self.SETTING_KEY == 'opponent'):
			opponent = self.parent.frameEditor.opponent
		else:
			opponent = self.parent.frameEditor.onionSkinEnt
		if(opponent != None):
			self.entityAnimation.addItems(opponent.anims.keys())
		self.entityAnimation.setCurrentText(default)
		
		self.loadingAnims = False
		
	def reloadPalettes(self, default=None):
		
		self.entityPalette.clear()
		
		if(self.SETTING_KEY == 'opponent'):
			opponent = self.parent.frameEditor.opponent
		else:
			opponent = self.parent.frameEditor.onionSkinEnt
		if(opponent != None):
			self.entityPalette.addItems(opponent.palettes)
		self.entityPalette.setCurrentText(default)
		
		# self.loadingAnims = False
		
		
		
	def changeEntityModel(self):
		txt = self.entityModelEntry.currentText()
		if(txt in Entity.AVAILABLE_MODELS and txt != self.loadedModel):
			print("Loading opponent")
			self.loadedModel = txt
			
			if self.SETTING_KEY == "opponent":
				self.parent.frameEditor.opponentModel = txt
			else:
				self.parent.frameEditor.onionSkinModel = txt
			settings.set_option('entity/last_' + self.SETTING_KEY + '_model', txt)
			# self.entityModelEntry.setProperty("class", "valid")
			# self.entityModelEntry.setObjectName("entityModelCB-valid")
			self.setColorState(self.entityModelEntry, 'valid')
			
			return True
			
		else:
			# print("Refusing opponent", txt)
			if(txt not in Entity.AVAILABLE_MODELS):
				# if(self.loadedModel != None and not self.loadedModel.startswith(txt)):
				# self.entityModelEntry.setProperty("class", "valid")
				# self.entityModelEntry.setObjectName("entityModelCB-valid")
				
				self.setColorState(self.entityModelEntry, 'invalid')
			else:
				self.setColorState(self.entityModelEntry, 'valid')
				# self.entityModelEntry.setProperty("class", "invalid")
				# self.entityModelEntry.setObjectName("entityModelCB-invalid")
			return False
			
			
	def setColorState(self, CB, state):
		theme = settings.get_option('gui/widgets_theme', None)
		if(theme == 'Dark'):
			if(state == 'valid'):
				CB.setStyleSheet("QComboBox { background: rgb(0, 100, 0); selection-background-color: rgb(78, 99, 0);}");
			else:
				CB.setStyleSheet("QComboBox { background: rgb(100, 0, 0); selection-background-color: rgb(78, 99, 0); }");
		else:
			if(state == 'valid'):
				CB.setStyleSheet("QComboBox { background: rgb(0, 255, 0); selection-background-color: rgb(233, 99, 0); }");
			else:
				CB.setStyleSheet("QComboBox { background: rgb(255, 0, 0); selection-background-color: rgb(233, 99, 0); }");
			
	def changeEntityAnimation(self):
		
		txt = self.entityAnimation.currentText()
		
		if self.SETTING_KEY == 'opponent':
		
			opponent = self.parent.frameEditor.opponent
		else:
			opponent = self.parent.frameEditor.onionSkinEnt
			
		if opponent == None: return False
		if(txt in opponent.anims):
			opponent.changeAnimation(txt)
			opponent.setAt(0)
			opponent.actualizeFrame()
			print("Loading animation")
			
			settings.set_option('entity/last_' + self.SETTING_KEY + '_animation', txt)
			self.entityAnimation.setStyleSheet("QComboBox { background: rgb(0, 255, 0); selection-background-color: rgb(233, 99, 0); }");
			
			return True
			
		else:
			if(txt not in Entity.AVAILABLE_MODELS): self.entityAnimation.setStyleSheet("QComboBox { background: rgb(255, 0, 0); selection-background-color: rgb(233, 99, 0); }");
			return False
		
	def changeEntityPalette(self):
		txt = self.entityPalette.currentText()
		
		if self.SETTING_KEY == 'opponent':
		
			opponent = self.parent.frameEditor.opponent
		else:
			opponent = self.parent.frameEditor.onionSkinEnt
			
		print("changePalette", self.SETTING_KEY, txt, opponent.palettes)
			
		if opponent == None: return False
		if(txt in opponent.palettes):
			opponent.setPalette(txt)
			opponent.setAt(0)
			opponent.actualizeFrame()
			print("Loading palette")
			
			# settings.set_option('entity/last_' + self.SETTING_KEY + '_animation', txt)
			# self.entityAnimation.setStyleSheet("QComboBox { background: rgb(0, 255, 0); selection-background-color: rgb(233, 99, 0); }");
			
			return True
			
		else:
			# if(txt not in Entity.AVAILABLE_MODELS): self.entityAnimation.setStyleSheet("QComboBox { background: rgb(255, 0, 0); selection-background-color: rgb(233, 99, 0); }");
			return False
		
	
	def showOpponentChanged(self):
		showOpponent = self.showOpponent.isChecked()
		self.parent.frameEditor.showOpponent(showOpponent)
		
	def showCrossOffsetChanged(self):
		show = self.showCrossOffset.isChecked()
		settings.set_option('entity/binding_show_cross_offset', show)
		opponent = self.parent.frameEditor.opponent
		if(opponent != None):
			opponent.showCrossOffsetChanged(show)
		
	def showSquareOffsetChanged(self):
		show = self.showSquareOffset.isChecked()
		settings.set_option('entity/binding_show_square_offset', show)
		opponent = self.parent.frameEditor.opponent
		if(opponent != None):
			opponent.showSquareOffsetChanged(show)
			
			
	def updateFrame(self):
		self.parent.frameEditor.onionSkinFrame = self.frameSpinBox.value()
		self.parent.frameEditor.loadFrame()
		
	def valueChanged(self, *args):
		# for
		# blocker = QSignalBlocker(self.double_spin_box)
		# blocker.__enter__()
		
		if not self.loading:
			# print('value changed', args)
			self.loading = True
			self.updateData()
			if(self.mask != ''):
				self.parent.rebuildText()
			
			self.parent.frameEditor.loadFrame()
			self.loading = False



class BindingEditor(AbstractOverlayEditor):
	def __init__(self, parent):
		AbstractOverlayEditor.__init__(self, parent)
		

		
		
		
		# self.toggleDragEntity = QtWidgets.QPushButton(_('Toggle drag entity'))
		# self.toggleDragEntity.setCheckable(True)
		# self.layout.addWidget(self.toggleDragEntity, 5, 0)
		
		
		
		# Binding GB
		self.bindingGB = CustomGroupBox(_('Binding settings'))
		self.bindingGB.addClicked.connect(self.addBindData)
		layout = QtWidgets.QGridLayout()
		
		self.bindingGB.setLayout(layout)
		# self.bindingGB.addClicked.connect(self.addBox)
		# self.bindingGB.deleteClicked.connect(self.deleteBox)
		
		x = QtWidgets.QSpinBox()
		y = QtWidgets.QSpinBox()
		z = QtWidgets.QSpinBox()
		direction = QtWidgets.QSpinBox()
		frame = QtWidgets.QSpinBox()
		
		self.widgets['bind'] = {'x':x, 'y':y, 'z':z, 'direction':direction, 'frame':frame}
		
		layout.addWidget(QLabel(_("X")), 0, 0)
		layout.addWidget(x, 1, 0)
		layout.addWidget(QLabel(_("Y")), 0, 1)
		layout.addWidget(y, 1, 1)
		
		layout.addWidget(QLabel(_("Z")), 2, 0)
		layout.addWidget(z, 3, 0)
		layout.addWidget(QLabel(_("Direction")), 2, 1)
		layout.addWidget(direction, 3, 1)
		
		layout.addWidget(QLabel(_("Frame")), 4, 0)
		layout.addWidget(frame, 5, 0)
		
		self.layout.addWidget(self.bindingGB, 0)
		
		self.layout.addStretch(1)
		
		self.bindingGB.setDisabled(True)
		
		
		maskGB = QtWidgets.QGroupBox(_('Text Mask'))
		layout = QtWidgets.QGridLayout()
		
		self.maskEntry = QtWidgets.QLineEdit() # 
		
		self.mask = settings.get_option('entity/binding_mask', '')
		self.maskEntry.setText(self.mask)
		
		self.maskEntry.textChanged.connect(self.maskChanged)
		
		
		layout.addWidget(self.maskEntry, 0, 0)
		
		self.additionalTranslationsEntry = QtWidgets.QLineEdit() # 
		self.additionalTranslationsEntry.setText(str(settings.get_option('entity/binding_additional_translations', {})))
		
		self.additionalTranslationsEntry.textChanged.connect(self.translationsChanged)
		layout.addWidget(QLabel(_("Additional translations")), 1, 0)
		layout.addWidget(self.additionalTranslationsEntry, 2, 0)
		maskGB.setLayout(layout)
		
		
		
		self.layout.addWidget(maskGB, 0)
		
		

		# self.entityModelEntry.currentTextChanged.emit('')
		
		for w in list(self.widgets['bind'].values()):
			w.setRange(-1000,1000)
			w.valueChanged.connect(self.valueChanged)
			
		self.widgets['bind']['direction'].setRange(-2, 2)
		
		
		self.loading = False
		self.loadingModels = False
		self.loadingAnims = False
		
		self.loadedModel = None
		
		
		
		
	def addBindData(self):
		if len(self.parent.anim) == 0 : return
		
		data = self.parent.frames[self.parent.currentFrame]
		data['bind'] = BindData()
		data['bind']['direction'] = -1
		data['bind']['z'] = 1
		
		if(self.mask != ''):
			self.parent.rebuildText()
		self.parent.frameEditor.loadFrame()
		
		

			
		
	def maskChanged(self, widget):
		mask = self.maskEntry.text()
		settings.set_option('entity/binding_mask', mask)
		self.mask = mask
		
		
	def translationsChanged(self, widget):
		try:
			settings.set_option('entity/binding_additional_translations', eval(self.additionalTranslationsEntry.text()))
		except:
			QtWidgets.QMessageBox.warning(self, _('Formatting Error'), _('The data is not formatted right'))
		
		
	def refreshEntPos(self):
		
		self.loading = True
		opponent = self.parent.frameEditor.opponent
		newX = int(opponent.pos().x()) + opponent.xOffset
		self.widgets['bind']['x'].setValue(newX)
		y = opponent.altitude
		if(y == None): y = 0
		print('pos y', int(opponent.pos().y()), y)
		newY = -int(opponent.pos().y()) - opponent.yOffset + y
		self.widgets['bind']['y'].setValue(newY)
		print('\nrefresh', newX, newY)
		opponent.setAt(0)
		self.loading = False
		self.valueChanged()
		
		


		
	def loadData(self, data):
		if(self.loading):
			return
		self.changeEntityModel()
		
		
		self.loading = True
		
		if('bind' in data):
			self.bindingGB.setDisabled(False)
			data = data['bind']
		else:
			self.bindingGB.setDisabled(True)
			data = []
			
		x = 0
		y = 0
		z = 0
		direction = 0
		frame = 0
		
		keys = ['x', 'y', 'z', 'direction', 'frame']
		for key in keys:
			val = 0 # default
			if(key in data):
				val = data[key]
				try:
					self.widgets['bind'][key].setValue(val)
				except:
					print('could not set value', val, 'for key', key)
			
		# 
			

			
		
		self.loading = False
		
	

	
	def updateData(self, data=None):
		if data is None:
			data = self.parent.frames[self.parent.currentFrame]
			
			
		if('bind' in data):
			bindData = data['bind']
			keys = ['x', 'y', 'z', 'direction', 'frame']
			for key in keys:
				bindData[key] = self.widgets['bind'][key].value()
				
	
		
		


class OnionSkinEditor(AbstractOverlayEditor):
	
	SETTING_KEY = 'onionskin'
	
	def __init__(self, parent):
		AbstractOverlayEditor.__init__(self, parent)
		
		onionSkinGB = QtWidgets.QGroupBox(_('Onion skin type'))
		layout = QtWidgets.QVBoxLayout()
		onionSkinGB.setLayout(layout)
		
		self.b1 = QRadioButton("Classic")
		self.b1.setChecked(True)
		self.b1.toggled.connect(lambda:self.btnstate(self.b1))
		layout.addWidget(self.b1)
		
		self.b2 = QRadioButton("Semi-transp. overlay")
		self.b2.toggled.connect(lambda:self.btnstate(self.b2))
		
		self.b3 = QRadioButton("Opaque overlay")
		self.b3.toggled.connect(lambda:self.btnstate(self.b3))
		
		self.b4 = QRadioButton("Fully transp. overlay")
		self.b4.toggled.connect(lambda:self.btnstate(self.b4))


		layout.addWidget(self.b2)
		layout.addWidget(self.b3)
		layout.addWidget(self.b4)
		
		self.layout.addWidget(onionSkinGB, 0)
		
		self.loading = False
		self.loadingModels = False
		self.loadingAnims = False
		
		self.loadedModel = None
		
	def btnstate(self, button):
		if(button == self.b1): self.parent.frameEditor.onionSkinMode = 1
		if(button == self.b2): self.parent.frameEditor.onionSkinMode = 2
		if(button == self.b3): self.parent.frameEditor.onionSkinMode = 3
		if(button == self.b4): self.parent.frameEditor.onionSkinMode = 4
		
		self.parent.frameEditor.loadFrame()
		
		
		
	def showOpponentChanged(self):
		print("show onion skin changed")
		showOpponent = self.showOpponent.isChecked()
		self.parent.frameEditor.showOnionSkin(showOpponent)
		


class FramePropertiesEditor(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self)
		self.setAutoFillBackground(True); 
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
		z1B = QtWidgets.QSpinBox()
		z2B = QtWidgets.QSpinBox()
		self.widgets['bbox'] = {'x':xB, 'y':yB, 'w':wB, 'h':hB, 'z1':z1B, 'z2': z2B}

		
		layout.addWidget(QLabel(_("X")), 0, 0)
		layout.addWidget(QLabel(_("Y")), 0, 1)
		layout.addWidget(xB, 1, 0)
		layout.addWidget(yB, 1, 1)
		
		layout.addWidget(QLabel(_("Width")), 2, 0)
		layout.addWidget(QLabel(_("Height")), 2, 1)
		layout.addWidget(wB, 3, 0)
		layout.addWidget(hB, 3, 1)
		
		layout.addWidget(QLabel(_("Z bg")), 4, 0)
		layout.addWidget(QLabel(_("Z fg")), 4, 1)
		layout.addWidget(z1B, 5, 0)
		layout.addWidget(z2B, 5, 1)
		
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
		
		
		
		# ******     RANGEZ BOX       ********
		self.rangezGB = CustomGroupBox(_('Range Z'))
		layout = QtWidgets.QGridLayout()
		
		self.rangezGB.setLayout(layout)
		self.rangezGB.addClicked.connect(self.addBox)
		self.rangezGB.deleteClicked.connect(self.deleteBox)
		
		zMin = QtWidgets.QSpinBox()
		zMax = QtWidgets.QSpinBox()
		
		self.widgets['rangez'] = {'zMin':zMin, 'zMax':zMax}
		
		layout.addWidget(QLabel(_("Z min")), 0, 0)
		layout.addWidget(zMin, 1, 0)
		layout.addWidget(QLabel(_("Z max")), 0, 1)
		layout.addWidget(zMax, 1, 1)
		
		self.showRangeZ = QtWidgets.QCheckBox(_('Visualize range Z'))
		self.showRangeZ.setChecked(settings.get_option('entity/visualize_rangez', True))
		self.showRangeZ.stateChanged.connect(self.visualizeRangeZChanged)
		layout.addWidget(self.showRangeZ, 2, 0)
		
		self.layout.addWidget(self.rangezGB, 0)
		
		
		
		#self.layout.addWidget(ButtonGroupBox(), 0)
		
		self.layout.addStretch(1)
		
		
		self.loading = False
		
		for w in list([delay] + list(self.widgets['offset'].values()) + list(self.widgets['bbox'].values()) + list(self.widgets['range'].values()) + list(self.widgets['rangez'].values()) + list(self.widgets['attack'].values())):
			w.setRange(-1000000,1000000)
			w.valueChanged.connect(self.valueChanged)
		
		self.unblockable.stateChanged.connect(self.valueChanged)
		self.noflash.stateChanged.connect(self.valueChanged)
		
		self.bboxGB.setDisabled(True)
		self.attackGB.setDisabled(True)
	
	
	def visualizeRangeZChanged(self):
		settings.set_option('entity/visualize_rangez', self.showRangeZ.isChecked())
		self.parent.frameEditor.loadFrame()
		
	def addBox(self):
		if len(self.parent.anim) == 0 : return
		if self.sender() == self.attackGB:
			data = self.parent.frames[self.parent.currentFrame]
			data['attack'] = AttackBox()
		elif self.sender() == self.bboxGB:
			data = self.parent.frames[self.parent.currentFrame]
			data['bbox'] = BBox()
		elif self.sender() == self.rangeGB:
			data = self.parent.frames[0]
			data['range'] = (-10, 100)
		elif self.sender() == self.rangezGB:
			data = self.parent.frames[0]
			data['rangez'] = (-15, 15)
			
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
		elif self.sender() == self.rangeGB:
			data = self.parent.frames[0]
			data['deleteRange'] = True
		elif self.sender() == self.rangezGB:
			data = self.parent.frames[0]
			data['deleteRangez'] = True
			
		self.parent.rebuildText()
		self.parent.frameEditor.loadFrame()
		
		
	def loadData(self, data, anim):
		
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
			params = data['bbox'].getParams()
			x, y, w, h = params[0:4]
			self.widgets['bbox']['x'].setValue(x)
			self.widgets['bbox']['y'].setValue(y)
			self.widgets['bbox']['w'].setValue(w)
			self.widgets['bbox']['h'].setValue(h)
			
			try: self.widgets['bbox']['z1'].setValue(params[4])
			except: pass
			
			try: self.widgets['bbox']['z2'].setValue(params[5])
			except: pass
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
			
			
		if 'range' in anim.frames[0]:
			self.rangeGB.setDisabled(False)
			xMin, xMax = anim.frames[0]['range']
			self.widgets['range']['xMin'].setValue(xMin)
			self.widgets['range']['xMax'].setValue(xMax)
		else:
			self.rangeGB.setDisabled(True)
			
			
		if 'rangez' in anim.frames[0]:
			self.rangezGB.setDisabled(False)
			zMin, zMax = anim.frames[0]['rangez']
			self.widgets['rangez']['zMin'].setValue(zMin)
			self.widgets['rangez']['zMax'].setValue(zMax)
		else:
			self.rangezGB.setDisabled(True)
			
			
			
		self.loading = False
		
		
		
	
	'''
		Fill the data argument with the form values
	
	'''
	def updateData(self, data=None):
		
		def updateNotEmpty(box, key, value):
			#print("HERE", key, value)
			if value == 0 and (box.phantom or box.data[key] == None):
				return
			
			box.data[key] = value
			box.phantom = False
			
		print('DATA UPDATE')
		if data is None:
			data = self.parent.frames[self.parent.currentFrame]
			
		delay = self.widgets['delay'].value()
		if delay != 0:
			data['delay'] = delay
			
		x = self.widgets['offset']['x'].value()
		y = self.widgets['offset']['y'].value()
		print('offset', x, y)
		if 'offset' in data:
			data['offset'] = [x, y]
		elif x!= 0 or y !=0:
			
			i = self.parent.currentFrame - 1
			previousOffsetFound = False
			while not previousOffsetFound and i >=0:
				dataPrevFrame = self.parent.frames[i]
				if 'offset' in dataPrevFrame:
					previousOffsetFound = True
					x, y = dataPrevFrame['offset']
				i -= 1
				
			
			data['offset'] = [x, y]
			
		if 'bbox' in data:
			bbox = data['bbox']
			x, y, w, h = bbox.getParams()[0:4]
			x = self.widgets['bbox']['x'].value()
			y = self.widgets['bbox']['y'].value()
			w = self.widgets['bbox']['w'].value()
			h = self.widgets['bbox']['h'].value()
			z1 = self.widgets['bbox']['z1'].value()
			z2 = self.widgets['bbox']['z2'].value()
			bbox.x = x
			bbox.y = y
			bbox.width = w
			bbox.height = h
			bbox.z1 = z1
			bbox.z2 = z2
			
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
			updateNotEmpty(abox, 'size.z.background', depth)
			
		
		frame0 = self.parent.frames[0]
		if 'range' in frame0:
			
			xMin, xMax = frame0['range']
			xMin = self.widgets['range']['xMin'].value()
			xMax = self.widgets['range']['xMax'].value()
			frame0['range'] = [xMin, xMax]
			
		if 'rangez' in frame0:
			
			xMin, xMax = frame0['rangez']
			xMin = self.widgets['rangez']['zMin'].value()
			xMax = self.widgets['rangez']['zMax'].value()
			frame0['rangez'] = [xMin, xMax]


	def valueChanged(self, *args):
		# return
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
		
		self.painter = None
	
	
	def setDisabled(self, disabled):
		# print('\nset Disabled', disabled)
		for i in range(self.layout().count()):
			widget = self.layout().itemAt(i).widget()
			widget.setEnabled(not disabled)
		self.disabled = disabled
		self.update()
				
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
		
		rect = e.rect();
   
   
   
		
		QtWidgets.QGroupBox.paintEvent(self, e)
		# if( self.painter != None): 
			# self.painter.end()
			# self.update()
			# del self.painter
			# pass
		painter = QtGui.QPainter(self)
		# painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		# painter.fillRect(e.rect(), QtCore.Qt.transparent);

		# painter.eraseRect(rect);
		# painter = self.painter
		painter.setRenderHint(QtGui.QPainter.Antialiasing);
		
		
		# painter.eraseRect(0, 0, 300,300)
		# print('\nDisabled', self.disabled)
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
		# self.update() # cause leak
		#label = QtWidgets.QLabel("Hello")
		#label.render(painter)
