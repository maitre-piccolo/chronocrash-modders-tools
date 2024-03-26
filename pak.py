import os
import re
import shutil

from common import settings
from gui.util import FileInput
from PyQt5 import QtCore, QtWidgets

#blabla dd  deee

# List of files (other than sprites images and model files) that need to be copied too
OTHERS = ('.wav',)

class PakWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self, parent)
		self.parent = parent # prevent garbabe collector to delete parent dialog
		layout = QtWidgets.QFormLayout()
		
		button = QtWidgets.QPushButton('What is this tool ?')
		button.clicked.connect(self.showInfos)
		layout.addRow(button )
		
		dataPath = settings.get_option('general/data_path', '')
		charsFolderPath = os.path.join(dataPath, 'chars')
		self.charsFolder = FileInput(self, 'folder', charsFolderPath, 'Select chars folder', dataPath)
		layout.addRow(_('Workbase chars folder') + ' : ', self.charsFolder)
		
		outCharsFolderPath = settings.get_option('pak/chars_out_path', os.path.join(dataPath, 'publishData' + os.sep + 'chars'))
		self.outCharsFolder = FileInput(self, 'folder', outCharsFolderPath, 'Select chars folder', dataPath)
		layout.addRow(_('Publish chars folder') + ' : ', self.outCharsFolder)
		
		button = QtWidgets.QPushButton(_('Start process'))
		button.clicked.connect(self.process)
		layout.addRow(button)
		
		self.setLayout(layout)
		
	def showInfos(self):
		txt = '''Some clarifications for the "prepake PAK" tool

The tools asks you to set two folders : workbase chars folder, and publish chars folder.

The two folders (workbase and publish) must be different.

Workbase folder should be the path folder of your private dev chars folder (this one can't be empty, and must exists).

And publish folder should be the path folder of the public "release" chars folder, the one you will use to build the pak that you will upload (this folder can be empty, and will be created if it doesn't exist).

The purpose of the tool is to create a copy of your private dev chars folder that includes only the files referenced in txt files, so that you can have a lot of unused material/stuff in your private dev chars folder, and they won't be copied in the "release" version. Useful to create a trimmed version of chars folder for release, and reduce size of PAK.



So for example, the paths should be something like C:/project path/data/chars for workbase folder
and C:/project path/release/data/chars for publish folder

It won't work if you use the same folders as one serves as the basis of the other.

Also, note that it's not the data path that must but set, but data/chars

For now this tool only works on chars folder.'''
		
		dialog = QtWidgets.QDialog(self, QtCore.Qt.Window)
		dialog.setWindowTitle("Prepare PAK infos")
		mainLayout = QtWidgets.QVBoxLayout()
		
		widget = QtWidgets.QPlainTextEdit(self)
		widget.setPlainText(txt)
		mainLayout.addWidget(widget)
		
		dialog.setLayout(mainLayout)
		dialog.exec()
		
	def process(self):
		dataPath = settings.get_option('general/data_path', '')
		dig = True
		files = []

		baseFolder = self.charsFolder.text()
		
		dstroot = self.outCharsFolder.text()
		
		if(baseFolder == dstroot):
			QtWidgets.QMessageBox.information(self, _('Warning'), _('Workbase path and publish path must be different'))
			return

		exclude = (
			baseFolder + '/misc',
		)

		modelFiles = []
		spriteFiles = []

		f = open(os.path.join(dataPath, 'models.txt'), 'r')
		data = f.readlines()
		p = re.compile('^[^#](.*)data/chars/(.*).txt')

		for line in data:
			m = p.search(line)
			if m:
				modelFiles.append(m.group(2) + '.txt')

		#print modelFiles

		#modelFiles = [modelFiles[0],]

		#modelFiles = [baseFolder + os.sep + 'TAN_CLARK/clark.txt',]
		#modelFiles = [baseFolder + os.sep + 'zangief/zangief.txt',]

		p = re.compile('^[^#](.*)data/chars/([^/]*)([^.]*)(.*)')
		#p2 = re.compile('^[^#](.*)data\\chars\\([^.]*)(.*)')
		for modelFile in modelFiles:
			f = open(baseFolder + os.sep + modelFile, 'r') # 'r'
			
			data = f.readlines()

			for line in data:
				m = p.search(line)
				#print line
				#print ''
				#print '________________________'
				#print ''
				if m:
					#spriteFiles.append(baseFolder + os.sep + m.group(2)[0:-1])
					extension = m.group(4)[0:4]
					print (extension)
					pos = extension.find('\r')
					if pos != -1:
						extension = extension[0:pos]
					spriteFiles.append(m.group(2) + m.group(3) + extension)
				#else:
					#m = p2.search(line)
					#if m:
						#spriteFiles.append(m.group(2) + m.group(3)[0:4])

		#print spriteFiles

		files = spriteFiles + modelFiles

		size = 0
		
		settings.set_option('pak/chars_out_path', dstroot)
		for f in files:
			srcfile = f
			dstdir =  os.path.join(dstroot, os.path.dirname(srcfile))
			try:
				os.makedirs(dstdir)
			except OSError:
				pass
			try:	
				shutil.copy(baseFolder + os.sep + srcfile, dstdir)
				#size += os.path.getsize(f)
			except:
				pass
		print (size)


		# ***** COPY OTHER FILES, such as .wav sound files *****
		
		def scanFolder(folder, dig, files):
			
			def checkFileInterest(folder, filename, extension):
				if extension in OTHERS and filename[0:5] != '_src_':
					try:
						files.append((folder, filename))
						recovered_paths.append(folder + os.sep + filename)
					except UnicodeDecodeError:
						error_paths.append(folder + os.sep + filename)



			
			for f in os.listdir(folder):
				if f[0] != '.':
					if os.path.isfile(os.path.join(folder, f)):
						(shortname, extension) = os.path.splitext(f)
						checkFileInterest(folder, f, extension)
					else:
						if(dig and folder + os.sep + f not in exclude):
							scanFolder(folder + os.sep + f, dig, files)
			#return (files)
			
			
			#recovered_paths = set(recovered_paths)
			return recovered_paths

		recovered_paths = []
		error_paths = []
			
		# WAV
		#print scanFolder(baseFolder, dig, files)


		for f in scanFolder(baseFolder, dig, files):
			srcfile = f[len(baseFolder)+1:]

			dstdir =  os.path.join(dstroot, os.path.dirname(srcfile))
			try:
				os.makedirs(dstdir)
			except OSError:
				pass
			try:	
				shutil.copy(baseFolder + os.sep + srcfile, dstdir)
				#size += os.path.getsize(f)
			except:
				pass

		print('Preparation finished')
		QtWidgets.QMessageBox.information(self, _('Done'), _('Preparation done'))
