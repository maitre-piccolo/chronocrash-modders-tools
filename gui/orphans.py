import os
import re
import shutil

from common import settings
from gui.util import FileInput
from PyQt5 import QtCore, QtWidgets


class OrphanWidget(QtWidgets.QWidget):
	def __init__(self, parent):
		QtWidgets.QWidget.__init__(self, parent)
		self.parent = parent # prevent garbabe collector to delete parent dialog
		layout = QtWidgets.QFormLayout()
		
		dataPath = settings.get_option('general/data_path', '')
		
		layout.addRow(QtWidgets.QLabel('Warning : this tool will delete files from the input folder.'))
		layout.addRow(QtWidgets.QLabel('If you want to make a copy that includes only files used, use "Prepare PAK" tool instead'))
		
		
		self.singleChar = FileInput(self, 'openFile', dataPath, 'Select char model', dataPath)
		layout.addRow(_('Single char model') + ' : ', self.singleChar)
		
	
		charsFolderPath = os.path.join(dataPath, 'chars')
		self.charsFolder = FileInput(self, 'folder', charsFolderPath, 'Select chars folder', dataPath)
		layout.addRow(_('Workbase chars folder') + ' : ', self.charsFolder)
		
		#outCharsFolderPath = settings.get_option('pak/chars_out_path', os.path.join(dataPath, 'publishData' + os.sep + 'chars'))
		
		
		button = QtWidgets.QPushButton(_('Start process'))
		button.clicked.connect(self.process)
		layout.addRow(button)
		
		
		layout.addRow(QtWidgets.QLabel("Not found"))
		self.logWidget = QtWidgets.QPlainTextEdit('Log not found...')
		layout.addRow(self.logWidget)
		
		layout.addRow(QtWidgets.QLabel(""))
		layout.addRow(QtWidgets.QLabel("Found"))
		self.logWidgetFound = QtWidgets.QPlainTextEdit('Log found...')
		layout.addRow(self.logWidgetFound)
		
		
		button = QtWidgets.QPushButton(_('Create copy'))
		#button.clicked.connect(self.process)
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
		spriteFiles = []
		
		

		f = open(os.path.join(dataPath, 'models.txt'), 'r')
		data = f.readlines()
		p = re.compile('^[^#](.*)data/chars/(.*).txt')

		for line in data:
			m = p.search(line)
			if m:
				modelFiles.append(m.group(2) + '.txt')
				
				
			p = re.compile('^[^#](.*)data/chars/([^/]*)([^.]*)(.*)')
		#p2 = re.compile('^[^#](.*)data\\chars\\([^.]*)(.*)')
		
		#modelFiles = ['zangief/zangief.txt',]
		modelFiles = ['alfred/alfred.txt',]
		
		singleCharText = self.singleChar.text()
		if(singleCharText.strip() != ''):
			rPath = 'data' + os.path.dirname( singleCharText.replace(dataPath, ''))
			modelFilesAbs = [{'abs':singleCharText, 'rPath':rPath, 'path': os.path.dirname(singleCharText)  }]
			
			print(modelFilesAbs)
			
		else:
		
			modelFilesAbs = []
			for modelFile in modelFiles:
				modelFilesAbs.append({'abs': baseFolder + os.sep + modelFile, 'rPath':os.path.dirname(modelFile), 'path':os.path.dirname(baseFolder + os.sep + modelFile)})
			
		for data in modelFilesAbs:	
			
			modelFile = data['abs']
			#f = open(baseFolder + os.sep + modelFile, 'r') # 'r'
			f = open(modelFile, 'r') # 'r'
			
			#charsPath = os.path.dirname(baseFolder + os.sep + modelFile)
			#charsPath = os.path.dirname(baseFolder + os.sep + modelFile)
			charsPath = data['path']
			
			#charsRPath = os.path.dirname(modelFile)
			charsRPath = data['rPath']
			
			listOfFiles = os.listdir(charsPath)
			
			
			origLEN = len(listOfFiles)
			
			for i in range(len(listOfFiles)):
				listOfFiles[i] = charsRPath + '/' + listOfFiles[i]
			
			
			
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
					#print (extension)
					pos = extension.find('\r')
					if pos != -1:
						extension = extension[0:pos]
					spriteFiles.append('data/chars/' + m.group(2) + m.group(3) + extension)
					
					try:
						print(m.group(2) + m.group(3) + extension)
						listOfFiles.remove('data/chars/' + m.group(2) + m.group(3) + extension)
					except ValueError:
						pass
				#else:
					#m = p2.search(line)
					#if m:
						#spriteFiles.append(m.group(2) + m.group(3)[0:4])

		#print spriteFiles
		
		print("length", origLEN, len(listOfFiles))
		
		self.logWidget.setPlainText('Orphans count ' + str(len(listOfFiles)) + '\n\n' +  '\n'.join(listOfFiles) )
		
		self.logWidgetFound.setPlainText('Found count ' + str(len(spriteFiles)) + '\n\n' + '\n'.join(spriteFiles) )
		return

		files = spriteFiles + modelFiles

		size = 0
		dstroot = self.outCharsFolder.text()
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
