from PySide import QtGui
import sys

from MSField    import MSField
from MSButton   import MSButton
from MSBot      import MSBot

class MSScreen(QtGui.QMainWindow):
    __field__ = None
    __bot__ = None
    __grid__ = None
    __console__ = None
    
    def __init__(self):
        super(MSScreen, self).__init__()
        self.__initUI__()
        
    def __initUI__(self):
        #Set start and finish actions
        exitAction = QtGui.QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из приложения')
        exitAction.triggered.connect(self.close)
        
        startAction = QtGui.QAction('Начать', self)
        startAction.setShortcut('Ctrl+N')
        startAction.setStatusTip('Начать приложение')
        startAction.triggered.connect(self.__game_start__)
        
        botAction = QtGui.QAction('Бот', self)
        botAction.setShortcut('Ctrl+B')
        botAction.setStatusTip('Запустить бота')
        botAction.triggered.connect(self.__bot_start__)
        
        botStep = QtGui.QAction('Шаг', self)
        botStep.setShortcut('Ctrl+S')
        botStep.setStatusTip('Сделать следующий шаг бота')
        botStep.triggered.connect(self.__bot_step__)
        
        #Initiate menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Меню')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(startAction)
        
        cheatMenu = menubar.addMenu('Читы')
        cheatMenu.addAction(botAction)
        cheatMenu.addAction(botStep)
        
        self.setWindowTitle('Minesweeper')
        self.setWindowIcon(QtGui.QIcon('M.png'))
    
    def setNames(self):
        #Set new field names if game is not finished already
        if self.__field__.finit == 1: return
        for i in range(self.__field__.sizeN):
            for j in range(self.__field__.sizeM):
                if self.__field__.field_closed[i][j] == 0: #if cell == 0 set no icon+gray color
                    self.__grid__.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str('')))
                    self.__grid__.itemAtPosition(i, j).widget().setStyleSheet("background-color: gray")
                else:            
                    self.__grid__.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str(self.__field__.field_closed[i][j])+'.png'))
                    self.__grid__.itemAtPosition(i, j).widget().setStyleSheet("background-color: white")

        #On stage of namesetting let's check if field isn't solved yet
        if self.__field__.is_solved() and self.__field__.finit != 2:
            self.__field__.finit = 1 
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Congratulations!")
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')    
            msgBox.exec_()
   
    def __get_button_action__(self):
        #Open cell action
        if self.__field__.finit == 1: return
        call_button = self.sender()
        
        column, row = self.__grid__.getItemPosition(self.__grid__.indexOf(call_button))[0:2]
        
        self.__field__.defuse_cell(column, row)
        
        #If user opened mine we have to terminate the game
        if self.__field__.finit == 2:
            self.__field__.kill_field()
            self.setNames() 
            self.__field__.finit = 1
            call_button.setStyleSheet("background-color: red")
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')
            msgBox.setText("Failed!")
            msgBox.exec_()
            
        self.setNames() 
    
    def __get_button_toggle__(self):
        #Set flag action
        if self.__field__.finit == 1: return
        call_button = self.sender()
        
        column, row = self.__grid__.getItemPosition(self.__grid__.indexOf(call_button))[0:2]
        self.__field__.mark_cell(column, row)
        self.setNames() 
    
    def __game_start__(self):
        #Let user select difficulty level!
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('M.png'))
        msgBox.setWindowTitle('Minesweeper')
        
        msgBox_layout = msgBox.layout()
        
        groupBox = QtGui.QGroupBox("Выберите сложность")
        radio1 = QtGui.QRadioButton("Новичок")
        radio2 = QtGui.QRadioButton("Любитель")
        radio3 = QtGui.QRadioButton("Профессионал")
        radio1.setChecked(True)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        msgBox_layout.addWidget(groupBox, 0, 0)
        msgBox.exec_()
        
        sizeN, sizeM, mines = 0, 0, 0
        if radio1.isChecked(): sizeN, sizeM, mines = 8, 8, 10
        if radio2.isChecked(): sizeN, sizeM, mines = 16, 16, 40
        if radio3.isChecked(): sizeN, sizeM, mines = 16, 30, 99
        
        #Create a new field
        self.__field__ = MSField(sizeN, sizeM, mines)
        
        #Create central widget for this game and overwrite previous one
        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)
        
        #Create grid and add buttons
        
        self.__grid__ = QtGui.QGridLayout()
        self.__grid__.setSpacing(0)
        
        for i in range(self.__field__.sizeN):
            for j in range(self.__field__.sizeM):
                button = MSButton()
                button.rightClicked.connect(self.__get_button_action__)
                button.leftClicked.connect(self.__get_button_toggle__)
                self.__grid__.addWidget(button, i, j)
        
        self.__console__ = QtGui.QTextEdit()
        self.__console__.hide()
        
        #Starting all things
        
        term_layout = QtGui.QHBoxLayout()
        term_layout.addLayout(self.__grid__)
        term_layout.addWidget(self.__console__)
    
        centralWidget.setLayout(term_layout)
        
        centralWidget.setFixedSize(centralWidget.sizeHint())
        self.setFixedSize(self.sizeHint()+centralWidget.sizeHint())
        self.setNames() 
        self.__field__.print_opened()

    def __bot_start__(self):
        self.__console__.show()
        self.__bot__ = MSBot(self, self.__console__)
        self.centralWidget().setFixedSize(self.centralWidget().sizeHint())
        self.setFixedSize(self.sizeHint())

    def __bot_step__(self):
        if self.__bot__.step1_simple(): return
        if self.__bot__.step2_random(): return
        pass

def initGame():
    app = QtGui.QApplication(sys.argv)
    scr = MSScreen()    
    scr.show()
    app.exec_()
