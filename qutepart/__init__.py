"""qutepart --- Code editor component for PyQt and Pyside
=========================================================
"""

import threading
from functools import wraps


def threaded(f):
	"""
		A decorator that will make any function run in a new thread
	"""
	@wraps(f)
	def wrapper(*args, **kwargs):
		t = threading.Thread(target=f, args=args, kwargs=kwargs)
		#t = multiprocessing.Process(target = func, args = args, kwargs = kwargs)
		t.setDaemon(True)
		t.start()
		
	return wrapper

import sys
import os.path
import logging
import platform

from PyQt5 import QtGui

from PyQt5.QtCore import QRect, Qt, pyqtSignal, QRegExp, QSignalBlocker, QEvent, QMimeData
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QPlainTextEdit, QTextEdit, QToolTip
from PyQt5.QtPrintSupport import QPrintDialog
from PyQt5.QtGui import QColor, QBrush, \
                        QFont, \
                        QIcon, QKeySequence, QPainter, QPen, QPalette, \
                        QTextCharFormat, QTextCursor, \
                        QTextBlock, QTextFormat, QDropEvent

from qutepart.syntax import SyntaxManager

if 'sphinx-build' not in sys.argv[0]:
    # See explanation near `import sip` above
    from qutepart.syntaxhlighter import SyntaxHighlighter
    from qutepart.brackethlighter import BracketHighlighter
    from qutepart.completer import Completer
    from qutepart.lines import Lines
    from qutepart.rectangularselection import RectangularSelection
    import qutepart.sideareas
    from qutepart.indenter import Indenter
    import qutepart.vim
    import qutepart.bookmarks

    def setPositionInBlock(cursor, positionInBlock, anchor=QTextCursor.MoveAnchor):
        return cursor.setPosition(cursor.block().position() + positionInBlock, anchor)



VERSION = (2, 2, 3)


logger = logging.getLogger('qutepart')
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter("qutepart: %(message)s"))
logger.addHandler(consoleHandler)

logger.setLevel(logging.ERROR)


# After logging setup
import qutepart.syntax.loader
binaryParserAvailable = qutepart.syntax.loader.binaryParserAvailable


_ICONS_PATH = os.path.join(os.path.dirname(__file__), 'icons')

def getIconPath(iconFileName):
    return os.path.join(_ICONS_PATH, iconFileName)


#Define for old Qt versions methods, which appeared in 4.7
if not hasattr(QTextCursor, 'positionInBlock'):
    def _positionInBlock(cursor):
        return cursor.position() - cursor.block().position()
    QTextCursor.positionInBlock = _positionInBlock



	

class Qutepart(QPlainTextEdit):
    '''Qutepart is based on QPlainTextEdit, and you can use QPlainTextEdit methods,
    if you don't see some functionality here.

    **Text**

    ``text`` attribute holds current text. It may be read and written.::

        qpart.text = readFile()
        saveFile(qpart.text)

    This attribute always returns text, separated with ``\\n``. Use ``textForSaving()`` for get original text.

    It is recommended to use ``lines`` attribute whenever possible,
    because access to ``text`` might require long time on big files.
    Attribute is cached, only first read access after text has been changed in slow.

    **Selected text**

    ``selectedText`` attribute holds selected text. It may be read and written.
    Write operation replaces selection with new text. If nothing is selected - just inserts text::

        print qpart.selectedText  # print selection
        qpart.selectedText = 'new text'  # replace selection

    **Text lines**

    ``lines`` attribute, which represents text as list-of-strings like object
    and allows to modify it. Examples::

        qpart.lines[0]  # get the first line of the text
        qpart.lines[-1]  # get the last line of the text
        qpart.lines[2] = 'new text'  # replace 3rd line value with 'new text'
        qpart.lines[1:4]  # get 3 lines of text starting from the second line as list of strings
        qpart.lines[1:4] = ['new line 2', 'new line3', 'new line 4']  # replace value of 3 lines
        del qpart.lines[3]  # delete 4th line
        del qpart.lines[3:5]  # delete lines 4, 5, 6

        len(qpart.lines)  # get line count

        qpart.lines.append('new line')  # append new line to the end
        qpart.lines.insert(1, 'new line')  # insert new line before line 1

        print qpart.lines  # print all text as list of strings

        # iterate over lines.
        for lineText in qpart.lines:
            doSomething(lineText)

        qpart.lines = ['one', 'thow', 'three']  # replace whole text

    **Position and selection**

    * ``cursorPosition`` - cursor position as ``(line, column)``. Lines are numerated from zero. If column is set to ``None`` - cursor will be placed before first non-whitespace character. If line or column is bigger, than actual file, cursor will be placed to the last line, to the last column
    * ``absCursorPosition`` - cursor position as offset from the beginning of text.
    * ``selectedPosition`` - selection coordinates as ``((startLine, startCol), (cursorLine, cursorCol))``.
    * ``absSelectedPosition`` - selection coordinates as ``(startPosition, cursorPosition)`` where position is offset from the beginning of text.
    Rectangular selection is not available via API currently.

    **EOL, indentation, edge**

    * ``eol`` - End Of Line character. Supported values are ``\\n``, ``\\r``, ``\\r\\n``. See comments for ``textForSaving()``
    * ``indentWidth`` - Width of ``Tab`` character, and width of one indentation level. Default is ``4``.
    * ``indentUseTabs`` - If True, ``Tab`` character inserts ``\\t``, otherwise - spaces. Default is ``False``.
    * ``lineLengthEdge`` - If not ``None`` - maximal allowed line width (i.e. 80 chars). Longer lines are marked with red (see ``lineLengthEdgeColor``) line. Default is ``None``.
    * ``lineLengthEdgeColor`` - Color of line length edge line. Default is red.

    **Visible white spaces**

    * ``drawIncorrectIndentation`` - Draw trailing whitespaces, tabs if text is indented with spaces, spaces if text is indented with tabs. Default is ``True``. Doesn't have any effect if ``drawAnyWhitespace`` is ``True``.
    * ``drawAnyWhitespace`` - Draw trailing and other whitespaces, used as indentation. Default is ``False``.

    **Autocompletion**

    Qutepart supports autocompletion, based on document contents.
    It is enabled, if ``completionEnabled`` is ``True``.
    ``completionThreshold`` is count of typed symbols, after which completion is shown.

    **Linters support**

    * ``lintMarks`` Linter messages as {lineNumber: (type, text)} dictionary. Cleared on any edit operation. Type is one of `Qutepart.LINT_ERROR, Qutepart.LINT_WARNING, Qutepart.LINT_NOTE)

    **Vim mode**

    ``vimModeEnabled`` - read-write property switches Vim mode. See also ``vimModeEnabledChanged``.
    ``vimModeIndication`` - An application shall display a label, which shows current Vim mode. This read-only property contains (QColor, str) to be displayed on the label. See also ``vimModeIndicationChanged``.

    **Actions**

    Component contains list of actions (QAction instances).
    Actions can be insered to some menu, a shortcut and an icon can be configured.

    Bookmarks:

    * ``toggleBookmarkAction`` - Set/Clear bookmark on current block
    * ``nextBookmarkAction`` - Jump to next bookmark
    * ``prevBookmarkAction`` - Jump to previous bookmark

    Scroll:

    * ``scrollUpAction`` - Scroll viewport Up
    * ``scrollDownAction`` - Scroll viewport Down
    * ``selectAndScrollUpAction`` - Select 1 line Up and scroll
    * ``selectAndScrollDownAction`` - Select 1 line Down and scroll

    Indentation:

    * ``increaseIndentAction`` - Increase indentation by 1 level
    * ``decreaseIndentAction`` - Decrease indentation by 1 level
    * ``autoIndentLineAction`` - Autoindent line
    * ``indentWithSpaceAction`` - Indent all selected lines by 1 space symbol
    * ``unIndentWithSpaceAction`` - Unindent all selected lines by 1 space symbol

    Lines:

    * ``moveLineUpAction`` - Move line Up
    * ``moveLineDownAction`` - Move line Down
    * ``deleteLineAction`` - Delete line
    * ``copyLineAction`` - Copy line
    * ``pasteLineAction`` - Paste line
    * ``cutLineAction`` - Cut line
    * ``duplicateLineAction`` - Duplicate line

    Other:
    * ``undoAction`` - Undo
    * ``redoAction`` - Redo
    * ``invokeCompletionAction`` - Invoke completion
    * ``printAction`` - Print file

    **Text modification and Undo/Redo**

    Sometimes, it is required to make few text modifications, which are Undo-Redoble as atomic operation.
    i.e. you want to indent (insert indentation) few lines of text, but user shall be able to
    Undo it in one step. In this case, you can use Qutepart as a context manager.::

        with qpart:
            qpart.modifySomeText()
            qpart.modifyOtherText()

    Nested atomic operations are joined in one operation

    **Signals**

    * ``userWarning(text)``` Warning, which shall be shown to the user on status bar. I.e. 'Rectangular selection area is too big'
    * ``languageChanged(langName)```              Language has changed. See also ``language()``
    * ``indentWidthChanged(int)``                 Indentation width changed. See also ``indentWidth``
    * ``indentUseTabsChanged(bool)``              Indentation uses tab property changed. See also ``indentUseTabs``
    * ``eolChanged(eol)``                         EOL mode changed. See also ``eol``.
    * ``vimModeEnabledChanged(enabled)            Vim mode has been enabled or disabled.
    * ``vimModeIndicationChanged(color, text)``   Vim mode changed. Parameters contain color and text to be displayed on an indicator. See also ``vimModeIndication``

    **Public methods**
    '''

    userWarning = pyqtSignal(str)
    languageChanged = pyqtSignal(str)
    syntaxLoaded = pyqtSignal(object)
    indentWidthChanged = pyqtSignal(int)
    indentUseTabsChanged = pyqtSignal(bool)
    eolChanged = pyqtSignal(str)
    vimModeIndicationChanged = pyqtSignal(QColor, str)
    vimModeEnabledChanged = pyqtSignal(bool)

    LINT_ERROR = 'e'
    LINT_WARNING = 'w'
    LINT_NOTE = 'n'

    _DEFAULT_EOL = '\n'

    _DEFAULT_COMPLETION_THRESHOLD = 3
    _DEFAULT_COMPLETION_ENABLED = True

    _globalSyntaxManager = SyntaxManager()
    entitySyntax = None

    def __init__(self, *args):
        QPlainTextEdit.__init__(self, *args)
        

        

        self.setAttribute(Qt.WA_KeyCompression, False)  # vim can't process compressed keys

        self._lastKeyPressProcessedByParent = False
        # toPlainText() takes a lot of time on long texts, therefore it is cached
        self._cachedText = None

        self._fontBackup = self.font()

        self._eol = self._DEFAULT_EOL
        self._indenter = Indenter(self)
        self.lineLengthEdge = None
        self.lineLengthEdgeColor = Qt.red
        self._atomicModificationDepth = 0

        self.drawIncorrectIndentation = True
        self.drawAnyWhitespace = False

        self._rectangularSelection = RectangularSelection(self)

        """Sometimes color themes will be supported.
        Now black on white is hardcoded in the highlighters.
        Hardcode same palette for not highlighted text
        """
        palette = self.palette()
        palette.setColor(QPalette.Base, QColor('#ffffff'))
        palette.setColor(QPalette.Text, QColor('#000000'))
        self.setPalette(palette)

        self._highlighter = None
        self._bracketHighlighter = BracketHighlighter()

        self._lines = Lines(self)

        self.completionThreshold = self._DEFAULT_COMPLETION_THRESHOLD
        self.completionEnabled = self._DEFAULT_COMPLETION_ENABLED
        self._completer = Completer(self)

        self._vim = None

        self._initActions()

        self._lineNumberArea = qutepart.sideareas.LineNumberArea(self)
        self._countCache = (-1, -1)
        self._markArea = qutepart.sideareas.MarkArea(self)

        self._bookmarks = qutepart.bookmarks.Bookmarks(self, self._markArea)

        self._nonVimExtraSelections = []
        self._userExtraSelections = []  # we draw bracket highlighting, current line and extra selections by user
        self._userExtraSelectionFormat = QTextCharFormat()
        self._userExtraSelectionFormat.setBackground(QBrush(QColor('#ffee00')))

        self._lintMarks = {}

        self.blockCountChanged.connect(self._updateLineNumberAreaWidth)
        self.updateRequest.connect(self._updateSideAreas)
        
        # WARNING why did I comment this line before ?
        self.cursorPositionChanged.connect(self._updateExtraSelections)
        
        self.textChanged.connect(self._dropUserExtraSelections)
        self.textChanged.connect(self._resetCachedText)
        self.textChanged.connect(self._clearLintMarks)

        fontFamilies = {'Windows':'Courier New',
                        'Darwin': 'Menlo'}
        fontFamily = fontFamilies.get(platform.system(), 'Monospace')
        self.setFont(QFont(fontFamily))

        self._updateLineNumberAreaWidth(0)
        self.overwriteHighlightColor = None
        self.highlightColor = QColor('#ffffa3')
        #self.highlightColor = QColor('#2CA2AE')
        
        self._updateExtraSelections()
        self.syntaxLoaded.connect(self.loadSyntax)
        
        
        if(settings.get_option('editor/scroll_instead_of_wrap', False)):
	        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap);
        

    def terminate(self):
        """ Terminate Qutepart instance.
        This method MUST be called before application stop to avoid crashes and
        some other interesting effects
        Call it on close to free memory and stop background highlighting
        """
        self.text = ''
        self._completer.terminate()

        if self._highlighter is not None:
            self._highlighter.terminate()

        if self._vim is not None:
            self._vim.terminate()

    def _initActions(self):
        """Init shortcuts for text editing
        """

        def createAction(text, shortcut, slot, iconFileName=None):
            """Create QAction with given parameters and add to the widget
            """
            action = QAction(text, self)
            if iconFileName is not None:
                action.setIcon(QIcon(getIconPath(iconFileName)))

            keySeq = shortcut if isinstance(shortcut, QKeySequence) else QKeySequence(shortcut)
            action.setShortcut(keySeq)
            action.setShortcutContext(Qt.WidgetShortcut)
            action.triggered.connect(slot)

            self.addAction(action)

            return action

        # scrolling
        self.scrollUpAction = createAction('Scroll up', 'Ctrl+Up',
                                           lambda: self._onShortcutScroll(down = False),
                                           'up.png')
        self.scrollDownAction = createAction('Scroll down', 'Ctrl+Down',
                                             lambda: self._onShortcutScroll(down = True),
                                             'down.png')
        self.selectAndScrollUpAction = createAction('Select and scroll Up', 'Ctrl+Shift+Up',
                                                    lambda: self._onShortcutSelectAndScroll(down = False))
        self.selectAndScrollDownAction = createAction('Select and scroll Down', 'Ctrl+Shift+Down',
                                                      lambda: self._onShortcutSelectAndScroll(down = True))

        # indentation
        self.increaseIndentAction = createAction('Increase indentation', 'Tab',
                                                 self._onShortcutIndent,
                                                 'indent.png')
        self.decreaseIndentAction = createAction('Decrease indentation', 'Shift+Tab',
                            lambda: self._indenter.onChangeSelectedBlocksIndent(increase = False),
                            'unindent.png')
        self.autoIndentLineAction = createAction('Autoindent line', 'Ctrl+I',
                                                  self._indenter.onAutoIndentTriggered)
        self.indentWithSpaceAction = createAction('Indent with 1 space', 'Shift+Space',
                        lambda: self._indenter.onChangeSelectedBlocksIndent(increase=True,
                                                                              withSpace=True))
        self.unIndentWithSpaceAction = createAction('Unindent with 1 space', 'Shift+Backspace',
                            lambda: self._indenter.onChangeSelectedBlocksIndent(increase=False,
                                                                                  withSpace=True))

        # editing
        self.undoAction = createAction('Undo', QKeySequence.Undo,
                                       self.undo, 'undo.png')
        self.redoAction = createAction('Redo', QKeySequence.Redo,
                                       self.redo, 'redo.png')

        self.moveLineUpAction = createAction('Move line up', 'Alt+Up',
                                             lambda: self._onShortcutMoveLine(down = False), 'up.png')
        self.moveLineDownAction = createAction('Move line down', 'Alt+Down',
                                               lambda: self._onShortcutMoveLine(down = True), 'down.png')
        self.deleteLineAction = createAction('Delete line', 'Alt+Del', self._onShortcutDeleteLine, 'deleted.png')
        self.copyLineAction = createAction('Copy line', 'Alt+C', self._onShortcutCopyLine, 'copy.png')
        self.pasteLineAction = createAction('Paste line', 'Alt+V', self._onShortcutPasteLine, 'paste.png')
        self.cutLineAction = createAction('Cut line', 'Alt+X', self._onShortcutCutLine, 'cut.png')
        self.duplicateLineAction = createAction('Duplicate line', 'Alt+D', self._onShortcutDuplicateLine)
        self.invokeCompletionAction = createAction('Invoke completion', 'Ctrl+Space', self._completer.invokeCompletion)

        # other
        self.printAction = createAction('Print', 'Ctrl+P', self._onShortcutPrint, 'print.png')

    def __enter__(self):
        """Context management method.
        Begin atomic modification
        """
        self._atomicModificationDepth = self._atomicModificationDepth + 1
        if self._atomicModificationDepth == 1:
            self.textCursor().beginEditBlock()

    def __exit__(self, exc_type, exc_value, traceback):
        """Context management method.
        End atomic modification
        """
        self._atomicModificationDepth = self._atomicModificationDepth - 1
        if self._atomicModificationDepth == 0:
            self.textCursor().endEditBlock()

        if exc_type is not None:
            return False

    def setFont(self, font):
        pass  # suppress dockstring for non-public method
        """Set font and update tab stop width
        """
        self._fontBackup = font
        QPlainTextEdit.setFont(self, font)
        self._updateTabStopWidth()

        # text on line numbers may overlap, if font is bigger, than code font
        self._lineNumberArea.setFont(font)

    def showEvent(self, ev):
        pass  # suppress dockstring for non-public method
        """ Qt 5.big automatically changes font when adding document to workspace. Workaround this bug """
        super().setFont(self._fontBackup)
        return super().showEvent(ev)

    def _updateTabStopWidth(self):
        """Update tabstop width after font or indentation changed
        """
        self.setTabStopWidth(self.fontMetrics().width(' ' * self._indenter.width))

    @property
    def lines(self):
        return self._lines

    @lines.setter
    def lines(self, value):
        if not isinstance(value, (list, tuple)) or \
           not all([isinstance(item, str) for item in value]):
            raise TypeError('Invalid new value of "lines" attribute')
        self.setPlainText('\n'.join(value))

    def _resetCachedText(self):
        """Reset toPlainText() result cache
        """
        self._cachedText = None

    @property
    def text(self):
        if self._cachedText is None:
            self._cachedText = self.toPlainText()

        return self._cachedText

    @text.setter
    def text(self, text):
        self.setPlainText(text)

    def textForSaving(self):
        """Get text with correct EOL symbols. Use this method for saving a file to storage
        """
        lines = self.text.splitlines()
        if self.text.endswith('\n'):  # splitlines ignores last \n
            lines.append('')
        return self.eol.join(lines) + self.eol

    @property
    def selectedText(self):
        text = self.textCursor().selectedText()

        # replace unicode paragraph separator with habitual \n
        text = text.replace('\u2029', '\n')

        return text

    @selectedText.setter
    def selectedText(self, text):
        self.textCursor().insertText(text)

    @property
    def cursorPosition(self):
        cursor = self.textCursor()
        return cursor.block().blockNumber(), cursor.positionInBlock()

    @cursorPosition.setter
    def cursorPosition(self, pos):
        line, col = pos

        line = min(line, len(self.lines) - 1)
        lineText = self.lines[line]

        if col is not None:
            col = min(col, len(lineText))
        else:
            col = len(lineText) - len(lineText.lstrip())

        cursor = QTextCursor(self.document().findBlockByNumber(line))
        setPositionInBlock(cursor, col)
        self.setTextCursor(cursor)

    @property
    def absCursorPosition(self):
        return self.textCursor().position()

    @absCursorPosition.setter
    def absCursorPosition(self, pos):
        cursor = self.textCursor()
        cursor.setPosition(pos)
        self.setTextCursor(cursor)

    @property
    def selectedPosition(self):
        cursor = self.textCursor()
        cursorLine, cursorCol = cursor.blockNumber(), cursor.positionInBlock()

        cursor.setPosition(cursor.anchor())
        startLine, startCol = cursor.blockNumber(), cursor.positionInBlock()

        return ((startLine, startCol), (cursorLine, cursorCol))

    @selectedPosition.setter
    def selectedPosition(self, pos):
        anchorPos, cursorPos = pos
        anchorLine, anchorCol = anchorPos
        cursorLine, cursorCol = cursorPos

        anchorCursor = QTextCursor(self.document().findBlockByNumber(anchorLine))
        setPositionInBlock(anchorCursor, anchorCol)

        # just get absolute position
        cursor = QTextCursor(self.document().findBlockByNumber(cursorLine))
        setPositionInBlock(cursor, cursorCol)

        anchorCursor.setPosition(cursor.position(), QTextCursor.KeepAnchor)
        self.setTextCursor(anchorCursor)

    @property
    def absSelectedPosition(self):
        cursor = self.textCursor()
        return cursor.anchor(), cursor.position()

    @absSelectedPosition.setter
    def absSelectedPosition(self, pos):
        anchorPos, cursorPos = pos
        cursor = self.textCursor()
        cursor.setPosition(anchorPos)
        cursor.setPosition(cursorPos, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)

    def resetSelection(self):
        """Reset selection. Nothing will be selected.
        """
        cursor = self.textCursor()
        cursor.setPosition(cursor.position())
        self.setTextCursor(cursor)

    @property
    def eol(self):
        return self._eol

    @eol.setter
    def eol(self, eol):
        if not eol in ('\r', '\n', '\r\n'):
            raise ValueError("Invalid EOL value")
        if eol != self._eol:
            self._eol = eol
            self.eolChanged.emit(self._eol)

    @property
    def indentWidth(self):
        return self._indenter.width

    @indentWidth.setter
    def indentWidth(self, width):
        if self._indenter.width != width:
            self._indenter.width = width
            self._updateTabStopWidth()
            self.indentWidthChanged.emit(width)

    @property
    def indentUseTabs(self):
        return self._indenter.useTabs

    @indentUseTabs.setter
    def indentUseTabs(self, use):
        if use != self._indenter.useTabs:
            self._indenter.useTabs = use
            self.indentUseTabsChanged.emit(use)

    @property
    def lintMarks(self):
        return self._lintMarks

    @lintMarks.setter
    def lintMarks(self, marks):
        if self._lintMarks != marks:
            self._lintMarks = marks
            self.update()

    def _clearLintMarks(self):
        if self._lintMarks != {}:
            self._lintMarks = {}
            self.update()

    @property
    def vimModeEnabled(self):
        return self._vim is not None

    @vimModeEnabled.setter
    def vimModeEnabled(self, enabled):
        if enabled:
            if self._vim is None:
                self._vim = qutepart.vim.Vim(self)
                self._vim.modeIndicationChanged.connect(self.vimModeIndicationChanged)
                self.vimModeEnabledChanged.emit(True)
        else:
            if self._vim is not None:
                self._vim.terminate()
                self._vim = None
                self.vimModeEnabledChanged.emit(False)

    @property
    def vimModeIndication(self):
        if self._vim is not None:
            return self._vim.indication()
        else:
            return (None, None)

    def replaceText(self, pos, length, text):
        """Replace length symbols from ``pos`` with new text.

        If ``pos`` is an integer, it is interpreted as absolute position, if a tuple - as ``(line, column)``
        """
        if isinstance(pos, tuple):
            pos = self.mapToAbsPosition(*pos)

        endPos = pos + length

        if not self.document().findBlock(pos).isValid():
            raise IndexError('Invalid start position %d' % pos)

        if not self.document().findBlock(endPos).isValid():
            raise IndexError('Invalid end position %d' % endPos)

        cursor = QTextCursor(self.document())
        cursor.setPosition(pos)
        cursor.setPosition(endPos, QTextCursor.KeepAnchor)

        cursor.insertText(text)

    def insertText(self, pos, text):
        """Insert text at position

        If ``pos`` is an integer, it is interpreted as absolute position, if a tuple - as ``(line, column)``
        """
        return self.replaceText(pos, 0, text)


    def detectSyntax(self,
                     xmlFileName=None,
                     mimeType=None,
                     language=None,
                     sourceFilePath=None,
                     firstLine=None):
        """Get syntax by next parameters (fill as many, as known):

            * name of XML file with syntax definition
            * MIME type of source file
            * Programming language name
            * Source file path
            * First line of source file

        First parameter in the list has the hightest priority.
        Old syntax is always cleared, even if failed to detect new.

        Method returns ``True``, if syntax is detected, and ``False`` otherwise
        """
        oldLanguage = self.language()

        self.clearSyntax()
        
        @threaded
        def loadSyntax():
                if(Qutepart.entitySyntax is not None and xmlFileName == 'entity.xml'):
                        syntax = self.entitySyntax
                else:
                        syntax = self._globalSyntaxManager.getSyntax(SyntaxHighlighter.formatConverterFunction,
                                                     xmlFileName=xmlFileName,
                                                     mimeType=mimeType,
                                                     languageName=language,
                                                     sourceFilePath=sourceFilePath,
                                                     firstLine=firstLine)
                        if(Qutepart.entitySyntax is None and xmlFileName == 'entity.xml'):
                                Qutepart.entitySyntax = syntax
                #self._highlighter = SyntaxHighlighter(syntax, self)
                self.syntaxLoaded.emit(syntax, )
                print('FIRST')
                
        loadSyntax()


        #if syntax is not None:
            #self._highlighter = SyntaxHighlighter(syntax, self)
            #self._indenter.setSyntax(syntax)

        #newLanguage = self.language()
        #if oldLanguage != newLanguage:
            #self.languageChanged.emit(newLanguage)

        #return syntax is not None
    def loadSyntax(self, syntax):
        print('SECOND')
        if syntax is not None:
            self._highlighter = SyntaxHighlighter(syntax, self)
            self._indenter.setSyntax(syntax)

        newLanguage = self.language()
        #if oldLanguage != newLanguage:
            #self.languageChanged.emit(newLanguage)

        return syntax is not None
        
    def clearSyntax(self):
        """Clear syntax. Disables syntax highlighting

        This method might take long time, if document is big. Don't call it if you don't have to (i.e. in destructor)
        """
        if self._highlighter is not None:
            self._highlighter.terminate()
            self._highlighter = None
            self.languageChanged.emit(None)

    def language(self):
        """Get current language name.
        Return ``None`` for plain text
        """
        if self._highlighter is None:
            return None
        else:
            return self._highlighter.syntax().name

    def isHighlightingInProgress(self):
        """Check if text highlighting is still in progress
        """
        return self._highlighter is not None and \
               self._highlighter.isInProgress()

    def isCode(self, blockOrBlockNumber, column):
        """Check if text at given position is a code.

        If language is not known, or text is not parsed yet, ``True`` is returned
        """
        if isinstance(blockOrBlockNumber, QTextBlock):
            block = blockOrBlockNumber
        else:
            block = self.document().findBlockByNumber(blockOrBlockNumber)


        return self._highlighter is None or \
               self._highlighter.isCode(block, column)

    def isComment(self, line, column):
        """Check if text at given position is a comment. Including block comments and here documents.

        If language is not known, or text is not parsed yet, ``False`` is returned
        """
        return self._highlighter is not None and \
               self._highlighter.isComment(self.document().findBlockByNumber(line), column)

    def isBlockComment(self, line, column):
        """Check if text at given position is a block comment.

        If language is not known, or text is not parsed yet, ``False`` is returned
        """
        return self._highlighter is not None and \
               self._highlighter.isBlockComment(self.document().findBlockByNumber(line), column)

    def isHereDoc(self, line, column):
        """Check if text at given position is a here document.

        If language is not known, or text is not parsed yet, ``False`` is returned
        """
        return self._highlighter is not None and \
               self._highlighter.isHereDoc(self.document().findBlockByNumber(line), column)

    def _dropUserExtraSelections(self):
        if self._userExtraSelections:
            self.setExtraSelections([])

    def setExtraSelections(self, selections):
        """Set list of extra selections.
        Selections are list of tuples ``(startAbsolutePosition, length)``.
        Extra selections are reset on any text modification.

        This is reimplemented method of QPlainTextEdit, it has different signature. Do not use QPlainTextEdit method
        """
        def _makeQtExtraSelection(startAbsolutePosition, length):
            selection = QTextEdit.ExtraSelection()
            cursor = QTextCursor(self.document())
            cursor.setPosition(startAbsolutePosition)
            cursor.setPosition(startAbsolutePosition + length, QTextCursor.KeepAnchor)
            selection.cursor = cursor
            selection.format = self._userExtraSelectionFormat
            #selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            return selection

        self._userExtraSelections = [_makeQtExtraSelection(*item) for item in selections]
        self._updateExtraSelections()

    def mapToAbsPosition(self, line, column):
        """Convert line and column number to absolute position
        """
        block = self.document().findBlockByNumber(line)
        if not block.isValid():
            raise IndexError("Invalid line index %d" % line)
        if column >= block.length():
            raise IndexError("Invalid column index %d" % column)
        return block.position() + column

    def mapToLineCol(self, absPosition):
        """Convert absolute position to ``(line, column)``
        """
        block = self.document().findBlock(absPosition)
        if not block.isValid():
            raise IndexError("Invalid absolute position %d" % absPosition)

        return (block.blockNumber(),
                absPosition - block.position())

    def _updateLineNumberAreaWidth(self, newBlockCount):
        """Set line number are width according to current lines count
        """
        self.setViewportMargins(self._lineNumberArea.width() + self._markArea.width(), 0, 0, 0)

    def _updateSideAreas(self, rect, dy):
        """Repaint line number area if necessary
        """
        # _countCache magic taken from Qt docs Code Editor Example
        if dy:
            self._lineNumberArea.scroll(0, dy)
            self._markArea.scroll(0, dy)
        elif self._countCache[0] != self.blockCount() or \
             self._countCache[1] != self.textCursor().block().lineCount():

            # if block height not added to rect, last line number sometimes is not drawn
            blockHeight = self.blockBoundingRect(self.firstVisibleBlock()).height()

            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), int(rect.height() + blockHeight))
            self._lineNumberArea.update(0, rect.y(), self._markArea.width(), int(rect.height() + blockHeight))
        self._countCache = (self.blockCount(), self.textCursor().block().lineCount())

        if rect.contains(self.viewport().rect()):
            self._updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        pass # suppress dockstring for non-public method
        """QWidget.resizeEvent() implementation.
        Adjust line number area
        """
        QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self._lineNumberArea.width(), cr.height()))

        self._markArea.setGeometry(QRect(cr.left() + self._lineNumberArea.width(),
                                         cr.top(),
                                         self._markArea.width(),
                                         cr.height()))

    def _insertNewBlock(self):
        """Enter pressed.
        Insert properly indented block
        """
        cursor = self.textCursor()
        atStartOfLine = cursor.positionInBlock() == 0
        with self:
            cursor.insertBlock()
            if not atStartOfLine:  # if whole line is moved down - just leave it as is
                self._indenter.autoIndentBlock(cursor.block())
        self.ensureCursorVisible()

    def textBeforeCursor(self):
        pass  # suppress docstring for non-API method, used by internal classes
        """Text in current block from start to cursor position
        """
        cursor = self.textCursor()
        return cursor.block().text()[:cursor.positionInBlock()]

    def keyPressEvent(self, event):
        pass # suppress dockstring for non-public method
        """QPlainTextEdit.keyPressEvent() implementation.
        Catch events, which may not be catched with QShortcut and call slots
        """
        self._lastKeyPressProcessedByParent = False

        cursor = self.textCursor()

        def shouldUnindentWithBackspace():
            text = cursor.block().text()
            spaceAtStartLen = len(text) - len(text.lstrip())

            return self.textBeforeCursor().endswith(self._indenter.text()) and \
                   not cursor.hasSelection() and \
                   cursor.positionInBlock() == spaceAtStartLen

        def atEnd():
            return cursor.positionInBlock() == cursor.block().length() - 1

        def shouldAutoIndent(event):
            return atEnd() and \
                   event.text() and \
                   event.text() in self._indenter.triggerCharacters()

        def backspaceOverwrite():
            with self:
                cursor.deletePreviousChar()
                cursor.insertText(' ')
                setPositionInBlock(cursor, cursor.positionInBlock() - 1)
                self.setTextCursor(cursor)

        def typeOverwrite(text):
            """QPlainTextEdit records text input in replace mode as 2 actions:
            delete char, and type char. Actions are undone separately. This is
            workaround for the Qt bug"""
            with self:
                if not atEnd():
                    cursor.deleteChar()
                cursor.insertText(text)

        if event.matches(QKeySequence.InsertParagraphSeparator):
            if self._vim is not None:
                if self._vim.keyPressEvent(event):
                    return
            self._insertNewBlock()
        elif event.matches(QKeySequence.Copy) and self._rectangularSelection.isActive():
            self._rectangularSelection.copy()
        elif event.matches(QKeySequence.Cut) and self._rectangularSelection.isActive():
            self._rectangularSelection.cut()
        elif self._rectangularSelection.isDeleteKeyEvent(event):
            self._rectangularSelection.delete()
        elif event.key() == Qt.Key_Insert and event.modifiers() == Qt.NoModifier:
            if self._vim is not None:
                self._vim.keyPressEvent(event)
            else:
                self.setOverwriteMode(not self.overwriteMode())
        elif event.key() == Qt.Key_Backspace and \
             shouldUnindentWithBackspace():
            self._indenter.onShortcutUnindentWithBackspace()
        elif event.key() == Qt.Key_Backspace and \
             not cursor.hasSelection() and \
             self.overwriteMode() and \
             cursor.positionInBlock() > 0:
            backspaceOverwrite()
        elif self.overwriteMode() and \
            event.text() and \
            qutepart.vim.isChar(event) and \
            not cursor.hasSelection() and \
            cursor.positionInBlock() < cursor.block().length():
            typeOverwrite(event.text())
            if self._vim is not None:
                self._vim.keyPressEvent(event)
        elif event.matches(QKeySequence.MoveToStartOfLine):
            if self._vim is not None and \
               self._vim.keyPressEvent(event):
                return
            else:
                self._onShortcutHome(select=False)
        elif event.matches(QKeySequence.SelectStartOfLine):
            self._onShortcutHome(select=True)
        elif self._rectangularSelection.isExpandKeyEvent(event):
            self._rectangularSelection.onExpandKeyEvent(event)
        elif shouldAutoIndent(event):
                with self:
                    super(Qutepart, self).keyPressEvent(event)
                    self._indenter.autoIndentBlock(cursor.block(), event.text())
        else:
            if self._vim is not None:
                if self._vim.keyPressEvent(event):
                    return

            # make action shortcuts override keyboard events (non-default Qt behaviour)
            for action in self.actions():
                seq = action.shortcut()
                if seq.count() == 1 and seq[0] == event.key() | int(event.modifiers()):
                    action.trigger()
                    break
            else:
                if event.text() and event.modifiers() == Qt.AltModifier:
                    return  # alt+letter is a shortcut. Not mine
                else:
                    self._lastKeyPressProcessedByParent = True
                    super(Qutepart, self).keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if self._lastKeyPressProcessedByParent:
            """ A hacky way to do not show completion list after a event, processed by vim
            """

            text = event.text()
            textTyped = (text and \
                         event.modifiers() in (Qt.NoModifier, Qt.ShiftModifier)) and \
                         (text.isalpha() or text.isdigit() or text == '_')

            if textTyped or \
            (event.key() == Qt.Key_Backspace and self._completer.isVisible()):
                self._completer.invokeCompletionIfAvailable()

        super(Qutepart, self).keyReleaseEvent(event)

    def mousePressEvent(self, mouseEvent):
        pass  # suppress docstring for non-public method
        if mouseEvent.modifiers() in RectangularSelection.MOUSE_MODIFIERS and \
           mouseEvent.button() == Qt.LeftButton:
            self._rectangularSelection.mousePressEvent(mouseEvent)
        else:
            super(Qutepart, self).mousePressEvent(mouseEvent)

    def mouseMoveEvent(self, mouseEvent):
        pass  # suppress docstring for non-public method
        if mouseEvent.modifiers() in RectangularSelection.MOUSE_MODIFIERS and \
           mouseEvent.buttons() == Qt.LeftButton:
            self._rectangularSelection.mouseMoveEvent(mouseEvent)
        else:
            super(Qutepart, self).mouseMoveEvent(mouseEvent)

    def _chooseVisibleWhitespace(self, text):
        result = [False for _ in range(len(text))]

        lastNonSpaceColumn = len(text.rstrip()) - 1

        # Draw not trailing whitespace
        if self.drawAnyWhitespace:
            # Any
            for column, char in enumerate(text[:lastNonSpaceColumn]):
                if char.isspace() and \
                   (char == '\t' or \
                    column == 0 or \
                    text[column - 1].isspace() or \
                    ((column + 1) < lastNonSpaceColumn and \
                     text[column + 1].isspace())):
                    result[column] = True
        elif self.drawIncorrectIndentation:
            # Only incorrect
            if self.indentUseTabs:
                # Find big space groups
                firstNonSpaceColumn = len(text) - len(text.lstrip())
                bigSpaceGroup = ' ' * self.indentWidth
                column = 0
                while True:
                    column = text.find(bigSpaceGroup, column, lastNonSpaceColumn)
                    if column == -1 or column >= firstNonSpaceColumn:
                        break

                    for index in range(column, column + self.indentWidth):
                        result[index] = True
                    while index < lastNonSpaceColumn and \
                          text[index] == ' ':
                            result[index] = True
                            index += 1
                    column = index
            else:
                # Find tabs:
                column = 0
                while column != -1:
                    column = text.find('\t', column, lastNonSpaceColumn)
                    if column != -1:
                        result[column] = True
                        column += 1

        # Draw trailing whitespace
        if self.drawIncorrectIndentation or self.drawAnyWhitespace:
            for column in range(lastNonSpaceColumn + 1, len(text)):
                result[column] = True

        return result

    def _drawIndentMarkersAndEdge(self, paintEventRect):
        """Draw indentation markers
        """
        painter = QPainter(self.viewport())

        def cursorRect(block, column, offset):
            cursor = QTextCursor(block)
            setPositionInBlock(cursor, column)
            return self.cursorRect(cursor).translated(offset, 0)

        def drawWhiteSpace(block, column, char):
            leftCursorRect = cursorRect(block, column, 0)
            rightCursorRect = cursorRect(block, column + 1, 0)
            if leftCursorRect.top() == rightCursorRect.top():  # if on the same visual line
                middleHeight = int((leftCursorRect.top() + leftCursorRect.bottom()) / 2)
                if char == ' ':
                    painter.setPen(Qt.transparent)
                    painter.setBrush(QBrush(Qt.gray))
                    xPos = int((leftCursorRect.x() + rightCursorRect.x()) / 2)
                    painter.drawRect(QRect(xPos, middleHeight, 2, 2))
                else:
                    painter.setPen(QColor(Qt.gray).lighter(factor=120))
                    painter.drawLine(leftCursorRect.x() + 3, middleHeight,
                                     rightCursorRect.x() - 3, middleHeight)

        def effectiveEdgePos(text):
            """Position of edge in a block.
            Defined by self.lineLengthEdge, but visible width of \t is more than 1,
            therefore effective position depends on count and position of \t symbols
            Return -1 if line is too short to have edge
            """
            if self.lineLengthEdge is None:
                return -1

            tabExtraWidth = self.indentWidth - 1
            fullWidth = len(text) + (text.count('\t') * tabExtraWidth)
            if fullWidth <= self.lineLengthEdge:
                return -1

            currentWidth = 0
            for pos, char in enumerate(text):
                if char == '\t':
                    # Qt indents up to indentation level, so visible \t width depends on position
                    currentWidth += (self.indentWidth - (currentWidth % self.indentWidth))
                else:
                    currentWidth += 1
                if currentWidth > self.lineLengthEdge:
                    return pos
            else:  # line too narrow, probably visible \t width is small
                return -1

        def drawEdgeLine(block, edgePos):
            painter.setPen(QPen(QBrush(self.lineLengthEdgeColor), 0))
            rect = cursorRect(block, edgePos, 0)
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

        def drawIndentMarker(block, column):
            painter.setPen(QColor(Qt.blue).lighter())
            rect = cursorRect(block, column, offset=0)
            painter.drawLine(rect.topLeft(), rect.bottomLeft())

        indentWidthChars = len(self._indenter.text())
        cursorPos = self.cursorPosition

        for block in iterateBlocksFrom(self.firstVisibleBlock()):
            blockGeometry = self.blockBoundingGeometry(block).translated(self.contentOffset())
            if blockGeometry.top() > paintEventRect.bottom():
                break

            if block.isVisible() and blockGeometry.toRect().intersects(paintEventRect):

                # Draw indent markers, if good indentation is not drawn
                text = block.text()
                if not self.drawAnyWhitespace:
                    column = indentWidthChars
                    while text.startswith(self._indenter.text()) and \
                          len(text) > indentWidthChars and \
                          text[indentWidthChars].isspace():

                        if column != self.lineLengthEdge and \
                           (block.blockNumber(), column) != cursorPos:  # looks ugly, if both drawn
                            """on some fonts line is drawn below the cursor, if offset is 1
                            Looks like Qt bug"""
                            drawIndentMarker(block, column)

                        text = text[indentWidthChars:]
                        column += indentWidthChars

                # Draw edge, but not over a cursor
                edgePos = effectiveEdgePos(block.text())
                if edgePos != -1 and edgePos != cursorPos[1]:
                    drawEdgeLine(block, edgePos)

                if self.drawAnyWhitespace or \
                   self.drawIncorrectIndentation:
                    text = block.text()
                    for column, draw in enumerate(self._chooseVisibleWhitespace(text)):
                        if draw:
                            drawWhiteSpace(block, column, text[column])

    def paintEvent(self, event):
        pass # suppress dockstring for non-public method
        """Paint event
        Draw indentation markers after main contents is drawn
        """
        super(Qutepart, self).paintEvent(event)
        self._drawIndentMarkersAndEdge(event.rect())

    def _currentLineExtraSelections(self):
        """QTextEdit.ExtraSelection, which highlightes current line
        """
        #self.highlightColor = QColor('#2CA2AE')
        if(self.overwriteHighlightColor != None):
        	lineColor = self.overwriteHighlightColor
        else:
        	
	        lineColor = self.highlightColor
        
        def makeSelection(cursor):
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(lineColor)
            
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            cursor.clearSelection()
            selection.cursor = cursor
            return selection

        rectangularSelectionCursors = self._rectangularSelection.cursors()
        if rectangularSelectionCursors:
            return [makeSelection(cursor) \
                        for cursor in rectangularSelectionCursors]
        else:
            return [makeSelection(self.textCursor())]

    def _updateExtraSelections(self):
        
        
        
        if(self.updatingCursor):return
    
        if(self.highlightCurrentWordJustFinished):
            self.highlightCurrentWordJustFinished = False
            return
    
        print("updating cursor updateExtra")
        """Highlight current line
        """
        cursorColumnIndex = self.textCursor().positionInBlock()

        bracketSelections = self._bracketHighlighter.extraSelections(self,
                                                                     self.textCursor().block(),
                                                                     cursorColumnIndex)

        selections = self._currentLineExtraSelections() + \
                     self._rectangularSelection.selections() + \
                     bracketSelections + \
                     self._userExtraSelections

        self._nonVimExtraSelections = selections

        if self._vim is None:
            allSelections = selections
        else:
            allSelections = selections + self._vim.extraSelections()

        QPlainTextEdit.setExtraSelections(self, allSelections)

    def _updateVimExtraSelections(self):
        QPlainTextEdit.setExtraSelections(self, self._nonVimExtraSelections + self._vim.extraSelections())

    def _onShortcutIndent(self):
        if self.textCursor().hasSelection():
            self._indenter.onChangeSelectedBlocksIndent(increase=True)
        else:
            self._indenter.onShortcutIndentAfterCursor()

    def _onShortcutScroll(self, down):
        """Ctrl+Up/Down pressed, scroll viewport
        """
        value = self.verticalScrollBar().value()
        if down:
            value += 1
        else:
            value -= 1
        self.verticalScrollBar().setValue(value)

    def _onShortcutSelectAndScroll(self, down):
        """Ctrl+Shift+Up/Down pressed.
        Select line and scroll viewport
        """
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Down if down else QTextCursor.Up, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        self._onShortcutScroll(down)

    def _onShortcutHome(self, select):
        """Home pressed. Run a state machine:

            1. Not at the line beginning. Move to the beginning of the line or
               the beginning of the indent, whichever is closest to the current
               cursor position.
            2. At the line beginning. Move to the beginning of the indent.
            3. At the beginning of the indent. Go to the beginning of the block.
            4. At the beginning of the block. Go to the beginning of the indent.
        """
        # Gather info for cursor state and movement.
        cursor = self.textCursor()
        text = cursor.block().text()
        indent = len(text) - len(text.lstrip())
        anchor = QTextCursor.KeepAnchor if select else QTextCursor.MoveAnchor

        # Determine current state and move based on that.
        if cursor.positionInBlock() == indent:
            # We're at the beginning of the indent. Go to the beginning of the
            # block.
            cursor.movePosition(QTextCursor.StartOfBlock, anchor)
        elif cursor.atBlockStart():
            # We're at the beginning of the block. Go to the beginning of the
            # indent.
            setPositionInBlock(cursor, indent, anchor)
        else:
            # Neither of the above. There's no way I can find to directly
            # determine if we're at the beginning of a line. So, try moving and
            # see if the cursor location changes.
            pos = cursor.positionInBlock()
            cursor.movePosition(QTextCursor.StartOfLine, anchor)
            # If we didn't move, we were already at the beginning of the line.
            # So, move to the indent.
            if pos == cursor.positionInBlock():
                setPositionInBlock(cursor, indent, anchor)
            # If we did move, check to see if the indent was closer to the
            # cursor than the beginning of the indent. If so, move to the
            # indent.
            elif cursor.positionInBlock() < indent:
                setPositionInBlock(cursor, indent, anchor)

        self.setTextCursor(cursor)

    def _selectLines(self, startBlockNumber, endBlockNumber):
        """Select whole lines
        """
        startBlock = self.document().findBlockByNumber(startBlockNumber)
        endBlock = self.document().findBlockByNumber(endBlockNumber)
        cursor = QTextCursor(startBlock)
        cursor.setPosition(endBlock.position(), QTextCursor.KeepAnchor)
        cursor.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        self.setTextCursor(cursor)
        

    def _selectedBlocks(self):
        """Return selected blocks and tuple (startBlock, endBlock)
        """
        cursor = self.textCursor()
        return self.document().findBlock(cursor.selectionStart()), \
               self.document().findBlock(cursor.selectionEnd())

    def _selectedBlockNumbers(self):
        """Return selected block numbers and tuple (startBlockNumber, endBlockNumber)
        """
        startBlock, endBlock = self._selectedBlocks()
        return startBlock.blockNumber(), endBlock.blockNumber()

    def _onShortcutMoveLine(self, down):
        """Move line up or down
        Actually, not a selected text, but next or previous block is moved
        TODO keep bookmarks when moving
        """
        startBlock, endBlock = self._selectedBlocks()

        startBlockNumber = startBlock.blockNumber()
        endBlockNumber = endBlock.blockNumber()

        def _moveBlock(block, newNumber):
            text = block.text()
            with self:
                del self.lines[block.blockNumber()]
                self.lines.insert(newNumber, text)

        if down:  # move next block up
            blockToMove = endBlock.next()
            if not blockToMove.isValid():
                return

            # if operaiton is UnDone, marks are located incorrectly
            self._bookmarks.clear(startBlock, endBlock.next())

            _moveBlock(blockToMove, startBlockNumber)

            self._selectLines(startBlockNumber + 1, endBlockNumber + 1)
        else:  # move previous block down
            blockToMove = startBlock.previous()
            if not blockToMove.isValid():
                return

            # if operaiton is UnDone, marks are located incorrectly
            self._bookmarks.clear(startBlock.previous(), endBlock)

            _moveBlock(blockToMove, endBlockNumber)

            self._selectLines(startBlockNumber - 1, endBlockNumber - 1)

        self._markArea.update()

    def _selectedLinesSlice(self):
        """Get slice of selected lines
        """
        startBlockNumber, endBlockNumber = self._selectedBlockNumbers()
        return slice(startBlockNumber, endBlockNumber + 1, 1)

    def _onShortcutDeleteLine(self):
        """Delete line(s) under cursor
        """
        del self.lines[self._selectedLinesSlice()]

    def _onShortcutCopyLine(self):
        """Copy selected lines to the clipboard
        """
        lines = self.lines[self._selectedLinesSlice()]
        text = self._eol.join(lines)
        QApplication.clipboard().setText(text)

    def _onShortcutPasteLine(self):
        """Paste lines from the clipboard
        """
        lines = self.lines[self._selectedLinesSlice()]
        text = QApplication.clipboard().text()
        if text:
            with self:
                if self.textCursor().hasSelection():
                    startBlockNumber, endBlockNumber = self._selectedBlockNumbers()
                    del self.lines[self._selectedLinesSlice()]
                    self.lines.insert(startBlockNumber, text)
                else:
                    line, col = self.cursorPosition
                    if col > 0:
                        line = line + 1
                    self.lines.insert(line, text)

    def _onShortcutCutLine(self):
        """Cut selected lines to the clipboard
        """
        lines = self.lines[self._selectedLinesSlice()]

        self._onShortcutCopyLine()
        self._onShortcutDeleteLine()

    def _onShortcutDuplicateLine(self):
        """Duplicate selected text or current line
        """
        cursor = self.textCursor()
        if cursor.hasSelection():  # duplicate selection
            text = cursor.selectedText()
            selectionStart, selectionEnd = cursor.selectionStart(), cursor.selectionEnd()
            cursor.setPosition(selectionEnd)
            cursor.insertText(text)
            # restore selection
            cursor.setPosition(selectionStart)
            cursor.setPosition(selectionEnd, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
        else:
            line = cursor.blockNumber()
            self.lines.insert(line + 1, self.lines[line])
            self.ensureCursorVisible()

        self._updateExtraSelections()  # newly inserted text might be highlighted as braces

    def _onShortcutPrint(self):
        """Ctrl+P handler.
        Show dialog, print file
        """
        dialog = QPrintDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            printer = dialog.printer()
            self.print_(printer)

    def insertFromMimeData(self, source):
        pass # suppress docstring for non-public method
        if source.hasFormat(self._rectangularSelection.MIME_TYPE):
            self._rectangularSelection.paste(source)
        else:
            super(Qutepart, self).insertFromMimeData(source)


def iterateBlocksFrom(block):
    """Generator, which iterates QTextBlocks from block until the End of a document
    """
    while block.isValid():
        yield block
        block = block.next()

def iterateBlocksBackFrom(block):
    """Generator, which iterates QTextBlocks from block until the Start of a document
    """
    while block.isValid():
        yield block
        block = block.previous()


from common import settings, util

class EverydayPart(Qutepart):
	
	toolTipEvent = pyqtSignal(int, str, object)
	newExtraSelection = pyqtSignal(object)
	tabAlwaysIndent = True

	def __init__(self, *args):
		
		self.updatingCursor = False
		self.highlightCurrentWordJustFinished = False
		# self.mousePressed = False
		Qutepart.__init__(self, *args)
		
		self.completionEnabled = settings.get_option('editor/completion_enabled', True)
		
		self.selectionChanged.connect(self.highlightCurrentWord)
		#self.newExtraSelection.connect(self.addExtraSelection)
		
		self.wordHighlighted = False
		self.mousePressed = False
		
		self.searchColor = QColor('#ffffa3')
		
		ovw_highlight_color = settings.get_option('editor/color_highlighted_line', None)
		
		if(ovw_highlight_color != None):
			self.overwriteHighlightColor = QColor(ovw_highlight_color)

		
		self.initialSearchPos = None
		
	def addExtraSelection(self, selection):
		pass
	
	def dropEvent(self, e):
		data = QMimeData()
		text = e.mimeData().text()
		data_path = settings.get_option('general/data_path', '')
		newText = []
		first = True
		
		extensionsToCheck = ('.wav', '.ogg', '.bor')
		
		
		for line in text.split('\n'):

			if data_path in line:
				#print(line)
				command = 'frame'
				#if line.endswith(extensionsToCheck):
				if any(x in line for x in extensionsToCheck):
					command = 'sound'
				newLine = '	' + command + ' data' + line[line.index(data_path)+len(data_path):]
				if first:
					newLine = '\n' + newLine
				newText.append(newLine)
			else:
				newText.append(line)
			
			if first:
				first = False
		data.setText('\n'.join(newText))
		#data.setUrls([])
		e = QDropEvent(e.pos(), e.dropAction(), data, e.mouseButtons(), e.keyboardModifiers())
		
		Qutepart.dropEvent(self, e)
		
	def event(self, e):
		if e.type() == QEvent.ToolTip:
			#QHelpEvent* helpEvent = static_cast<QHelpEvent*>(event);
			start, end = self.selectedPosition
			if start != end:
				self.toolTipEvent.emit(start, self.selectedText, e)
			else:
				cursor = self.cursorForPosition(e.pos())
				cursor.select(QTextCursor.LineUnderCursor)
				line = cursor.block().blockNumber()
				if (len(cursor.selectedText())!= 0):
					self.toolTipEvent.emit(line, cursor.selectedText(), e)
			return True

		return Qutepart.event(self, e)
		
		
	def keyPressEvent(self, e):
		if e.text() == '	' and EverydayPart.tabAlwaysIndent: # tab
			start, end = self.selectedPosition
			start = start[0]
			end = end[0]
			if end < start:
				tmp = end
				end = start
				start = tmp
			#line, col = self.cursorPosition
			for line in range(start, end+1):
				self.insertText((line, 0), e.text())

		else:
			Qutepart.keyPressEvent(self, e)
		
	def mousePressEvent(self, e):
		self.mousePressed = True
		Qutepart.mousePressEvent(self, e)
		
	def mouseReleaseEvent(self, e):
		self.mousePressed = False
		Qutepart.mouseReleaseEvent(self, e)
		
	
	def getContext(self, blockNumber, col=None):
		block = self.document().findBlockByNumber(blockNumber)
		data = block.userData().data[0].currentContext()
		data = data.name
		
		return data
	
	def saveScroll(self):
		self.previousScroll = self.verticalScrollBar().sliderPosition()
		print('saveScroll', self.previousScroll)
		
	def restoreScroll(self):
		self.verticalScrollBar().setSliderPosition(self.previousScroll)

	def highlightCurrentWord(self): # PROBABLY DAIMAO
		print("highlight current word");
		
		
	
		#@threaded
		def buildFormat():
			#selection = QTextEdit.ExtraSelection()
			#cursor = self.textCursor()
			#selection.format.setBackground(self.searchColor)
			#selection.cursor = cursor
			#format.setForeground(Qt.black);
			regex = QRegExp(word)
			# Process the displayed document
			pos = 0
			index = regex.indexIn(self.text, pos)
			
			previousScroll = self.verticalScrollBar().sliderPosition()
			previousSelected = self.selectedPosition
			
			self.moveCursor(QTextCursor.Start);
			extraSelections = []
			while self.find(word):
				print("found")
				selection = QTextEdit.ExtraSelection()
				selection.cursor = self.textCursor()
				selection.format.setBackground(self.searchColor)
				extraSelections.append(selection)
				
			#for e in extraSelections:
				#print(e.cursor.block().text())
			
			
			QPlainTextEdit.setExtraSelections(self, extraSelections)
			
			
			#while (index != -1 and index != 0):
				## Select the matched text and apply the desired format
				#cursor.setPosition(index)
				#cursor.movePosition(QTextCursor.EndOfWord, 1)
				##cursor.mergeCharFormat(selection.format)
				
				##selection.append(
				## Move to the next match
				#pos = index + regex.matchedLength()
				#index = regex.indexIn(self.text, pos)
			
			self.selectedPosition = previousSelected
			self.verticalScrollBar().setSliderPosition(previousScroll)
			endBuild()

		
		def endBuild():
			self.updatingCursor = False
			self.highlightCurrentWordJustFinished = True 

			#self.selectionChanged.connect(self.highlightCurrentWord)
			if self._highlighter != None:
				return
				self._highlighter._document.contentsChange.connect(self._highlighter._onContentsChange)
				
		
		if self.updatingCursor or self.mousePressed: return
	
		# self.blockSignals(True)
		self.updatingCursor = True
		word = self.selectedText
		# print('word', '|' + word + '|')
		if len(word) == 0 or word[0] in ('\t', ' ') or word[-1] in ('\t', ' '):
			self.setExtraSelections([])
			#QPlainTextEdit.setExtraSelections(self, [])
			self.updatingCursor = False
			self.blockSignals(False)
			return
		
		
		# print('word', 'continue')
		#try:
			#if self._highlighter != None:
				#self._highlighter._document.contentsChange.disconnect(self._highlighter._onContentsChange)
		#except TypeError:
			#pass
		#self._highlighter
		
		#self.selectionChanged.disconnect(self.highlightCurrentWord)
		
		# Reset previous
		self.updatingCursor = True
		#cursor = self.textCursor()
		#cursor.movePosition(QTextCursor.Start, QTextCursor.MoveAnchor);
		#cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor);
		
		#cursor.setCharFormat(QTextCharFormat())

		#word = self.selectedText
		#if len(word) == 0 :
			##if self.wordHighlighted:
				##self.wordHighlighted = False
			#endBuild()
			#return

		
		#QSignalBlocker(self.document())
		#
		
		self.updatingCursor = False
		
		
		
		
		start, end = self.absSelectedPosition
		if start > end:
			tmp = start
			start = end
			end = tmp

		if start == 0:
			startChar = ' '
		else:
			startChar = self.text[ start-1]
			
		if end >= len(self.text):  # End of text
			endChar = ' '
		else : endChar = self.text[ end]
		
		print(startChar, endChar)
		
		delimiters = ('.', ',', ' ', '	', '-', ';', '(', ')', '{', '}', '/', '\n')
		#print('here', startChar, endChar)
		if(startChar not in delimiters  or endChar not in delimiters) : return
		#print('good')
		
		self.updatingCursor = True

		# print('word', 'continue 2')
		buildFormat()
		# self.blockSignals(False)
		
		#cursor.select(QTextCursor.WordUnderCursor);
		
		

		##cursor.setPosition(begin, QTextCursor.MoveAnchor);
		##cursor.setPosition(end, QTextCursor.KeepAnchor);
		#cursor.setCharFormat(format)
		##cursor.mergeCharFormat(fmt); # I did try also cursor.setCharFormat(fmt)

	def search(self, text, searchForward=True, loop=True):
		self.setCenterOnScroll(True)
		
		print('editor', self.initialSearchPos)
		if(self.initialSearchPos == None):
			self.initialSearchPos = self.textCursor()
			
		
		print('text', text)
		if(text == ''): 
			#self.searchEntry.setStyleSheet("")
			self.setTextCursor(self.initialSearchPos)
			self.initialSearchPos = None
			return False

		if searchForward:
			options = QtGui.QTextDocument.FindFlags()
		else:
			options = QtGui.QTextDocument.FindBackward
		result = self.find(text, options) # first try to search from cursor to end of document
		
		if(result):
			#self.searchEntry.setStyleSheet("QLineEdit { background: rgb(175, 255, 175); }");
			return True
		
		elif(loop and not result):
			self.moveCursor(QtGui.QTextCursor.Start)
			if not self.find(text, options): # then try to search from start to end of document
			
			
				# self.editor.moveCursor(self.editor.initialSearchPos)
				self.setTextCursor(self.initialSearchPos)
				self.initialSearchPos = None
			
			
				#self.searchEntry.setStyleSheet("QLineEdit { background: rgb(255, 175, 175); }");
				 # selection-background-color: rgb(233, 99, 0);
				 
				return False
			else:
				
				#self.searchEntry.setStyleSheet("QLineEdit { background: rgb(175, 255, 175); }");
				return True
	
	
	def replace(self, text1, text2):
		if(self.selectedText != ''):
			self.selectedText = text2
			self.search(text1)
			
	def replaceAllRaw(self, text, replaceWith):
		self.updatingCursor = True
		
		if(self.selectedText == ''):
		
			lines = self.lines
			newLines = []
			for line in lines:
				newLines.append(line.replace(text, replaceWith))
			
			self.lines = newLines
		else:
			self.selectedText = self.selectedText.replace(text, replaceWith)
		self.updatingCursor = False
	
	def setTheme(self, data):
		if data is None:
			return
		print(';'.join(data['css']))
		self.setStyleSheet('QPlainTextEdit {' + ';'.join(data['css']) + '}')
		self.searchColor = data['searchColor']
		self.highlightColor = data['currentLine']
		#self.highlightColor = QColor('#2CA2AE')
	
	
	def wheelEvent(self, e):
		if (e.modifiers() & Qt.ControlModifier):
			if e.angleDelta().y() > 0:
				step = 1
			else:
				step = -1
			font = self.currentFont
			font.setPointSize(font.pointSize()+step)
			self.setFont(font)
		else:
			Qutepart.wheelEvent(self, e)
