STYLE_SHEET = '''

.red{
	color :red;
}

QWidget {
	/*border-radius : 4px;*/
	font-family:Courier;
	margin:0px;
	padding:0px;
}

QLayout {
	margin : 0px;
	padding : 0px;
}

QLineEdit, QTreeView, QPlainTextEdit{
	border-radius : 4px;
	border: 2px solid #C4C4C3;
	
}

QLineEdit {
	padding : 4px;
}

QTableView {
	border-radius : 4px;
	border: 2px solid #C4C4C3;
	border-top : none;
}

QPushButton {
   background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    border-style: outset;
    border-width: 1px;
    border-radius: 10px;
    border-color: beige;
    border: 2px solid #C4C4C3;
    /*font: bold 14px;*/
    /*min-width: 10em;*/
    padding: 4px;
}

QPushButton:pressed {
    background-color: #E9E9E9;
    border-style: inset;
}


QPushButton#toggleButton {
    background-color: #BA6565;
    border-style: outset;
    border-width: 2px;
    border-radius: 10px;
    border-color: beige;
    font: bold 14px;
    min-width: 10em;
    padding: 6px;
}
QPushButton#toggleButton:pressed {
    background-color: #E9E9E9;
    border-style: inset;
}

QPushButton[activated="true"], QPushButton#toggleButton[activated="true"] {
    color: #F2F2F2;
    background-color: green;
    border-style: outset;
    border-width: 2px;
    border-radius: 10px;
    border-color: beige;
    font: bold 14px;
    min-width: 10em;
    padding: 6px;
}

QScrollBar:vertical {               
    border: 1px solid #999999;
        background:white;
        width:12px;    
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
        min-height: 15px;
    
    }
    QScrollBar::add-line:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
        height: 4px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
        height: 4px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    
    
 EverydayEditor   QScrollBar:vertical {               

        width:30px;    
        margin: 0px 0px 0px 0px;
    }
    QScrollBar::handle:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
        min-height: 15px;
    
    }
    QScrollBar::add-line:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
        height: 4px;
        subcontrol-position: bottom;
        subcontrol-origin: margin;
    }
    QScrollBar::sub-line:vertical {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop: 0  rgb(32, 47, 130), stop: 0.5 rgb(32, 47, 130),  stop:1 rgb(32, 47, 130));
        height: 4px;
        subcontrol-position: top;
        subcontrol-origin: margin;
    }
    
    
QTabWidget::pane { /* The tab widget frame */
    border : 0px;
}


    
QTabBar::tab:top, QTabBar::tab:bottom {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    border: 2px solid #C4C4C3;
    border-bottom-color: #C2C7CB; /* same as the pane color */
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 2px;
}

QTabBar::tab:left, QTabBar::tab:right {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
    border: 2px solid #C4C4C3;
    border-right-color: #C2C7CB; /* same as the pane color */
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
     padding: 20px 6px;
    margin : 10px 1px; 
}

QTabWidget::tab-bar:left, QTabWidget::tab-bar:right {
    alignment: center;
}

QTabBar::tab:selected, QTabBar::tab:hover {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #fafafa, stop: 0.4 #f4f4f4,
                                stop: 0.5 #e7e7e7, stop: 1.0 #fafafa);
}

QTabBar::tab:top:selected, QTabBar::tab:bottom:selected {
    border-color: #9B9B9B;
    border-bottom-color: #C2C7CB; /* same as pane color */
}

QTabBar::tab:left:selected, QTabBar::tab:right:selected {
    border-color: #9B9B9B;
    border-right-color: #C2C7CB; /* same as pane color */
}


QTabBar::tab::top:!selected, QTabBar::tab::bottom:!selected {
    margin-top: 2px; /* make non-selected tabs look smaller */
}

QTabBar::tab::left:!selected, QTabBar::tab::right:!selected {
    margin-left: 4px; /* make non-selected tabs look smaller */
}


QTabBar::close-button {
   image: url(icons/genre.png);
    subcontrol-position: right;
}

QTabBar::close-button:hover {
    image: url(icons/star.png);
}


QHeaderView::section {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #616161, stop: 0.5 #505050,
                                      stop: 0.6 #434343, stop:1 #656565);
    color: white;
    padding-left: 4px;
    border: 1px solid #6c6c6c;
}

QHeaderView::section:checked
{
    background-color: red;
}

/* style the sort indicator */
QHeaderView::down-arrow {
    image: url(down_arrow.png);
}

QHeaderView::up-arrow {
    image: url(up_arrow.png);
}




QSlider::groove:horizontal {
    border: 1px solid #999999;
    height: 8px; /* the groove expands to the size of the slider by default. by giving it a height, it has a fixed size */
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
    margin: 2px 0;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
    border: 1px solid #5c5c5c;
    width: 18px;
    margin: -2px 0; /* handle is placed by default on the contents rect of the groove. Expand outside the groove */
    border-radius: 3px;
}

QSlider::groove:vertical {
    background: red;
    position: absolute; /* absolutely position 4px from the left and right of the widget. setting margins on the widget should work too... */
    left: 4px; right: 4px;
}

QSlider::handle:vertical {
    height: 10px;
    background: green;
    margin: 0 -4px; /* expand outside the groove */
}

QSlider::add-page:vertical {
    background: white;
}

QSlider::sub-page:vertical {
    background: pink;
}



QComboBox {
    border: 1px solid gray;
    border-radius: 3px;
    padding: 1px 18px 1px 3px;
    min-width: 6em;
}

QComboBox:editable {
    background: white;
}

QComboBox:!editable, QComboBox::drop-down:editable {
     background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                 stop: 0 #E1E1E1, stop: 0.4 #DDDDDD,
                                 stop: 0.5 #D8D8D8, stop: 1.0 #D3D3D3);
}

/* QComboBox gets the "on" state when the popup is open */
QComboBox:!editable:on, QComboBox::drop-down:editable:on {
    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                stop: 0 #D3D3D3, stop: 0.4 #D8D8D8,
                                stop: 0.5 #DDDDDD, stop: 1.0 #E1E1E1);
}

QComboBox:on { /* shift the text when the popup opens */
    padding-top: 3px;
    padding-left: 4px;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;

    border-left-width: 1px;
    border-left-color: darkgray;
    border-left-style: solid; /* just a single line */
    border-top-right-radius: 3px; /* same radius as the QComboBox */
    border-bottom-right-radius: 3px;
}

QComboBox::down-arrow {
    image: url(/usr/share/icons/crystalsvg/16x16/actions/1downarrow.png);
}

QComboBox::down-arrow:on { /* shift the arrow when popup is open */
    top: 1px;
    left: 1px;
}




QMenuBar {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 lightgray, stop:1 darkgray);
}

QMenuBar::item {
    spacing: 12px; /* spacing between menu bar items */
    padding: 1px 10px;
    background: transparent;
    border-radius: 4px;
}

QMenuBar::item:selected { /* when selected using mouse or keyboard */
    background: #a8a8a8;
}

QMenuBar::item:pressed {
    background: #888888;
}

ButtonGroupBox, QGroupBox {
	font-weight:bold;
    border: 1px solid gray;
    border-radius: 9px;
    margin-top: 0.5em;
}

QGroupBox::title:hover {
	font-weight:bold;
    border: 1px solid gray;
    border-radius: 9px;
    margin-top: 0.5em;
    color:green;
    background-color:green;
}

ButtonGroupBox::title, QGroupBox::title {
	
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 3px 0 3px;
}

QWidget#FileSelector{
	margin-left:200px;
	padding-left:200px;
	font-size:20px;
}

QToolButton#MainToolButton {  margin:0px 4px; padding: 4px 10px; }

QTreeView::item {
  padding: 5px 0px;
}


QToolButton[popupMode="1"] { /* only for MenuButtonPopup */
padding-right: 20px; /* make way for the popup button */
}

/* the subcontrols below are used only in the MenuButtonPopup mode */

QToolButton::menu-button {
border: 2px solid gray;
border-top-right-radius: 6px;
border-bottom-right-radius: 6px;
/* 16px width + 4px for border = 20px allocated above */
width: 16px;
image: url(icons/caret-down.svg);
background:white;
}


QToolButton::menu-arrow {
    image: url(icons/todo.png);
}

QToolButton::menu-arrow:open {
    top: 1px; left: 1px; /* shift it a bit */
}


'''
