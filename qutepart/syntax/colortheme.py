"""Default color theme
"""

THEME_DESCR = None

class ColorTheme:
	"""Color theme.
	"""
	def __init__(self, textFormatClass):
		"""Constructor gets TextFormat class as parameter for avoid cross-import problems
		"""
		self.buildFormat(textFormatClass)

	def getFormat(self, styleName):
		"""Returns TextFormat for particular style
		"""
		return self.format[styleName]
	@staticmethod
	def setThemeDescr(mainDic, subDic={}):
		
		for key, stringParams in subDic.items():
			params = stringParams.split(',')
			if params[0] != 1:
				mainDic[key] = stringParams
		
		global THEME_DESCR
		THEME_DESCR = mainDic

	def buildFormat(self, textFormatClass):
		if THEME_DESCR is not None:
			defaultColor = '#000000'
			defaultBackground = '#ffffff'
			defaultSelectionColor = '#0000ff'
			dic = {}

			styles = {'Special Character':'SpecialChar', 'Built-in':'BuilIn', 'Comment Variable':'CommentVar', 'Floating Point':'FLoat',
		'Data Type': 'DataType', 'Base-N Integer':'BaseN'}

			for name, params in THEME_DESCR.items():

				
				if name in styles:
					name = styles[name]
				name = name.replace(' ', '')
				params = params.split(',')
				
				background = defaultBackground
				if params[6] not in ('-', '') : background = '#' + params[6]
				#print('***  bk   ***', background)
				

				colr = '#' + params[0]
				dic['ds' + name] = textFormatClass(color=colr, bold=bool(params[2]), background=background)
			self.format = dic
		else :
			self.format = {
			'dsNormal':         textFormatClass(),
			'dsKeyword':        textFormatClass(bold=True),
			'dsFunction':       textFormatClass(color='#644a9a'),
			'dsVariable':       textFormatClass(color='#0057ad'),
			'dsControlFlow':    textFormatClass(bold=True),
			'dsOperator':       textFormatClass(),
			'dsBuiltIn':        textFormatClass(color='#644a9a', bold=True),
			'dsExtension':      textFormatClass(color='#0094fe', bold=True),
			'dsPreprocessor':   textFormatClass(color='#006e28'),
			'dsAttribute':      textFormatClass(color='#0057ad'),

			'dsChar':           textFormatClass(color='#914c9c'),
			'dsSpecialChar':    textFormatClass(color='#3dade8'),
			'dsString':         textFormatClass(color='#be0303'),
			'dsVerbatimString': textFormatClass(color='#be0303'),
			'dsSpecialString':  textFormatClass(color='#fe5500'),
			'dsImport':         textFormatClass(color='#fe5500', bold=True),

			'dsDataType':       textFormatClass(color='#0057ad'),
			'dsDecVal':         textFormatClass(color='#af8000'),
			'dsBaseN':          textFormatClass(color='#af8000'),
			'dsFloat':          textFormatClass(color='#af8000'),

			'dsConstant':       textFormatClass(bold=True),

			'dsComment':        textFormatClass(color='#888786'),
			'dsDocumentation':  textFormatClass(color='#608880'),
			'dsAnnotation':     textFormatClass(color='#0094fe'),
			'dsCommentVar':     textFormatClass(color='#c960c9'),

			'dsRegionMarker':   textFormatClass(color='#0057ad', background='#e0e9f8'),
			'dsInformation':    textFormatClass(color='#af8000'),
			'dsWarning':        textFormatClass(color='#be0303'),
			'dsAlert':          textFormatClass(color='#bf0303', background='#f7e6e6', bold=True),
			'dsOthers':         textFormatClass(color='#006e28'),
			'dsError':          textFormatClass(color='#bf0303', underline=True),
			}
