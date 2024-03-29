# -*- coding: utf-8 -*-
import os, subprocess
import re
import shutil

from common import settings
from gui.util import FileInput
from PyQt5 import QtCore, QtGui, QtWidgets

PLAIN_TEXT = True

#

class CommandListGenerator(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		layout = QtWidgets.QFormLayout()
		
		self.formatCB = QtWidgets.QComboBox()
		self.formatCB.addItems(['HTML (view)', 'HTML (code)', 'OpenBOR Script (if + int IDs)', 'OpenBOR Script (switch + string IDs)'])
		self.formatCB.setCurrentIndex(settings.get_option('command_list/output_format', 0))
		self.formatCB.currentIndexChanged.connect(self.changeOutputFormat)
		
		
		self.modelPath = QtWidgets.QLineEdit()
		dataPath = settings.get_option('general/data_path', '')
		self.modelPath.setText(settings.get_option('command_list/file', dataPath))
		
		button = QtWidgets.QPushButton('...')
		def setPath():
			path = QtWidgets.QFileDialog.getOpenFileName(self, _('Open Entity File'), os.path.join(settings.get_option('general/data_path', ''), 'chars'), self.tr("Entity Files (*.txt);;All files (*.*)"))[0]
			self.modelPath.setText(path)
		button.clicked.connect(setPath)
		
		w = QtWidgets.QWidget()
		l = QtWidgets.QHBoxLayout()
		w.setLayout(l)
		
		layout.addRow(_('Output format') + ' : ', self.formatCB)
		
		l.addWidget(self.modelPath, 1)
		l.addWidget(button, 0)
		
		layout.addRow(_('Model file') + ' : ', w)
		

		
		button = QtWidgets.QPushButton(_('Process file'))
		button.clicked.connect(self.processFile)
		layout.addRow(button)
		
		if(PLAIN_TEXT):
			self.editor = QtWidgets.QPlainTextEdit()
		else:
			self.editor = QtWidgets.QTextEdit()
			
		policy = self.editor.sizePolicy()
		policy.setVerticalStretch(1)
		self.editor.setSizePolicy(policy)

		button = QtWidgets.QPushButton(_('Process inline text'))
		button.clicked.connect(self.processText)
		layout.addRow(self.editor)
		layout.addRow(button)
		

		
		self.setLayout(layout)
		
	def addChainFollow(self, move):
		if move['id'][0:6] == 'attack':
			attackNumber = move['id'][6:]

			try:
				pos = self.atchain.index(attackNumber)
				if pos != -1 and pos < len(self.atchain)-1:
					move['follows'].append({'id': 'attack'+ self.atchain[pos+1], 'input':'a1'})
			except ValueError:
				pass
				
	
	def changeOutputFormat(self):
		mode = self.formatCB.currentIndex()
		settings.set_option('command_list/output_format', mode)

	def clearComment(self, line):
		parts = re.split('#', line)
		line = parts[0]
		if line[-1] == ' ':
			line = line[0:-1]
		return line
	
	def clearLine(self, line):
		line = self.clearComment(line)
		while line[0] == ' ' or line[0] == '	':
			line = line[1:]
		return line
		
	def processText(self):
		text = self.editor.toPlainText()
		data = text.split('\n')
		
		newText = self.processData(data)
		
		self.editor.clear()
		self.editor.appendPlainText(newText)
		
	def processFile(self):
		path = self.modelPath.text()
		if os.path.isfile(path):
			(start, extension) = os.path.splitext(path)
			shutil.copyfile(path, start + '_back' + extension)
			
			settings.set_option('command_list/file', path)
			
			f = open(path, 'r')
			data = f.readlines()
			
			newText = self.processData(data, True)
			
			self.editor.clear()
			if(PLAIN_TEXT):
				self.editor.appendPlainText(newText)
			else:
				self.editor.setHtml('<pre>' + newText + '</pre>')

			#f = open(start + '_new' + extension, 'w')
			#f.write(newText)
			f.close()
			print('SAVED')
	
	def retrieveBreak(self):
		path = settings.get_option('general/data_path', '') + os.sep + 'scripts/cancel.c'
		#path = '/home/piccolo/workspace/OpenBOR/data/scripts/cancel.c'
		if not os.path.isfile(path): return []
		f = open(path, 'rU')
		data = f.readlines()
		currentNameMask = re.compile('(.*)"' + self.modelName + '"(.*)')
		animMask =  re.compile('(.*)return openborconstant\((.*)')
		vNameMask = re.compile('(.*)vName(.*)')
		
		follows = []
		self.inBlockOfInterest = False
		
		for line in data:
			
			if currentNameMask.match(line) != None:
				self.inBlockOfInterest = True
			elif self.inBlockOfInterest and animMask.match(line) != None:
				inputStart = line.find('(') + 1
				inputEnd = line.find(')')
				animStart = line.rfind('openborconstant')
				anim = re.split('"', line[animStart:])[1]
				input = line[inputStart : inputEnd]
				inputParts = re.split(' ', input)
				

				trueInputParts = []
				currentPart = None
				for part in inputParts:
					if part.count('"') == 1 :
						if currentPart is None: # Opening quote
							currentPart = part
						else: # Closing quote
							currentPart += ' ' + part
							trueInputParts.append(currentPart)
							currentPart = None
					elif currentPart is not None: # In between two lonely quotes
						currentPart += ' ' + part
					else: # Opening and closing quote in one part
						currentPart = None
						trueInputParts.append(part)
				if(currentPart is not None): trueInputParts.append(currentPart)
						
				startCode = ''
				endCode = ''
				processing = ''
				operator = ''
				for part in trueInputParts:
					if part == 'mainCode' or part == 'code':
						processing = part
					elif part == '==':
						operator = part
					elif part == '!=':
						operator = part
					else:
						if(processing == "mainCode"):
							endCode += part
						else: 
							if(operator == '!=' and part.count(' ') == 1): # e.g., T a1 : ok ; T D a1 : not ok
								subParts = re.split(' ', part)
								startCode += 'ad ' + subParts[-1]
							else:
								startCode += part
				
				if(startCode != '' and endCode != ''):
					code = startCode
				else:
					code = startCode + endCode
				print (str(trueInputParts))
				code = code.replace('"', '')
				if(code[0:2] == 'T ') : code = code[2:]
				
				if(len(anim) < 30 and len(code) < 20):
					follow = {'input':code, "id":anim[4:].lower()}
					follows.append(follow)
				
				print( code + ' ' + anim)
			elif self.inBlockOfInterest and vNameMask.match(line) != None:
				break
		follows.append({'input':'a4 s', 'id':'freespecial1'})
		print (follows)
		return follows
			
		
	def processData(self, data, lineBreakTrick=False):
		USE_INT_IDS = True
		mode = self.formatCB.currentIndex()
		if mode == 0:
			mode = 'show-html'
		elif mode == 1:
			mode = 'html'
		elif mode == 2:
			mode = 'game-script'
		elif mode == 3:
			mode = 'game-script'
			USE_INT_IDS = False
		
		p = re.compile('^([ \s]*)anim([ \s]+)(.*)')
		nameMask = re.compile('^([ \s]*)name( |	)(.*)')
		atchainMask = re.compile('^([ \s]*)atchain(.*)')
		attackboxMask = re.compile('^([ \s]*)attack(\d*)( |	)(.*)')
		holdMask = re.compile('^([ \s]*)aniHoldSwitch(.*)')
		followMask = re.compile('^([ \s]*)followanim(.*)')
		cancelMask = re.compile('^([ \s]*)cancel(.*)')
		#dCancelMask = re.compile('^([ \s]*)set\(data, "(.*)ANI_(.*)')
		dCancelMask = re.compile('^([ \s]*)addCancel\(data, "(.*)ANI_(.*)')
		comMask = re.compile('^([ \s]*)com([ \s]+)(.*)')
		frameMask = re.compile('^([ \s]*)frame([ \s]+)(.*)')
		i = 0
		
		self.atchain = []
		moveData = {}
		baseMoves = {}
		orderedMoves = []
		
		for line in data:
			line = line.rstrip('\r\n')
			c = 0
			i += 1
			if p.match(line) != None:
				#print('match', line)
				
				currentMove = {}
				parts = re.split('#', line)
				label = None
				try:
					if(len(parts) > 1):
						label = parts[1]
				except IndexError:
					pass
				
				firstPart = ' '.join(parts[0].split())
				parts = re.split(' |	', firstPart)
				currentMove['id'] = parts[1].lower()
				print('match', parts[1].lower())

				if(label is None):
					currentMove['label'] = currentMove['id']
				else:
					currentMove['label'] = label
					
				currentMove['follows'] = []
				currentMove['frames'] = []
				currentMove['damage'] = []
				
				if currentMove['id'] == 'special':
					currentMove['follows'] = self.retrieveBreak()
				
				self.addChainFollow(currentMove)
				
				moveData[currentMove['id']] = currentMove

			elif attackboxMask.match(line) != None:
				line = self.clearLine(line)
				print( line)
				parts = re.split(' |	', line)
				if parts[1] != '0':
					currentMove['damage'].append(parts[5])
					#currentMove['power'] = parts[6]
			elif holdMask.match(line) != None:
				parts = re.split('"', line)
				aniID = parts[1].split('_')[1].lower()
				com = 'h'#parts[2]
				follow = {'input':com, 'id': aniID}
				currentMove['follows'].append(follow)
				
			elif cancelMask.match(line) != None:
				line = self.clearLine(line)
				parts = re.split(' |	', line)
				print( parts)
				if(parts[-2].lower() == 'a'): parts[-2] = 'a1'
					
				com = ' '.join(parts[4:-1]).lower()
				aniID = parts[-1].lower()
				follow = {'input':com, 'id': aniID}
				currentMove['follows'].append(follow)
				
			elif dCancelMask.match(line) != None:
				parts = re.split('"', line)
				aniID = parts[3].split('_')[1].lower()
				follow = {'input':parts[1], 'id': aniID}
				currentMove['follows'].append(follow)
			elif followMask.match(line) != None:
				parts = re.split(' |	', line)
				aniID = 'follow' + parts[-1]
				com = 'fl'
				follow = {'input':com, 'id': aniID}
				currentMove['follows'].append(follow)
				
			elif comMask.match(line) != None:
				parts = re.split('#', line)
				line = parts[0]
				if line[-1] == ' ':
					line = line[0:-1]
					
				line = ' '.join(line.split())
				parts = re.split(' |	', line)
				if(parts[-2].lower() == 'a'): parts[-2] = 'a1'
				com = ' '.join(parts[1:-1]).lower()
				aniID = parts[-1].lower()
				baseMoves[aniID] = com
				orderedMoves.append(aniID)
			elif frameMask.match(line) != None:
				parts = re.split(' |	', line)
				framePath = parts[-1]
				currentMove['frames'].append(framePath)
				if(currentMove['id'] == 'follow4'):
					print( framePath)
			elif atchainMask.match(line) != None:
				line = ' '.join(line.split())
				self.atchain = re.split(' |	', line)[1:]
				
				print("self.atchain", self.atchain)
				baseMoves['attack' + self.atchain[0]] = 'a1'
				orderedMoves.append('attack' + self.atchain[0])
			elif nameMask.match(line) != None:
				parts = re.split(' |	', line)
				print( parts)
				self.modelName = parts[-1]
		
		if len(self.atchain) == 0:
			self.atchain = [1,]
			baseMoves['attack1'] = 'a1'
			orderedMoves.insert(0, 'attack1')
			#orderedMoves.prepend('attack1')
		
		if("special" in orderedMoves):
			
			baseMoves["special"] = "s"
		#orderedMoves.append("special")
		
		print(orderedMoves)
		
		def getMoveString(move):
			basePath = os.path.dirname(settings.get_option('general/data_path', '')) +  '/';
			try:
				frames = move['frames']
				framePath = frames[int(len(frames)/2)]
				filename = os.path.basename(framePath)
				destDir = '/srv/http/misc/bb/' + self.modelName.lower()

				try:
					os.makedirs(destDir)
				except OSError:
					pass
			
				try:
					shutil.copy(basePath + framePath, destDir)
				except:
					pass
				
				framePath = destDir + os.sep + filename
			except IndexError:
				framePath = ''
				
			
			if(move['id'] in baseMoves):
				com = baseMoves[move['id']]
				text = '<div><span class="comInput">' + self.formatInput(com) + '</span> => '
			else:
				text = '<div><span class="comInput"></span> => '
			text += '<strong>' + move['label'] + '</strong></div>'
			text += '<div><img src="' + framePath + '" alt="' + move['label'] + '" />'
	
			for follow in move['follows']:
				orderedMoves.append(follow['id'])
				followInput = self.formatInput(follow['input'])
				text += '\n	' + followInput + ' => <a class="follow" href="#' + follow['id'] + '" input="' + followInput + '">' + moveData[follow['id']]['label'] + '</a>'
			text += '</div>'
			return text
		
		
		def getMoveCode(move):
			try:
				frames = move['frames']
				framePath = frames[len(frames)/2]
			except IndexError:
				framePath = 'data/chars/misc/empty.gif'
				
			if(USE_INT_IDS) :
				ani = 'openborconstant("ANI_' + move['id'] + '")'
				text = '''\n	if(aniID == openborconstant("ANI_''' + move['id'] + '''")){'''
			else :
				ani = '"' + move['id'] + '"'
				text = '''\ncase "''' + move['id'] + '''":'''
			text += '''\n		move = array(0);
				set(move, "ani", ''' + ani + ''');
				set(move, "label", "''' + move['label'] + '''");
				set(move, "sprite", "''' + framePath + '''");
				set(move, "damage", "''' + ', '.join(move['damage']) + '''");
				moveFollows = array(''' + str(len(move['follows'])) + ''');'''
			
			j = 0
			for follow in move['follows']:
				orderedMoves.append(follow['id'])
				print( move)
				print (follow)
				followInput = self.formatInput(follow['input'], 'script')
				if(USE_INT_IDS) : ani = 'openborconstant("ANI_' + follow['id'] + '")'
				else : ani = '"' + follow['id'] + '"'
				text += '''follow = array(2);
				set(follow, "command", "''' + followInput + '''");
				set(follow, "ani", ''' + ani + ''');
				set(follow, "label", "''' + moveData[follow['id']]['label'] + '''");
				set(moveFollows, ''' + str(j) + ''', follow);'''
				j+= 1
				
			text += '''set(move, "follows", moveFollows);'''
			
			text += '''return move;'''
			if(USE_INT_IDS) : text += '}'
			else : text += 'break;'
			#set(moveData, "''' + move['id'] + '''", move);\n'''
			return text
		

		exclude = ['walk', 'idle', 'run', 'waiting', 'select', 'pain', 'pain2', 'fall', 'rise', 'get', 'jumpdelay']
		prefixText = ''
		newText = ''
		if(mode != 'game-script'): newText += '<h2>Initial attacks :</h2>'
		#for com in baseMoves.iterkeys():
			#aniID = baseMoves[com]
			#newText += '<div id="' + aniID + '">'
			#newText += '\n\n' + self.formatInput(com) + ' => ' + getMoveString(moveData[aniID])
			#newText += '</div>'
			#exclude.append(aniID)
		
		#for aniID in moveData:
		
		if(mode == 'game-script'):
			initialMove = {'id':'idle', 'label':'Initial', 'follows':[], 'damage':[], 'frames':moveData['idle']['frames']} # Represent a non existing move (~ idle)
			i = 0
			
			while(i < len(orderedMoves)):
				aniID = orderedMoves[i]
				if aniID not in exclude:
					move = moveData[aniID]
					
					if aniID in baseMoves:
						com = baseMoves[move['id']]
						initialMove['follows'].append({'input':com, 'id':aniID})
					newText += getMoveCode(move)
					
					exclude.append(aniID)
				i+= 1
			
			if(not USE_INT_IDS) : newText += '} '
			newText += 'return NULL();'
			
			
			prefixText += '''void main(){
	int aniID = getindexedvar("moveList_aniID");
	setindexedvar("moveList_data", ''' + self.modelName.lower() + '''(aniID));

}
			
			
'''
			prefixText += 'void ' + self.modelName.lower() + '(char aniID){\n'
			prefixText += '	void moveFollows, move, follow;'
			if(not USE_INT_IDS) : prefixText += ' switch(aniID){'
			prefixText += getMoveCode(initialMove)

			newText = prefixText + newText + '\n}'
				
		else: # HTML 
			i = 0
			while(i < len(orderedMoves)):
				aniID = orderedMoves[i]
				if aniID not in exclude:
					move = moveData[aniID]
					if aniID in baseMoves:
						classes = "move base"
						newText += '<div class="comboString" level="1">'
					else:
						classes = "move"
					newText += '<div class="' + classes + '" id="' + aniID + '">'
					newText += '\n\n' + getMoveString(move)
					newText += '</div>'
					
					if aniID in baseMoves:
						newText += '</div>'
					exclude.append(aniID)
				i+= 1
				
			
		return newText
		

	def formatInput(self, input, type='HTML'):
		print( 'formating ' + input)
		if(type == 'HTML'):
			corresp = {'a1':'P', 'a2':'K', 'a3':'S', 'a4':'G', 's':'Br', 'j':'J', 'h':'Hold', 'b':'back', 'f':'&#x2192;', 'd':'&#x2193;', 'u':'&#x2191;', 'fl':'follow', 'ad':'Any direction'}
		else:
			corresp = {'a1':'P', 'a2':'K', 'a3':'S', 'a4':'G', 's':'Br', 'j':'J', 'h':'H', 'b':'b', 'f':'f', 'd':'d', 'u':'u', 'fl':'fl', 'ad':'m'}
		parts = input.split(' ')
		
		formatedInput = ''
		if(len(parts) > 1):
			for part in parts[0:-1]:
				formatedInput += corresp[part.lower()]
				if(type == "HTML") : formatedInput += ' + '
				else : formatedInput += ' '
			input = parts[-1]
			
		formatedInput += corresp[input]
		
		return formatedInput
		