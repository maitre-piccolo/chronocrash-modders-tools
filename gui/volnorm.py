import os, subprocess
import re
import shutil

from common import settings
from gui.util import FileInput
from PyQt5 import QtCore, QtWidgets

# List of files (other than sprites images and model files) that need to be copied too
OTHERS = ('.wav',)

class VolNormWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QFormLayout()
		
		dataPath = settings.get_option('general/data_path', '')
		charsFolderPath = os.path.join(dataPath, 'chars')
		self.charsFolder = FileInput('folder', charsFolderPath, 'Select chars folder', dataPath)
		layout.addRow(_('Workbase chars folder') + ' : ', self.charsFolder)
		

		
		button = QtWidgets.QPushButton(_('Start process'))
		button.clicked.connect(self.process)
		layout.addRow(button)
		
		self.setLayout(layout)
		
	def process(self):
		dataPath = settings.get_option('general/data_path', '')
		dig = True
		files = []

		baseFolder = self.charsFolder.text()

		exclude = (
			baseFolder + '/misc',
		)

		modelFiles = []

		f = open(os.path.join(dataPath, 'models.txt'), 'rU')
		data = f.readlines()
		p = re.compile('^[^#](.*)data/chars/(.*).txt')

		for line in data:
			m = p.search(line)
			if m:
				modelFiles.append(m.group(2) + '.txt')

		print( modelFiles)



		size = 0

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

			try:
				fileName = os.path.basename(srcfile)

				dirName = os.path.dirname(srcfile)
				
				saveFileName = '_src_' + fileName
				savePath = os.path.join(baseFolder, os.path.join(dirName, saveFileName))
				dbaPath = os.path.join(baseFolder, os.path.join(dirName, 'db_adjust')) # decibel adjust file
				if os.path.isfile(dbaPath):
					dbaFile = open(dbaPath, 'rU')
					lines = dbaFile.readlines()
					dba = lines[0].rstrip('\r\n')
					if(dba == '-'):
						dba = '-8'
					if len(lines) > 1:
						specif = eval(lines[1].rstrip('\r\n'))
					else:
						specif = {}
				else:
					dba = '-8'
					specif = {}
					
				if(fileName in specif):
					dba = str(specif[fileName])
					
				if not os.path.isfile(savePath):
					print( 'SAVING ' + savePath)
					shutil.copy(baseFolder + os.sep + srcfile, savePath)
				origPath = baseFolder + os.sep + srcfile
				
				cmd = 'sox ' + savePath + ' ' + origPath + " vol " + dba + " dB"
				if(dba != '-8'):
					print (origPath)
					print ('')
					
					print (cmd)
				subprocess.call(cmd, shell=True)
				
				#shutil.copy(baseFolder + os.sep + srcfile, dstdir)
				#size += os.path.getsize(f)
			except:
				
				pass

		print('Preparation finished')
		QtWidgets.QMessageBox.information(self, _('Done'), _('Preparation done'))
