import os, subprocess
import re
import shutil

from common import settings
from gui.util import FileInput
from PyQt5 import QtCore, QtGui, QtWidgets

START_INDEX = 0

NAMES = {
	0: 'idle',
	5: 'turn',
	10: 'crouch',
	20: 'walk',
	21: 'backwalk',
	40: 'jumpdelay',
	41: 'jump',
	42: 'jumpforward',
	52: 'jumpland',
	100: 'run',
	105: 'dodge',
	5120: 'rise'
}

DELAYS = {
	-1 : -1000,
	1 : 2,
	2 : 3,
	3 : 5,
	4 : 6,
	5 : 7,
	6 : 9,
	7 : 10,
	8 : 11,
	9 : 12,
	10 : 13
}

MERGE_NEXT_SAME = True # Merge next frame with previous frame if it is the same

def getName(aniGroup):
	if aniGroup in NAMES:
		return NAMES[aniGroup]
	elif aniGroup >= 120 and aniGroup <= 155:
		return 'block' + str(aniGroup)
	elif aniGroup >= 5000 and aniGroup <= 5300:
		return 'pain' + str(aniGroup)
	else:
		return 'freespecial' + str(aniGroup)
	
	
def getDelay(mugenDelay):
	mugenDelay = int(mugenDelay)
	if mugenDelay in DELAYS:
		return str(DELAYS[mugenDelay])
	else:
		return str(int(mugenDelay * 1.3))

class MugenWidget(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QFormLayout()
		
		dataPath = settings.get_option('general/datapath', '')
		charsFolderPath = os.path.join(dataPath, 'chars')

		
		outCharsFolderPath = os.path.join(dataPath, 'publishData' + os.sep + 'chars')
		lastSffPath = settings.get_option('mugen_tool/sff_file', '')
		if lastSffPath == '':
			lookPath = dataPath
		else:
			lookPath = os.path.dirname(lastSffPath)
		self.sffFile = FileInput('openFile', lastSffPath, 'Select character SFF file', lookPath, 'SFF Files (*.sff)')
		layout.addRow(_('SFF file') + ' : ', self.sffFile)
		
		
		self.airFile = FileInput('openFile', lastSffPath.replace('.sff', '.air'), 'Select character SFF file', lookPath, 'AIR Files (*.air)')
		layout.addRow(_('Air file') + ' : ', self.airFile)
		self.sffFile.changed.connect(self.airFile.clear)
		
		outCharsFolderPath = os.path.join(dataPath, 'publishData' + os.sep + 'chars')
		self.modelFolder = FileInput('folder', settings.get_option('mugen_tool/output_folder', ''), 'Select output folder', dataPath)
		layout.addRow(_('Output folder') + ' : ', self.modelFolder)
		
		button = QtWidgets.QPushButton(_('Start process'))
		button.clicked.connect(self.process)
		layout.addRow(button)
		
		self.setLayout(layout)
		
		self.baseWorkDir = os.getcwd()
		
	def clearLine(self, line):
		#line = self.clearComment(line)
		while line[0] == ' ' or line[0] == '	':
			line = line[1:]
		return line
		
	def process(self):
		os.chdir(self.baseWorkDir)
		
		output_folder = self.modelFolder.text()
		#if(os.path.isfile(output_folder)):
		settings.set_option('mugen_tool/output_folder', output_folder)
		
		parts = output_folder.split(os.sep)
		outputName = parts[-1]
		
		
		sff_path = self.sffFile.text()
		if(os.path.isfile(sff_path)):
			settings.set_option('mugen_tool/sff_file', sff_path)
			
		filename = os.path.basename(sff_path)
		(modelName, extension) = os.path.splitext(filename)
		


		output_path = os.path.join(output_folder, 'src_' + outputName + '.txt')
		
		tmp_path = os.path.join(output_folder, 'tmp.txt')

		cmd = 'wine other/sffextract.exe -d -i -o "' + tmp_path + '" "' + sff_path + '"'
		subprocess.call(cmd, shell=True)
		print('extraction done')
		
		
		air_path = self.airFile.text()
		if(air_path == ''):
			air_path = os.path.join(os.path.dirname(sff_path), modelName + '.air')
		
		# First, gather additional information from air file
		airFile = open(air_path, 'rU')
		airData = airFile.readlines()
		
		airParams = re.compile('(-?\d+),(.*)(-?\d+),(.*)(-?\d+)(.*)')
		
		animParams = {}

		#22002,0, 0,0, 1
		#group, frameNumber, x_shift, y_shift, delay
		for line in airData:
			line = self.clearLine(line)
			#print line
			if not line[0] == ';' and ('[Begin Action' in line or '[Begin action' in line):
				group = int(re.search(r'\d+', line).group())
				if group not in animParams:
					animParams[group] = []

			elif airParams.match(line):
				# Remove troubleshooting characters
				try:
					lastIndex = line.index(';')
					line = line[:lastIndex]
				except ValueError:
					pass
				
				try:
					lastIndex = line.index(']')
					line = line[:lastIndex]
				except ValueError:
					pass


				#line = line.replace(';', '')
				params = line.split(',')
				for i in range(min(len(params), 5)):
					try:
						params[i] = int(params[i])
					except ValueError:
						params[i] = 'FAIL'
				params = params[0:min(len(params), 5)]
				#print params
				spriteGroup = params[0]
				#if spriteGroup not in animParams:
					#animParams[spriteGroup] = []
				currentAnim = animParams[group]
				currentAnim.append(params)
					
		#for key, anim in animParams.items()[0:5]:
			#print anim
			#print ''
		
		
		# Gather sprites base information
		tmpFile = open(tmp_path, 'rU')
		tmpData = tmpFile.readlines()
		
		spriteGroups = {}
		i = 10
		spriteID = START_INDEX
		for line in tmpData:
			if '.pcx' in line and line[0] != ';':
				spritePath = line
				i = 0
			elif(i<=4):
				if(i == 1):
					group = int(line)
					if group not in spriteGroups:
						spriteGroups[group] = {}
					#currentFrame = [spritePath,]
					original = spritePath.split('\\')[1].split('.pcx')[0] + '.gif'
					currentFrame = [original, str(spriteID) + '.gif']
					spriteID+=1
				else:
					#currentFrame = spriteGroups[group][-1]
					currentFrame.append(int(line))
				if i == 2: # sprite number in group
					spriteGroups[group][int(line)] = currentFrame
			i+= 1
						
				
		#for key, anim in spriteGroups.items()[0:5]:
			#print anim
			#print ''
		
		
		# Merge same siblings, if there are any
		if(MERGE_NEXT_SAME):
			for key, data in animParams.items():
				if(len(data) > 1):
					modelLine = data[0]
					delayAddition = 0
					#for line in data[1:]:
					removeIndexes = []
					for j in range(1, len(data)):
						line = data[j]
						i = 0
						while(i <= 4 and line[i] == modelLine[i]):
							i+=1
						if(i > 4):
							identic = True
						else:
							identic = line[i] == modelLine[i]
							
						if identic:
							delayAddition += line[4]
							#data.remove(line)
							removeIndexes.append(j)
						else:
							modelLine[4] += delayAddition
							delayAddition = 0
							modelLine = line
							
					modelLine[4] += delayAddition
					for index in sorted(removeIndexes, reverse=True):
						del data[index]
				
			
		currentDelay = None
		output = ''
		for key, data in animParams.items():
			name = getName(key)
			output += 'anim ' + name + '\n'
			for line in data:
				spriteGroup = line[0]
				spriteNumber = str(line[1])
				#sprites = spriteGroups[key]
				if spriteGroup == -1:
					delay = str(line[4])
					output += '	delay ' + getDelay(delay) + '\n'
					output += '	offset ' + str(line[2]) + ' ' + str(line[3]) + '\n'
					output += '	frame data/chars/misc/empty.gif\n'
				else:
					try:
						sprites = spriteGroups[spriteGroup]
						spriteData = sprites[int(spriteNumber)]
					except KeyError:
						print('Error, no sprites group ' + str(spriteGroup))
						spriteData = ('ERROR_STR','ERROR_STR',0, 0, 0, 0, 0)
						#print sprites
						#print spriteNumber
					try:
						
						#print line
						delay = str(line[4])
						if delay != currentDelay:
							currentDelay = delay
							output += '	delay ' + getDelay(delay) + '\n'
						#if(line[2] != 0):
							#print(str(spriteData[3]) + ' - ' + str(line[2]))
						output += '	offset ' + str(spriteData[3] - line[2]) + ' ' + str(spriteData[4] - line[3]) + '\n'
						output += '	frame data/chars/' + outputName + '/' + spriteData[1] + '\n'
					except IndexError:
						print('Error for sprites group ' + str(spriteGroup) + ' - sprite number : ' + spriteNumber)
						#pass

			currentDelay = -42
			output += '\n\n'
			
		outputFile = open(output_path, 'w')
		outputFile.write(output)
		outputFile.close()
		
		
		i_param = '..\\' + modelName + '\*.pcx'
		o_param = '..\\new\*.gif'
		iviewPath = os.path.join(os.path.dirname(__file__), '../other') 
		os.chdir(iviewPath)
		
		print(iviewPath)
	
		cmd = 'wine i_view32.exe "' + i_param + '" /convert="' + o_param + '"'
		subprocess.call(cmd, shell=True)
		i = START_INDEX
		spritesPath = os.path.join(os.path.dirname(__file__), '../new')
		for key, groups in spriteGroups.items():
			for key, spriteData in groups.items():
				shutil.move(os.path.join(spritesPath, spriteData[0]), os.path.join(output_folder, spriteData[1]))
				#os.rename(os.path.join(spritesPath, spriteData[0]), os.path.join(output_folder, spriteData[1]))
		#for f in sorted(os.listdir(spritesPath)):
			#os.rename(os.path.join(spritesPath, f), os.path.join(output_folder, str(i) + '.gif'))
			#i+=1
		
		print('conversion finished')
		QtWidgets.QMessageBox.information(self, _('Done'), _('Conversion finished'))
		
