from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtCore import QBuffer, QIODevice
from PyQt5.QtGui import QImage, QPixmap, qRgba, QColor
import os
from common import settings, xdg
import PIL.Image
# from PIL import ImageQt
#from PIL import Image

FORCE_TRANSPARENCY = False
USE_PIL = True

CHECK_MISSING_EXTENSION = False

qt_version = "6"


def align8to32(bytes, width, mode):
    """
    converts each scanline of data from 8 bit to 32 bit aligned
    """

    bits_per_pixel = {"1": 1, "L": 8, "P": 8, "I;16": 16}[mode]

    # calculate bytes per line and the extra padding if needed
    bits_per_line = bits_per_pixel * width
    full_bytes_per_line, remaining_bits_per_line = divmod(bits_per_line, 8)
    bytes_per_line = full_bytes_per_line + (1 if remaining_bits_per_line else 0)

    extra_padding = -bytes_per_line % 4

    # already 32 bit aligned by luck
    if not extra_padding:
        return bytes

    new_data = []
    for i in range(len(bytes) // bytes_per_line):
        new_data.append(
            bytes[i * bytes_per_line : (i + 1) * bytes_per_line]
            + b"\x00" * extra_padding
        )

    return b"".join(new_data)

def rgb(r, g, b, a=255):
    """(Internal) Turns an RGB color into a Qt compatible color integer."""
    # use qRgb to pack the colors, and then turn the resulting long
    # into a negative integer with the same bitpattern.
    return qRgba(r, g, b, a) & 0xFFFFFFFF

def _toqclass_helper(im):
    data = None
    colortable = None
    exclusive_fp = False

    # handle filename, if given instead of image name
    if hasattr(im, "toUtf8"):
        # FIXME - is this really the best way to do this?
        im = str(im.toUtf8(), "utf-8")
    # if is_path(im):
    #     im = Image.open(im)
    #     exclusive_fp = True

    qt_format = QImage.Format if qt_version == "6" else QImage
    if im.mode == "1":
        format = qt_format.Format_Mono
    elif im.mode == "L":
        format = qt_format.Format_Indexed8
        colortable = []
        for i in range(256):
            colortable.append(rgb(i, i, i))
    elif im.mode == "P":
        format = qt_format.Format_Indexed8
        colortable = []
        palette = im.getpalette()
        for i in range(0, len(palette), 3):
            colortable.append(rgb(*palette[i : i + 3]))
    elif im.mode == "RGB":
        # Populate the 4th channel with 255
        im = im.convert("RGBA")

        data = im.tobytes("raw", "BGRA")
        format = qt_format.Format_RGB32
    elif im.mode == "RGBA":
        data = im.tobytes("raw", "BGRA")
        format = qt_format.Format_ARGB32
    elif im.mode == "I;16" and hasattr(qt_format, "Format_Grayscale16"):  # Qt 5.13+
        im = im.point(lambda i: i * 256)

        format = qt_format.Format_Grayscale16
    else:
        if exclusive_fp:
            im.close()
        msg = f"unsupported image mode {repr(im.mode)}"
        raise ValueError(msg)

    size = im.size
    __data = data or align8to32(im.tobytes(), size[0], im.mode)
    if exclusive_fp:
        im.close()
    return {"data": __data, "size": size, "format": format, "colortable": colortable}


class ImageQt(QtGui.QImage):
	def __init__(self, im):
		"""
		An PIL image wrapper for Qt.  This is a subclass of PyQt's QImage
		class.

		:param im: A PIL Image object, or a file name (given either as
		Python string or a PyQt string object).
		"""
		im_data = _toqclass_helper(im)
		# must keep a reference, or Qt will crash!
		# All QImage constructors that take data operate on an existing
		# buffer, so this buffer has to hang on for the life of the image.
		# Fixes https://github.com/python-pillow/Pillow/issues/1370
		self.__data = im_data["data"]
		super().__init__(
		self.__data,
		im_data["size"][0],
		im_data["size"][1],
		im_data["format"],
		)
		if im_data["colortable"]:
			self.setColorTable(im_data["colortable"])



class FileInput(QtWidgets.QWidget):
	
	changed = QtCore.pyqtSignal()
	
	def __init__(self, parent, mode='openFile', default='', title=None, lookFolder=None, filters=None):
		QtWidgets.QWidget.__init__(self, parent)
		self.parent = parent
		self.textEdit = QtWidgets.QLineEdit()
		self.textEdit.setText(default)
		
		button = QtWidgets.QPushButton('...')
			
		button.clicked.connect(self.setPath)
		
		self.textEdit.textChanged.connect(self.changeOccured)
		
		l = QtWidgets.QHBoxLayout()
		self.setLayout(l)
		l.addWidget(self.textEdit, 1)
		l.addWidget(button, 0)
		
		self.mode = mode
		self.lookFolder = lookFolder
		self.title = title
		self.filters = filters
		
		l.setContentsMargins(0,0,0,0)
		
	def clear(self):
		self.textEdit.clear()
		
	def changeOccured(self, *args):
		self.changed.emit()
		
	def text(self):
		return self.textEdit.text()
	
	def setText(self, text):
		self.textEdit.setText(text)
	
	def setPath(self):
		if(self.mode == 'openFile'):
			path = QtWidgets.QFileDialog.getOpenFileName(self, _(self.title), self.lookFolder, self.tr(self.filters))[0]
		elif(self.mode == 'saveFile'):
			path = QtWidgets.QFileDialog.getSaveFileName(self, directory=self.lookFolder)[0]
		elif(self.mode == 'folder' or self.mode == 'directory'):
			path = QtWidgets.QFileDialog.getExistingDirectory(self, _(self.title), self.lookFolder)
		self.textEdit.setText(path)
	
	
'''
	Qt can't show .pcx
	This function return path if not .pcx
	Or converted path (png path) if .pcx.
'''
def getSpriteShowingPath(path):
	mainPath, extension = os.path.splitext(path)
	if extension == '.pcx':
		imagesDir = os.path.join(xdg.get_data_home(), 'images')
		mainPath = mainPath.replace('/', '')
		mainPath = mainPath.replace('\\', '')
		mainPath = mainPath.replace(':', '')
		newPath = imagesDir + os.sep + mainPath + '.png'
		
		if not os.path.isfile(newPath):
			im = PIL.Image.open(path)
			im.save(newPath)
		path = newPath
	return path
	

	
def loadSprite(path, transp=0, options={}):
	
	# print('transp', transp)
	
	#print("load sprite", path)
	path = getSpriteShowingPath(path)
	
	if(CHECK_MISSING_EXTENSION):
		dirName = os.path.dirname(path)
		baseName = os.path.basename(path)
		if('.' not in baseName):
			newPath = os.path.join(dirName, baseName + '.png')
			if(os.path.isfile(newPath)):
				path = newPath
				
			else:
				newPath = os.path.join(dirName, baseName + '.gif')
				if(os.path.isfile(newPath)):
					path = newPath
			
	
	if(USE_PIL):
	
		if(not os.path.isfile(path)):
			return QImage()
		
		image = ImageQt(PIL.Image.open(path))
		
	else:


		image = QtGui.QImage(path)
	#print('BITPLANE', image.bitPlaneCount())
	# if('idle.gif' in path): print('\n\nframe', image.bitPlaneCount(), len(image.colorTable()))
	
	# image = image.createMaskFromColor(image.color(0), QtCore.Qt.MaskOutColor)
	
	#print('image.bitPlaneCount()', image.bitPlaneCount())
	
	
	
	
	
	
	if( image.bitPlaneCount() < 32 or len(image.colorTable()) != 0):
		
		
		
		transp = int(transp)
		

		#print('colorTable', image.colorTable())
		image = image.convertToFormat(QtGui.QImage.Format_Indexed8)
		table = image.colorTable()
		
		if(transp < 0):
			transp = len(table)+transp
		# if('idle.gif' in path): print('\n\ncolorCount', image.colorCount())
		# if('idle.gif' in path) : print('FIRST COLOR', table[0])
		image.setColor(transp, QtGui.qRgba(255, 255, 255, 0))
		#image.setColor(1, QtGui.qRgba(255, 255, 255, 0))
		#image.setColor(len(table)-1, QtGui.qRgba(255, 255, 255, 0))
		#for i in range(len(table)):
			#image.setColor(i, QtGui.qRgba(255, 255, 255, 0))
	# image = image.createMaskFromColor(image.color(0), QtCore.Qt.MaskOutColor)
	# image.setColor(0, QtGui.qRgba(255, 255, 255, 0))
	elif(FORCE_TRANSPARENCY):
		#print('here', path)
		transColor = image.pixelColor(0,0)
		# image = image.createMaskFromColor(transColor.value(), QtCore.Qt.MaskOutColor)
		for y in range (image.height()):
			for x in range(image.width()):
				if image.pixelColor(x,y) == transColor:
				# color.setAlpha(image.pixelColor(x,y).alpha())
					image.setPixelColor(x,y,QtGui.QColor(255, 0, 0, 0))
 
	# pixmap = QPixmap::fromImage(tmp);
	
	
	if('colorTable' in options):
		image.setColorTable(options['colorTable'])
	
	return image





# act_file = "1.act"
# act_file = "valis_base_0.ACT"

def loadACTPalette(act_file):
        from codecs import encode
        with open(act_file, 'rb') as act:
            raw_data = act.read()                           # Read binary data
        hex_data = encode(raw_data, 'hex')                  # Convert it to hexadecimal values
        total_colors_count = (int(hex_data[-7:-4], 16))     # Get last 3 digits to get number of colors total
        misterious_count = (int(hex_data[-4:-3], 16))       # I have no idea what does it do
        colors_count = (int(hex_data[-3:], 16))             # Get last 3 digits to get number of nontransparent colors

        if(total_colors_count == 0):
                total_colors_count = 255
        # Decode colors from hex to string and split it by 6 (because colors are #1c1c1c)               
        colors = [hex_data[i:i+6].decode() for i in range(0, total_colors_count*6, 6)]

        # Add # to each item and filter empty items if there is a corrupted total_colors_count bit        
        colors = ['#'+i for i in colors if len(i)]
        
        true_colors = []
        for c in colors:
                qColor = QtGui.QColor(c)
                true_colors.append(qColor.rgb())
                
        true_colors[0] = QtGui.qRgba(255, 255, 255, 0)

        # return colors, total_colors_count
        return true_colors
