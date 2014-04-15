import random
import logging
import sys
from PySide import QtGui, QtCore

class MSButton(QtGui.QPushButton):
    #Let's catch left and right mouse click
    rightClicked = QtCore.Signal()
    leftClicked = QtCore.Signal()
    
    def __init__(self):
        #Init button with fixed size
        super(MSButton, self).__init__()
        self.setFixedSize(35, 35)
        
    def mousePressEvent(self,event):
        if   event.button() == QtCore.Qt.LeftButton:
            logging.debug('Left button pressed')
            self.rightClicked.emit()
        elif event.button() == QtCore.Qt.RightButton:
            logging.debug('Right button pressed')
            self.leftClicked.emit()
        
class MSField():
    __field_opened__ = list()
    __field_closed__ = list()
    __sizeN__ = 0
    __sizeM__ = 0
    __mines__ = 0
    __finit__ = 0
    
    def __init__(self, sizeN, sizeM, mines):
        if mines > sizeN*sizeM:
            raise Exception('To many mines for this field size')
        #Initiate field and properties of fields
        mine_field = ['M']*mines + [0]*(sizeN*sizeM-mines) #mines+free spaces
        random.shuffle(mine_field)
        self.__sizeN__ = sizeN
        self.__sizeM__ = sizeM
        self.__mines__ = mines
        self.__finit__ = 0
        self.__field_opened__ = [mine_field[self.__sizeM__*i:self.__sizeM__*(i+1)] for i in range(self.__sizeN__)] 
        self.__field_closed__ = [['C']*(self.__sizeM__) for i in range(self.__sizeN__)] #all field are closed('C')
        
        #Count number of mines
        for x in range(self.__sizeN__):
            for y in range(self.__sizeM__):
                if self.__field_opened__[x][y] == 'M': continue
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(self.__sizeN__) and y_next in range(self.__sizeM__):
                        if (self.__field_opened__[x_next][y_next] == 'M'): self.__field_opened__[x][y] += 1
    
    #Debug print methods
    def print_opened(self):
        for i in range(self.__sizeN__):
            info_str = ''
            for j in range(self.__sizeM__):
                info_str += str(self.__field_opened__[i][j])
            logging.info(info_str)
        logging.info('')

    def print_closed(self):
        for i in range(self.__sizeN__):
            info_str = ''
            for j in range(self.__sizeM__):
                info_str += str(self.__field_closed__[i][j])
            logging.info(info_str)
        logging.info('')
            
    def is_solved(self):
        #Check if field contain any closed numbers
        
        for i in range(self.__sizeN__):
            for j in range(self.__sizeM__):
                if self.__field_closed__[i][j] != self.__field_opened__[i][j] and self.__field_opened__[i][j] !='M':
                    return False
        return True 
    
    def defuse_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        logging.debug('    closed: {}'.format(self.__field_closed__[x][y]))
        logging.debug('    opened: {}'.format(self.__field_opened__[x][y]))
        
        #Check whether current field is full
        if self.__field_closed__[x][y] != 'C' and self.__field_closed__[x][y] != 'F': 
            if self.caim_prop(x, y)[0] == self.__field_closed__[x][y]:
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(self.__sizeN__) and y_next in range(self.__sizeM__):
                        if self.__field_closed__[x_next][y_next] != 'F': self.__open_cell__(x_next, y_next)
        else:
            self.__open_cell__(x, y)
    
    def __open_cell__(self, x, y):
        #Open number and if num=0 call dfs on field
        if self.__field_opened__[x][y] == 'M': self.__finit__ = 2
        if self.__field_opened__[x][y] == 0:
            self.__cell_dfs__(x, y, set())
        else:
            self.__field_closed__[x][y] = self.__field_opened__[x][y]
    
    def __cell_dfs__(self, x, y, used):
        logging.debug('Started with ({}, {})'.format(x, y))
        #Add cell to used if it is not already there
        if (x, y) in used: return 
        used.add((x, y))
        #Open cell and call dfs from surrounding fields
        self.__field_closed__[x][y] = self.__field_opened__[x][y]

        if self.__field_closed__[x][y] != 0: return 
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.__sizeN__) and y_next in range(self.__sizeM__):
                self.__cell_dfs__(x_next, y_next, used)
        
    def mark_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        
        #Set flag or unset flag
        if self.__field_closed__[x][y] == 'C': self.__field_closed__[x][y] = 'F'
        elif self.__field_closed__[x][y] == 'F': self.__field_closed__[x][y] = 'C'
    
    def caim_prop(self, x, y):
        mines = 0
        frees = 0
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.__sizeN__) and y_next in range(self.__sizeM__):
                if self.__field_closed__[x_next][y_next] == 'F': mines += 1
                if self.__field_closed__[x_next][y_next] == 'C': frees += 1
        return (mines, frees)         

class MSAI():
    __field__ = MSField(0, 0, 0)
    
    def step1_mine(self):
        logging.debug('Start mine brutforcing')
        for i in range(self.__sizeN__):
            for j in range(self.__sizeM__):
                pass
    
    def __initUI__(self, field):
        self.__field__ = field
        pass        

class MSScreen(QtGui.QMainWindow):
    __field__ = MSField(0, 0, 0)
    
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
        startAction.setShortcut('Ctrl+S')
        startAction.setStatusTip('Начать приложение')
        startAction.triggered.connect(self.__game_start__)
        
        #Initiate menu
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Меню')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(startAction)
        
        self.setWindowTitle('Minesweeper')
        self.setWindowIcon(QtGui.QIcon('M.png'))
            
    def setNames(self, names):
        #Set new field names if game is not finished already
        if self.__field__.__finit__ == 1: return
        grid = self.centralWidget().layout()
        for i in range(self.__field__.__sizeN__):
            for j in range(self.__field__.__sizeM__):
                if names[i][j] == 0: #if cell == 0 set no icon+gray color
                    grid.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str('')))
                    grid.itemAtPosition(i, j).widget().setStyleSheet("background-color: gray")
                else:            
                    grid.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str(names[i][j])+'.png'))
                    grid.itemAtPosition(i, j).widget().setStyleSheet("background-color: white")

        #On stage of namesetting let's check if field isn't solved yet
        if self.__field__.is_solved() and self.__field__.__finit__ != 2:
            self.__field__.__finit__ = 1 
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Congratulations!")
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')    
            msgBox.exec_()

        
    def __get_button_action__(self):
        #Open cell action
        if self.__field__.__finit__ == 1: return
        call_button = self.sender()
        grid = self.centralWidget().layout()
        
        column, row = grid.getItemPosition(grid.indexOf(call_button))[0:2]
        
        self.__field__.defuse_cell(column, row)
        
        #If user opened mine we have to terminate the game
        if self.__field__.__finit__ == 2:
            self.setNames(self.__field__.__field_opened__) 
            self.__field__.__finit__ = 1
            call_button.setStyleSheet("background-color: red")
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')
            msgBox.setText("Failed!")
            msgBox.exec_()
            
        self.setNames(self.__field__.__field_closed__) 
    
    def __get_button_toggle__(self):
        #Set flag action
        if self.__field__.__finit__ == 1: return
        call_button = self.sender()
        grid = self.centralWidget().layout()
        
        column, row = grid.getItemPosition(grid.indexOf(call_button))[0:2]
        self.__field__.mark_cell(column, row)
        self.setNames(self.__field__.__field_closed__) 
    
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
        
        #self.resize(35*sizeM, 35*sizeN)
        
        #Create grid and add buttons
        grid = QtGui.QGridLayout()
        grid.setSpacing(0)
        
        for i in range(self.__field__.__sizeN__):
            for j in range(self.__field__.__sizeM__):
                button = MSButton()
                button.rightClicked.connect(self.__get_button_action__)
                button.leftClicked.connect(self.__get_button_toggle__)
                grid.addWidget(button, i, j)
        
        #Starting all things
        centralWidget.setLayout(grid)
        centralWidget.setFixedSize(centralWidget.sizeHint())
        #self.resize(centralWidget.sizeHint())
        self.setFixedSize(centralWidget.sizeHint()+self.sizeHint())
        self.setNames(self.__field__.__field_closed__) 
        self.__field__.print_opened()
      
def main():
    logging.basicConfig(level=logging.DEBUG, format='(%(funcName)s) %(message)s')
    app = QtGui.QApplication(sys.argv)
    scr = MSScreen()    
    scr.show()
    app.exec_()
    
if __name__ == '__main__':
    main()
        