# -*- coding: utf-8 -*-
import os, sys, traceback, shutil
import locale
import time
from datetime import datetime
now = datetime.now()


import logging



# print log in example.log instead of the console, and set the log level to DEBUG (by default, it is set to WARNING)



logFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'journal.log')
try:
	os.remove(logFile + '.1')
except:
	pass
if(os.path.isfile(logFile)): shutil.copyfile(logFile, logFile + '.1')
#logFile = 'journal2.log'
logging.basicConfig(filename=logFile, filemode='w', level=logging.DEBUG)



logger = logging.getLogger()
logger.debug(now)
logger.debug(logFile)
#print(logging.getLoggerClass().root.handlers[0].baseFilename)
#sys.stderr.write = logger.error
#sys.stdout.write = logger.info
#print = lambda *tup : logger.info(str(" ".join([str(x) for x in tup])))

#old_stdout = sys.stdout

#log_file = open("journal.log","w")

#sys.stdout = log_file



from random import uniform

from common import settings, util

import gettext
trans = gettext.NullTranslations()
trans.install()


from PyQt5 import QtCore, QtGui, QtWidgets

#from dialogeditor import DialogEditor

from gui.project import ProjectSelector
from gui.backupviewer import BackupViewer
from gui.main import MainEditorWidget
#from leveleditor import LevelEditorWidget

#from spritesorter import SpriteSorterWidget
from gui.menubar import MenuBar

from gui.main.fileselector import File

import style

TITLE = 'OpenBOR Utils & Tools'
TITLE = 'ChronoCrash Modders Tools'
import fallbackicons



class Frame(QtWidgets.QMainWindow):
	
	def __init__(self, parent=None):
		self.logger = logging.getLogger()
		QtWidgets.QMainWindow.__init__(self, parent)
		self.setWindowTitle(TITLE)
		
	
		
		
		try:
			self.setWindowIcon(QtGui.QIcon("icons/CMT.png"))
		except:pass
		
		if not QtGui.QIcon.hasThemeIcon("document-open"):
			import fallbackicons
			QtGui.QIcon.setThemeName('oxygen')
		
		try:
			self.move(settings.get_option('gui/window_x', 50), settings.get_option('gui/window_y', 50))
		except AttributeError:
			if(QtWidgets.QMessageBox.question(self, _('FATAL ERROR in settings'), _('Do you want to delete settings ?'), defaultButton=QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes):
				settings.delete()
				QtWidgets.QMessageBox.warning(self, _('Please restart'), _('Settings deleted please restart the app'))
				app.quit()

			
		self.resize(settings.get_option('gui/window_width', 700), settings.get_option('gui/window_height', 500))
		if(settings.get_option('gui/maximized', False)):
			self.maximized = True
			self.showMaximized()
		else:
			self.maximized = False
		
		menuBar = MenuBar(self)
		self.setMenuBar(menuBar)
		

		#menuBar.setNativeMenuBar(False)
		#menuBar.setVisible(True)
		
		#self.mainTabWidget = QtWidgets.QTabWidget(self)
		#self.mainTabWidget.setTabPosition(QtWidgets.QTabWidget.West)
		#self.mainTabWidget.setFocusPolicy(QtCore.Qt.ClickFocus)
		
		#ssWidget = SpriteSorterWidget()
		
		self.meWidget = MainEditorWidget(self)
		self.meWidget.menuBar = menuBar
		#leWidget = LevelEditorWidget()
		
		cw = QtWidgets.QWidget()
		#toolWidget = ToolWidget()
		#self.mainTabWidget.addTab(cw, _('Dialog editor'))
		self.projectSelector = ProjectSelector(self)
		#self.mainTabWidget.addTab(self.projectSelector, _('Project Selector'))
		
		
		self.backupViewer = BackupViewer(self)
		
		#self.meWidget = meWidget
		#self.mainTabWidget.addTab(self.meWidget, _('Main editor'))
		#self.mainTabWidget.addTab(eeWidget, _('Entity editor'))
		#self.mainTabWidget.addTab(leWidget, _('Level editor'))
		#self.mainTabWidget.addTab(ssWidget, _('Sprite sorter'))
		#self.mainTabWidget.addTab(toolWidget, _('Tools'))

		#self.mainTabWidget.currentChanged.connect(self.tabChange)
		
		
		from data.db import DB
		self.DB = DB('backups.db')
		File.DB = self.DB
		
		
		from dialogeditor import DialogEditor
		self.dialogWidget = DialogEditor()

		layout = QtWidgets.QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		cw.setLayout(layout)
		
		self.setCentralWidget(cw)
		#self.setCentralWidget(self.mainTabWidget)
		#cw.addWidget(self.mainTabWidget)
		self.meWidget.hide()
		self.dialogWidget.hide()
		self.backupViewer.hide()
		layout.addWidget(self.projectSelector)
		layout.addWidget(self.meWidget)
		layout.addWidget(self.dialogWidget)
		layout.addWidget(self.backupViewer)

		#self.textEditor = DialogEditor()
		#layout.addWidget(self.textEditor)
		
		self.setAcceptDrops(True)
		self.mainWidget = self.meWidget
		
		
		self.setTheme(settings.get_option('gui/widgets_theme', None))
		self.setEditorTheme(settings.get_option('gui/editor_theme', None))
		
		
		self.autosaveTimer = QtCore.QTimer()
		interval = settings.get_option('autobackup/timeout', 60) * 1000
		# interval = 10000
		self.autosaveTimer.setInterval(interval)
		self.autosaveTimer.timeout.connect(self.autoSave)
		self.autosaveTimer.start()
		
		
		#self.createTrayIcon()
		#self.trayIcon.show()
		#self.trayIcon.activated.connect(self.trayIconClick)
		
		
	def autoSave(self):
		if hasattr(self.mainWidget, "fileSelector"):
			self.mainWidget.backupUnsaved();
		
		
	def createTrayIcon(self):
		trayIconMenu = QtWidgets.QMenu(self);
#		trayIconMenu.addAction(minimizeAction);
#		trayIconMenu.addAction(maximizeAction);
#		trayIconMenu.addAction(restoreAction);
#		trayIconMenu.addSeparator();
		trayIconMenu.addAction(_('&Quit'), self.quit)

		self.trayIcon = QtWidgets.QSystemTrayIcon(self)
		self.trayIcon.setContextMenu(trayIconMenu)
		
		
	def changeEvent(self, e):
		if e.type() == QtCore.QEvent.WindowStateChange:
			if self.windowState() == QtCore.Qt.WindowMaximized:
				self.maximized = True
			elif self.windowState() == QtCore.Qt.WindowNoState:
				self.maximized = False
				
	def closeEvent(self, e):
		#if self.trayIcon.isVisible():
			#self.hide()
			#e.ignore()
			#return
		logging.debug("close event")
		self.quit(e)
		
	def dragEnterEvent(self, e):
		data = e.mimeData()
		
		if data.hasUrls():
			newUrls = []
			newText = ''
			for url in data.urls():
				path = url.toLocalFile()
				p, extension = os.path.splitext(path)
				if extension.lower() in ('.gif', '.png', '.pcx'):
					newText += path
					continue
				newUrls.append(url)
				
			# e.ignore()
			e.accept()
			data = QtCore.QMimeData()
			data.setText(newText)
			data.setUrls(newUrls)
			print(data.formats())

			#data.setUrls([QtCore.QUrl('file:///home/piccolo/workspace/OpenBOR/data/chars/abubo/7.gif')])
			print('*** PRINTING URLS ***')
			print(data.urls())
			
			e = QtGui.QDragEnterEvent(e.pos(), e.dropAction(), data, e.mouseButtons(), e.keyboardModifiers())
			print( e.mimeData().urls())
			print('*** END PRINTING URLS ***')
			e.accept()
		#QtWidgets.QMainWindow.dragEnterEvent(self, e)
			
	def dropEvent(self, e):
		
		data = e.mimeData()
		print("\nDROP EVENT", data.urls())
		print(data.formats())
				
		if data.hasUrls():
			for url in data.urls():
				path = url.toLocalFile()
				p, extension = os.path.splitext(path)
				#if extension.lower() in ('.gif', '.png', '.pcx'):
					#continue
				#path = url.toString()
				self.mainWidget.openFile(path)
		
	def newFile(self):
		#self.textEditor.clear()
		self.mainWidget.editNew()
		
	def openFile(self):
		self.mainWidget.openFile()
		
		
	def quit(self, e=None):
		logging.debug("MAIN FRAME QUIT EVENT " + str(e) )
		if not self.meWidget.close(True):
			if e is not None:
				e.ignore()
			return
		settings.set_option('gui/maximized', self.maximized)
		settings.set_option('gui/window_x', self.pos().x())
		settings.set_option('gui/window_y', self.pos().y())
		settings.MANAGER.save()
		#settings.MANAGER.saveTimer.cancel()
		app.quit()
			
			
	def resizeEvent(self, e):
		if(not self.maximized):
			#pos = self.mapToGlobal(self.pos())
			settings.set_option('gui/window_x', self.pos().x())
			settings.set_option('gui/window_y', self.pos().y())
			settings.set_option('gui/window_width', e.size().width())
			settings.set_option('gui/window_height', e.size().height())
		
	def saveFile(self):
		self.mainWidget.save()
		
	def saveFileAs(self):
		self.mainWidget.saveAs()
			
			
	def setEditorTheme(self, name=None):
		if name is None and self.sender() != None:
			name = self.sender().data()
			
		if name is not None:
			import themes
			themes.setEditorTheme(name)
			settings.set_option('gui/editor_theme', name)
		self.mainWidget.setTheme()
		
	def setMode(self, mode, params={}):
		self.mainWidget.hide()
		if mode == 'dialog':
			
			
			self.mainWidget = self.dialogWidget
		elif mode == 'project':
			self.mainWidget = self.projectSelector
		elif mode == 'mainEditor':
			self.mainWidget = self.meWidget
		elif mode == 'backupViewer':
			self.backupViewer.reload(params)
			self.mainWidget = self.backupViewer
			
		self.mainWidget.show()
		
		
	def setTheme(self, name=None):
		if name is None and self.sender() != None:
			name = self.sender().data()
			
		if name is None: return
		global app
		path = os.path.join ('themes', 'widgets', name + '.css')
		if not os.path.exists(path): return
		f = open(path)
		content = f.read()
		f.close()
		app.setStyleSheet(style.STYLE_SHEET + content)
		settings.set_option('gui/widgets_theme', name)
		
		
	def setSession(self, name=None, save=False, savePrevious=True):
		logging.debug("Setting session from main frame... [" + str(name) + '] save=' + str(save))
		if name is None and self.sender() != None:
			name = self.sender().data()
		print(name)
		if name is None: return

	
		# Before changing, save current
		if(savePrevious and not self.meWidget.close(True)): # False mean there was unsaved files and the user canceled operation
			return
		#if self.mainWidget.fileSelector.sessionName != None:
			#self.mainWidget.fileSelector.saveSession()
	

		# Meant for "save session as" call
		if(save): self.mainWidget.fileSelector.saveSession(name)

		if(name != ''):
			settings.set_option('general/last_session', name)
		self.mainWidget.fileSelector.loadSession(name)
			
	def tabChange(self, index):
		pass
		
	def trayIconClick(self, reason):
		self.setVisible(not self.isVisible())



def excepthook(exc_type, exc_value, exc_tb):
	tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
	print("error catched!:")
	print("error message:\n", tb)
	logging.getLogger().exception('CRASH')
	logging.debug(tb)
	#QtWidgets.QApplication.quit()
	# or QtWidgets.QApplication.exit(0)
	msg = QtWidgets.QMessageBox()
	msg.setIcon(QtWidgets.QMessageBox.Warning)
	msg.setText("AN ERROR HAS OCCURED")
	msg.setInformativeText('PLEASE COPY THE ERROR MESSAGE AND REPORT IT HERE : <a href="https://www.chronocrash.com/forum/threads/chronocrash-modders-tools.2467">https://www.chronocrash.com/forum/threads/chronocrash-modders-tools.2467/</a><pre>\n\nTHEN CLICK "OK", SAVE EVERYTHING YOU CAN AND RESTART THE SOFTWARE BEFORE CONTINUING USING IT\n\n(OR CONTINUE USING IT AT YOUR OWN RISKS)\n\n' + tb + '</pre>')
	msg.setWindowTitle("CRASH REPORT")
	msg.setDetailedText(tb)
	msg.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
	#msg.buttonClicked.connect(msgbtn)
	
	retval = msg.exec_()

sys.excepthook = excepthook

try:
	app = QtWidgets.QApplication(sys.argv)
	print(app.instance())
	
	memory = QtCore.QSharedMemory(app)
	memory.setKey("CMT")
	if memory.attach():
		print('already running')
	else:
		print('NOT running')
		memory.create(1)
	
	app.setApplicationName(TITLE)
	app.setStyleSheet(style.STYLE_SHEET)
	print (sys.argv)
	frame = Frame()
	frame.show()

	sys.exit(app.exec_())

except Exception:
	print('CRASH')
	logging.getLogger().exception('CRASH')
	raise
