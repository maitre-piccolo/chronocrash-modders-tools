from configparser import (
    RawConfigParser,
    NoSectionError,
    NoOptionError
)




class Theme(RawConfigParser):
	def __init__(self, name, path):
		self.name = name
		RawConfigParser.__init__(self, delimiters=('='))
		
		self.optionxform = str # Case sensitive key
		self.read(path)


EDITOR_THEME = Theme('Solarized (dark)', 'themes/editor/Solarized (dark).txt')
#EDITOR_THEME = Theme('Normal', 'themes/editor/Normal.txt')


def setEditorTheme(name):
	global EDITOR_THEME
	EDITOR_THEME = Theme(name, 'themes/editor/' + name + '.txt')