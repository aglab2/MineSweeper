from PySide import QtGui
import sys
import threading
import time

from MSField    import MSField
from MSButton   import MSButton
from MSBot      import MSBot

class MSScreen(QtGui.QMainWindow):
    __field__ = None
    __bot__ = None
    __grid__ = None
    __console__ = None
    __val_mnf__ = None
    __val_rna__ = None
    __val_fne__ = None
    __autobot__ = None
    __botstep__ = None
    __timer__ = 0
    
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
        self.__botstep__ = botStep
        
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
        #Set new fieldf names if game is not finished already
        if (self.__game_finished__()): return 
        
        for i in range(self.__field__.sizeN):
            for j in range(self.__field__.sizeM):
                if self.__field__.field_closed[i][j] == 0: #if cell == 0 set no icon+gray color
                    self.__grid__.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str('')))
                    self.__grid__.itemAtPosition(i, j).widget().setStyleSheet("background-color: gray")
                else:            
                    self.__grid__.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str(self.__field__.field_closed[i][j])+'.png'))
                    self.__grid__.itemAtPosition(i, j).widget().setStyleSheet("background-color: white")

   
    def __get_button_action__(self):
        #Open cell action
        if self.__field__.finit == 1: return
        call_button = self.sender()
        
        column, row = self.__grid__.getItemPosition(self.__grid__.indexOf(call_button))[0:2]
        
        if self.__field__.__field_opened__[column][row] != 0 and self.__field__.finit == -1:
            sizeN = self.__field__.sizeN
            sizeM = self.__field__.sizeM
            mines = self.__field__.__mines__
            while self.__field__.__field_opened__[column][row] != 0:
                self.__field__ = MSField(sizeN, sizeM, mines)
        self.__field__.finit = 0
        
        self.__field__.defuse_cell(column, row)
        
        if self.__field__.finit == 2:
            percentage = round(self.__field__.kill_field()/self.__field__.sizeM/self.__field__.sizeN*100)
            self.setNames() 
            self.__field__.finit = 1
            call_button.setStyleSheet("background-color: red")
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')
            msgBox.setText("Failed! You blew up in {} seconds. You have opened {}% of field".format(round(time.time() - self.__timer__,2), percentage))
            msgBox.exec_()
            return True

        #If user opened mine we have to terminate the game

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
        
        vbox2 = QtGui.QVBoxLayout()
        self.__val_mnf__ = QtGui.QLabel('Number of m&f: 0')
        #self.__val_fne__ = QtGui.QLabel('Number of f&e: 0')
        self.__val_rna__ = QtGui.QLabel('Number of r&a: 0')
        self.__console__ = QtGui.QTextEdit()
        self.__autobot__ = QtGui.QPushButton('Auto-Bot')
        self.__autobot__.clicked.connect(self.__start_autobot__)
        
        vbox2.addWidget(self.__val_mnf__)
        #vbox2.addWidget(self.__val_fne__)
        vbox2.addWidget(self.__val_rna__)
        vbox2.addWidget(self.__console__)
        vbox2.addWidget(self.__autobot__)
        
        self.__console__.hide()
        self.__val_mnf__.hide()
        #self.__val_fne__.hide()
        self.__val_rna__.hide()
        self.__autobot__.hide()
        #Starting all things
        
        term_layout = QtGui.QHBoxLayout()
        term_layout.addLayout(self.__grid__)
        term_layout.addLayout(vbox2)
    
        centralWidget.setLayout(term_layout)
        
        centralWidget.setFixedSize(centralWidget.sizeHint())
        self.setFixedSize(self.sizeHint()+centralWidget.sizeHint())
        self.setNames() 
        self.__field__.print_opened()
        self.__timer__ = time.time()
    
    def __bot_start__(self):
        self.__console__.show()
        self.__val_mnf__.show()
        self.__val_rna__.show()
        #self.__val_fne__.show()
        self.__autobot__.show()
        
        self.__bot__ = MSBot(self)
        self.centralWidget().setFixedSize(self.centralWidget().sizeHint())
        self.setFixedSize(self.sizeHint())

    def __bot_step__(self):
        if self.__bot__.step1_mnf(): return
        if self.__bot__.step2_rna(): return
        if self.__bot__.step3_start(): return

    def __game_finished__(self):
        if self.__field__.finit == 1: return True
            
        if self.__field__.is_solved() and self.__field__.finit != 2:
            self.__field__.finit = 1 
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Congratulations! You have succeeded in {} seconds".format(round(time.time() - self.__timer__),2))
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')    
            msgBox.exec_()
            return True
        return False
    
    def __start_autobot__(self):
        period = 0.5
        def repeat():
            if self.__field__.finit <= 0:
                threading.Timer(period, repeat).start()
                self.__botstep__.triggered.emit()
        if self.__field__.finit <= 0: repeat()
        

def initGame():
    app = QtGui.QApplication(sys.argv)
    scr = MSScreen()    
    scr.show()
    app.exec_()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")