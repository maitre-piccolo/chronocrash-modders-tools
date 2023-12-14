import os

path = '/run/media/piccolo/015AF545360D8260/DATA/openbor-utils'

def checkPath(path):
	for f in os.listdir(path):
		if(os.path.isdir(os.path.join(path, f))):
			checkPath(os.path.join(path, f))
		else:
			# if(f.startswith('.') and f.endswith('.1')):
			if(f.startswith('.')):
				# os.remove(os.path.join(path, f))
				print(f)
		

checkPath(path)
