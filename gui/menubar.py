# -*- coding: utf-8 -*-
from PyQt5 import QtGui, QtCore, QtWidgets

from common import settings, xdg
from gui import modales, util

from qutepart import EverydayPart

import os



class MenuBar(QtWidgets.QMenuBar):
	def __init__(self, parent):
		self.core = parent
		QtWidgets.QMenuBar.__init__(self, parent)
		
		
		
		
		#fileMenu = QtWidgets.QMenu(_('&File'))
		fileMenu = self.addMenu(_('&File'))
		fileMenu.addAction(_('&New'), self.core.newFile, QtGui.QKeySequence(self.tr("Ctrl+N", "File|New")))
		fileMenu.addAction(_('&Open'), self.core.openFile, QtGui.QKeySequence(self.tr("Ctrl+O", "File|Open")))
		fileMenu.addAction(_('&Save'), self.core.saveFile, QtGui.QKeySequence(self.tr("Ctrl+S", "File|Save")))
		fileMenu.addAction(_('Save &As'), self.core.saveFileAs, QtGui.QKeySequence(self.tr("Shift+Ctrl+S", "File|Save As")))
		fileMenu.addAction(_('&Quit'), self.core.close, QtGui.QKeySequence(self.tr("Ctrl+Q", "File|Quit")))
		#self.addMenu(fileMenu)

		editMenu = self.addMenu(_('&Edit'))
		editMenu.addAction(_('&Undo'), self.tmp, QtGui.QKeySequence(self.tr("Ctrl+Z", "Edit|Undo")))
		editMenu.addAction(_('&Redo'), self.tmp, QtGui.QKeySequence(self.tr("Shift+Ctrl+Z", "Edit|Redo")))
		editMenu.addSeparator()
		editMenu.addAction(_('Settings'), self.openSettings)
		#self.addMenu(editMenu)
		
		
		self.projects_quickly_loadable = []
		self.viewMenu = self.addMenu(_('&View'))
		self.viewMenu.addAction(_('Project selector'), self.changeProject)
		self.viewMenu.addAction(_('Backups viewer'), self.backupViewer)
		self.viewMenu.addAction(_('Story editor'), self.dialogEdit)
		
		
		self.sessionMenu = self.addMenu(_('Sess&ion'))
		self.reloadSessionsList()
		
		themeMenu = self.addMenu(_('Theme'))
		editorThemeMenu = themeMenu.addMenu(_('Editor'))
		#tActions = []
		theme = settings.get_option('gui/editor_theme', None)
		actionGroup = QtWidgets.QActionGroup(self)
		for f in os.listdir('themes/editor'):
			name = os.path.splitext(f)[0]
			a = editorThemeMenu.addAction(name, self.core.setEditorTheme)
			a.setData(name)
			a.setCheckable(True)
			if name == theme: a.setChecked(True)
			actionGroup.addAction(a)
			
		colorThemeMenu = themeMenu.addMenu(_('Widgets'))
		#tActions = []
		theme = settings.get_option('gui/widgets_theme', None)
		actionGroup = QtWidgets.QActionGroup(self)
		for f in os.listdir('themes/widgets'):
			name = os.path.splitext(f)[0]
			a = colorThemeMenu.addAction(name, self.core.setTheme)
			a.setData(name)
			a.setCheckable(True)
			if name == theme: a.setChecked(True)
			actionGroup.addAction(a)
			
		
		
		toolMenu = self.addMenu(_('&Tools'))
		
		toolMenu.addAction(_('Tool dialog'), self.toolSelect)
		toolMenu.addAction(_('Font preview'), self.openFontPreview)
		
		
		#projectMenu = self.addMenu(_('&Project'))
		#projectMenu.addAction(_('Change project'), self.changeProject)
		
		
		optionMenu = self.addMenu(_('&Options'))
		self.optionMenu = optionMenu
		
		self.addOption('gui/double_click_to_load_element', False, 'Double click to load element in list', True)
		
		
		
		def autoCollapse():
			autoCollapse = settings.get_option('gui/auto_collapse', True)
			settings.set_option('gui/auto_collapse', not autoCollapse)
		
		a = optionMenu.addAction(_('Auto-collapse'), autoCollapse)
		a.setCheckable(True)
		autoCollapse = settings.get_option('gui/auto_collapse', True)
		a.setChecked(autoCollapse)
		
		
		def setSmallSceen():
			autoCollapse = settings.get_option('gui/small_screen', False)
			settings.set_option('gui/small_screen', not autoCollapse)
		
		a = optionMenu.addAction(_('Small screen mode'), setSmallSceen)
		a.setCheckable(True)
		smallScreen = settings.get_option('gui/small_screen', False)
		a.setChecked(smallScreen)
		
		
		def setLegacyCommand():
			legacyCommands = settings.get_option('misc/legacy_commands', False)
			settings.set_option('misc/legacy_commands', not legacyCommands)
		
		a = optionMenu.addAction(_('Legacy Mode (commands)'), setLegacyCommand)
		a.setCheckable(True)
		legacyCommands = settings.get_option('misc/legacy_commands', False)
		a.setChecked(legacyCommands)
		
		
		def setTabAction():
			tabAlwaysIndent = settings.get_option('editor/tab_always_indent', True)
			tabAlwaysIndent = not tabAlwaysIndent
			settings.set_option('editor/tab_always_indent', tabAlwaysIndent)
			EverydayPart.tabAlwaysIndent = tabAlwaysIndent
		
		a = optionMenu.addAction(_('Tab always indent'), setTabAction)
		a.setCheckable(True)
		tabAlwaysIndent = settings.get_option('editor/tab_always_indent', True)
		a.setChecked(tabAlwaysIndent)
		# also init here
		EverydayPart.tabAlwaysIndent = tabAlwaysIndent
		
		def setLevelAutoPlay():
			autoPlay = settings.get_option('level/auto_play_on_load', True)
			autoPlay = not autoPlay
			settings.set_option('level/auto_play_on_load', autoPlay)
			self.core.mainWidget.levelEditor.autoPlayOnLoad = autoPlay
		
		a = optionMenu.addAction(_('Level Editor / Auto-play on Load'), setLevelAutoPlay)
		a.setCheckable(True)
		tabAlwaysIndent = settings.get_option('level/auto_play_on_load', True)
		a.setChecked(tabAlwaysIndent)
		
		
		def setForceTransparency():
			forceTransp = settings.get_option('gui/force_transparency', False)
			forceTransp = not forceTransp
			
			
			settings.set_option('gui/force_transparency', forceTransp)
			util.FORCE_TRANSPARENCY
			self.informRestart()
		
		a = optionMenu.addAction(_('Force transparency (will cause slow down)'), setForceTransparency)
		a.setCheckable(True)
		forceTransp = settings.get_option('gui/force_transparency', False)
		a.setChecked(forceTransp)
		# also init here
		util.FORCE_TRANSPARENCY = forceTransp
		
		
		def setBindingModelsSortOrder():
			sortOrder = settings.get_option('entity/binding_models_sort_alphabetical', False)
			sortOrder = not sortOrder
			
			
			settings.set_option('entity/binding_models_sort_alphabetical', sortOrder)
			
			self.informRestart()
		
		a = optionMenu.addAction(_('Binding GUI - sort models from A to Z'), setBindingModelsSortOrder)
		a.setCheckable(True)
		sortOrder = settings.get_option('entity/binding_models_sort_alphabetical', False)
		a.setChecked(sortOrder)
		# also init here ?
		
		
		def setOpenGLRendering():
			openGLRendering = settings.get_option('gui/opengl_rendering', False)
			openGLRendering = not openGLRendering
			
			
			settings.set_option('gui/opengl_rendering', openGLRendering)
			self.informRestart()
		
		a = optionMenu.addAction(_('OpenGL Rendering'), setOpenGLRendering)
		a.setCheckable(True)
		openGLRendering = settings.get_option('gui/opengl_rendering', False)
		a.setChecked(openGLRendering)
		
		
		def disableAutoBackup():
			disableAutoBackupProp = settings.get_option('general/disable_auto_backup', False)
			disableAutoBackupProp = not disableAutoBackupProp
			
			
			settings.set_option('general/disable_auto_backup', disableAutoBackupProp)
			# self.informRestart()
		
		a = optionMenu.addAction(_('Disable basic Auto-Backup'), disableAutoBackup)
		a.setCheckable(True)
		disableAutoBackupProp = settings.get_option('general/disable_auto_backup', False)
		print("disable autobackup", disableAutoBackupProp)
		a.setChecked(disableAutoBackupProp)
		
		
		def disableAdvancedAutoBackup():
			openGLRendering = settings.get_option('general/disable_advanced_auto_backup', False)
			openGLRendering = not openGLRendering
			
			
			settings.set_option('general/disable_advanced_auto_backup', openGLRendering)
			# self.informRestart()
		
		a = optionMenu.addAction(_('Disable advanced Auto-Backup'), disableAdvancedAutoBackup)
		a.setCheckable(True)
		openGLRendering = settings.get_option('general/disable_advanced_auto_backup', False)
		a.setChecked(openGLRendering)
		
		
		def usePIL():
			usePILOption = settings.get_option('general/usePIL_for_sprites', True)
			usePILOption = not usePILOption
			
			
			settings.set_option('general/usePIL_for_sprites', usePILOption)
			# self.informRestart()
			
			util.USE_PIL = usePILOption
			self.informRestart()
		
		a = optionMenu.addAction(_('Use PIL to interpret sprites'), usePIL)
		a.setCheckable(True)
		usePILOption = settings.get_option('general/usePIL_for_sprites', True)
		a.setChecked(usePILOption)
		util.USE_PIL = usePILOption
		
		
		def enableCompletion():
			completionEnabled = settings.get_option('editor/completion_enabled', True)
			completionEnabled = not completionEnabled
			
			
			settings.set_option('editor/completion_enabled', completionEnabled)
			# self.informRestart()
			
			
			self.informRestart()
		
		a = optionMenu.addAction(_('Enable completion'), enableCompletion)
		a.setCheckable(True)
		completionEnabled = settings.get_option('editor/completion_enabled', True)
		a.setChecked(completionEnabled)
		
		
		def setSearchOnTextChange():
			searchOnTextChange = settings.get_option('misc/search_on_text_change', False)
			searchOnTextChange = not searchOnTextChange
			
			
			settings.set_option('misc/search_on_text_change', searchOnTextChange)
			# self.informRestart()
			
			
			self.informRestart()
		
		a = optionMenu.addAction(_('Search on text change (without pressing enter)'), setSearchOnTextChange)
		a.setCheckable(True)
		searchOnTextChange = settings.get_option('misc/search_on_text_change', False)
		a.setChecked(searchOnTextChange)
		
		
		def setCheckMissingExtension():
			checkForMissingExt = settings.get_option('misc/check_for_missing_extension', False)
			checkForMissingExt = not checkForMissingExt
			
			
			settings.set_option('misc/check_for_missing_extension', checkForMissingExt)
			# self.informRestart()
			util.CHECK_MISSING_EXTENSION = checkForMissingExt
			
			self.informRestart()
		
		a = optionMenu.addAction(_('Check for missing extensions'), setCheckMissingExtension)
		a.setCheckable(True)
		checkForMissingExt = settings.get_option('misc/check_for_missing_extension', False)
		a.setChecked(checkForMissingExt)
		util.CHECK_MISSING_EXTENSION = checkForMissingExt
		
		
		def setAutoAddEmptyLines():
			value = settings.get_option('entity/auto_add_empty_line_between_animations', True)
			value = not value
			
			
			settings.set_option('entity/auto_add_empty_line_between_animations', value)
			
	
			
		
		a = optionMenu.addAction(_('Force empty lines between animations'), setAutoAddEmptyLines)
		a.setCheckable(True)
		value = settings.get_option('entity/auto_add_empty_line_between_animations', True)
		a.setChecked(value)
		
		
		def setValue():
			value = settings.get_option('editor/anim_selector_on_left', False)
			value = not value
			
			
			settings.set_option('editor/anim_selector_on_left', value)
			self.informRestart()
			
		
		a = optionMenu.addAction(_('Main editor - anim selector on left side'), setValue)
		a.setCheckable(True)
		value = settings.get_option('editor/anim_selector_on_left', False)
		a.setChecked(value)
	
	
		
		self.runMenu = self.addMenu(_('&Run'))
		self.reloadRunPrograms()
		

		helpMenu = self.addMenu(_('&Help'))
		
		helpMenu.addAction(_('Tips'), self.tips)
		helpMenu.addAction(_('Donate'), self.donate)
		helpMenu.addAction(_('About this tool'), self.about)
		helpMenu.addAction(_('About Qt'), lambda:QtWidgets.QMessageBox.aboutQt(self))
		

		#parent.moduleLoaded.connect(self.loadModuleMenus)
		
		#for module in self.core.loadedModules:
			#self.loadModuleMenus(module)
	

	def addOption(self, key, defaultValue, label, informRestart=False):
		def setValue():
			value = settings.get_option(key, defaultValue)
			settings.set_option(key, not value)
			
			if informRestart:
				self.informRestart()
		
		a = self.optionMenu.addAction(_(label), setValue)
		a.setCheckable(True)
		value = settings.get_option(key, defaultValue)
		a.setChecked(value)
		
		
		
	def addProjectQuickAccess(self, path):
		if(path not in self.projects_quickly_loadable):
			self.projects_quickly_loadable.append(path)
			self.viewMenu.addAction(_('Quick switch to') + ' : ' + path, lambda: self.core.mainWidget.loadProject(path))
		
	def reloadSessionsList(self):
		sessionMenu = self.sessionMenu
		sessionMenu.clear()
		sessionMenu.addAction(_('New Session'), self.newSession)
		sessionMenu.addSeparator()
		sessionMenu.addAction(_('Save Session'), self.saveSession)
		sessionMenu.addAction(_('Save Session As'), self.saveSessionAs)
		sessionMenu.addSeparator()
		
		actionGroup = QtWidgets.QActionGroup(self)
		currentSession = settings.get_option('general/last_session', 'Default')
		for f in os.listdir(os.path.join(xdg.get_data_home(), 'sessions')):
			a = sessionMenu.addAction(f, self.core.setSession)
			a.setData(f)
			a.setCheckable(True)
			if f == currentSession:
				a.setChecked(True)
			actionGroup.addAction(a)
	
	def tmp(self):
		pass
		
	def informRestart(self):
		QtWidgets.QMessageBox.information(self, _('Please restart'), _("You'll need to restart the app for that setting to be properly applied"))
		
	def about(self):
		# Credits
		modales.AboutDialog().exec()
		
	def donate(self):
		modales.DonateDialog().exec()
		
	def tips(self):
		modales.TipsDialog().exec()
			
	def checkForNewFiles(self):
		progressNotifier = self.core.statusBar.addProgressNotifier(self.core.reloadLibraries)
		self.core.DB.checkForNewFiles(progressNotifier)
		
		
	def backupViewer(self):
		self.core.setMode('backupViewer')
		
	def changeProject(self):
		self.core.setMode('project')
		
		
	def dialogEdit(self):
		
		self.core.setMode('dialog')
		
		
	def loadModuleMenus(self, module):
		if(module == 'pictures' or module == 'videos'):
			pictures = QtWidgets.QMenu(_(module[0].capitalize() + module[1:]))
			#pictures.addAction(_("Check for doubloons"))
			pictures.addAction(_('Check for doubloons'), self.core.managers[module].containerBrowser.checkForDoubloons)
			pictures.addAction(_("Move to UC structure"), lambda: self.moveToUCStructure(module))
			pictures.addSeparator()

			panelGroup = QtGui.QActionGroup(self)

			browserMode = settings.get_option(module + '/browser_mode', 'panel')
			propPanelVisible = settings.get_option(module + '/prop_panel_visible', True)

			panes = pictures.addAction( _('Multi-panes'), lambda: self.core.managers[module].setBrowserMode('panes'))
			panes.setCheckable(True)
			if(browserMode == 'panes'):
				panes.setChecked(True)
			panes.setActionGroup(panelGroup)

			panel = pictures.addAction(_('All in one panel'), lambda: self.core.managers[module].setBrowserMode('panel'))
			panel.setCheckable(True)
			if(browserMode == 'panel'):
				panel.setChecked(True)
			panel.setActionGroup(panelGroup)
			
			
			pictures.addSeparator()
			viewGroup = QtGui.QActionGroup(self)

			viewMode = settings.get_option(module + '/view_mode', 'icons')

			icons = pictures.addAction( _('Icons'), lambda: self.core.managers[module].setViewMode('icons'))
			icons.setCheckable(True)
			if(viewMode == 'icons'):
				icons.setChecked(True)
			icons.setActionGroup(viewGroup)

			aList = pictures.addAction(_('List'), lambda: self.core.managers[module].setViewMode('compact_list'))
			aList.setCheckable(True)
			if(viewMode == 'compact_list'):
				aList.setChecked(True)
			aList.setActionGroup(viewGroup)
			
			
			pictures.addSeparator()
			hidePropPanel = pictures.addAction(_('Hide properties panel'), self.core.managers[module].togglePropPanelVisibilty)
			hidePropPanel.setCheckable(True)
			hidePropPanel.setChecked(not propPanelVisible)

			self.addMenu(pictures)
		elif(module == 'music'):
			def reloadCovers():
				progressNotifier = self.core.statusBar.addProgressNotifier()
				self.core.DB.reloadCovers(progressNotifier)
			music = QtGui.QMenu(_('Music'))
			music.addAction(_('Reload covers'), reloadCovers)
			
			
			self.addMenu(music)
		

	def addProgramToRun(self):
		
		listPrograms = settings.get_option('misc/run_menu_programs', [])
		
		path = QtWidgets.QFileDialog.getOpenFileName(self)
		path = path[0]
		if path == '':
			return
		else:
			listPrograms.append(path)
			settings.set_option('misc/run_menu_programs', listPrograms)
			self.reloadRunPrograms()
			
		
		
	def deleteRunProgram(self, name=None):
		if name is None and self.sender() != None:
			name = self.sender().data()
			
		if name is not None:
			listPrograms = settings.get_option('misc/run_menu_programs', [])
			listPrograms.remove(name)
			settings.set_option('misc/run_menu_programs', listPrograms)
			self.reloadRunPrograms()
		
		
	
	def reloadRunPrograms(self):
		
		self.runMenu.clear()
		
		listPrograms = settings.get_option('misc/run_menu_programs', [])
		
		i = 1
		for f in listPrograms:
			keySeq = settings.get_option('shortcuts/run_program_' + str(i), 'Ctrl+' + str(i))
			a = self.runMenu.addAction(f, self.runProgram, QtGui.QKeySequence(self.tr(keySeq)))
			a.setData(f)
			i+=1
		
		self.runMenu.addSeparator()
		self.runMenu.addAction(_('Add new program'), self.addProgramToRun)
		
		if(len(listPrograms) >0):
			deleteMenu = self.runMenu.addMenu(_('Delete'))
			for f in listPrograms:
				a = deleteMenu.addAction(f, self.deleteRunProgram)
				a.setData(f)
				
		def setCWDOption():
			changeCWD = settings.get_option('misc/run_menu_cwd_program_location', False)
			settings.set_option('misc/run_menu_cwd_program_location', not changeCWD)
		
		a = self.runMenu.addAction(_('Run program from program location (CWD)'), setCWDOption)
		a.setCheckable(True)
		changeCWD = settings.get_option('misc/run_menu_cwd_program_location', False)
		a.setChecked(changeCWD)
			
	
	def runProgram(self, name=None):
		changeCWD = settings.get_option('misc/run_menu_cwd_program_location', False)
		
		
		
		if name is None and self.sender() != None:
			name = self.sender().data()
		
		if(changeCWD):
			cwd = os.path.dirname(name)
		else:
			cwd = None
			
		if name is not None:
			import subprocess
			subprocess.Popen([name], cwd=cwd)

		

	def newSession(self):
		self.core.setSession('')
		
	def saveSession(self):
		name = settings.get_option('general/last_session', 'Default')
		self.core.mainWidget.fileSelector.saveSession(name)

	def saveSessionAs(self):
		text = QtWidgets.QInputDialog.getText(self, _("Session name"), _("Name"))[0]

		if text != '':
			self.core.setSession(text, True, savePrevious=False)
		self.reloadSessionsList()
	
	
	def openFontPreview(self):
		from gui.fontpreview import FontPreview
		w = FontPreview()
		w.show()
	
	def toolSelect(self):
		from tools import ToolWidget
		w = ToolWidget()
		w.show()
		
	def openSettings(self):
		dialog = modales.SettingsEditor()
		dialog.exec_()
		
	def openTips(self):
		dialog = modales.TipsDialog()
		dialog.exec_()
		
class StatusBar(QtWidgets.QStatusBar):
	def __init__(self):
		QtWidgets.QStatusBar.__init__(self)
		
	def addProgressNotifier(self, methodToRun=None):
		notifier = ProgressNotifier(self)
		notifier.done.connect(lambda : self.removeNotifier(notifier, methodToRun))
		self.addWidget(notifier)
		return notifier
		
	def removeNotifier(self, notifier, methodToRun=None):
		#notifier = self.sender()
		self.removeWidget(notifier)
		if methodToRun is not None:
			methodToRun()

class ProgressNotifier(QtWidgets.QProgressBar):
	
	valueRequested = QtCore.pyqtSignal(int)
	pulseRequested = QtCore.pyqtSignal()
	done = QtCore.pyqtSignal()
	
	def __init__(self, statusBar):
		QtWidgets.QProgressBar.__init__(self)
		self.statusBar = statusBar
		self.valueRequested.connect(self.setValue)
		self.pulseRequested.connect(self.doPulse)
		
	def doPulse(self):
		self.setRange(0, 0)
		
	def emitDone(self):
		self.done.emit()
		
	def pulse(self):
		self.pulseRequested.emit()
		
		
	def setFraction(self, val):
		val *= 100
		if(self.maximum != 100):
			self.setMaximum(100)
		self.valueRequested.emit(val)

			
