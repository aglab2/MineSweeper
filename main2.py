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
    field_closed = list()
    sizeN = 0
    sizeM = 0
    __mines__ = 0
    finit = 0
    
    def __init__(self, sizeN, sizeM, mines):
        if mines > sizeN*sizeM:
            raise Exception('To many mines for this field size')
        #Initiate field and properties of fields
        mine_field = ['M']*mines + [0]*(sizeN*sizeM-mines) #mines+free spaces
        random.shuffle(mine_field)
        self.sizeN = sizeN
        self.sizeM = sizeM
        self.__mines__ = mines
        self.finit = 0
        self.__field_opened__ = [mine_field[self.sizeM*i:self.sizeM*(i+1)] for i in range(self.sizeN)] 
        self.field_closed = [['C']*(self.sizeM) for i in range(self.sizeN)] #all field are closed('C')
        
        #Count number of mines
        for x in range(self.sizeN):
            for y in range(self.sizeM):
                if self.__field_opened__[x][y] == 'M': continue
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                        if (self.__field_opened__[x_next][y_next] == 'M'): self.__field_opened__[x][y] += 1
    
    #Debug print methods
    def print_opened(self):
        for i in range(self.sizeN):
            info_str = ''
            for j in range(self.sizeM):
                info_str += str(self.__field_opened__[i][j])
            logging.info(info_str)
        logging.info('')

    def print_closed(self):
        for i in range(self.sizeN):
            info_str = ''
            for j in range(self.sizeM):
                info_str += str(self.field_closed[i][j])
            logging.info(info_str)
        logging.info('')
            
    def is_solved(self):
        #Check if field contain any closed numbers
        
        for i in range(self.sizeN):
            for j in range(self.sizeM):
                if self.field_closed[i][j] != self.__field_opened__[i][j] and self.__field_opened__[i][j] !='M':
                    return False
        return True 
    
    def defuse_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        logging.debug('    closed: {}'.format(self.field_closed[x][y]))
        logging.debug('    opened: {}'.format(self.__field_opened__[x][y]))
        
        #Check whether current field is full
        if self.field_closed[x][y] != 'C' and self.field_closed[x][y] != 'F':
            mines, frees = self.caim_prop(x, y)
            if mines == self.field_closed[x][y]:
                self.mine_cell(x, y)  
            elif frees + mines == self.field_closed[x][y]:
                self.free_cell(x, y)
        else:
            self.__open_cell__(x, y)
    
    def mine_cell(self, x, y):
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                if self.field_closed[x_next][y_next] != 'F': self.__open_cell__(x_next, y_next)

    def free_cell(self, x, y):
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                if self.field_closed[x_next][y_next] == 'C': self.field_closed[x_next][y_next] = 'F'
    
    def __open_cell__(self, x, y):
        #Open number and if num=0 call dfs on field
        if self.__field_opened__[x][y] == 'M': self.finit = 2
        if self.__field_opened__[x][y] == 0:
            self.__cell_dfs__(x, y, set())
        else:
            self.field_closed[x][y] = self.__field_opened__[x][y]
    
    def __cell_dfs__(self, x, y, used):
        logging.info('Started with ({}, {})'.format(x, y))
        #Add cell to used if it is not already there
        if (x, y) in used: return 
        used.add((x, y))
        #Open cell and call dfs from surrounding fields
        self.field_closed[x][y] = self.__field_opened__[x][y]

        if self.field_closed[x][y] != 0: return 
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                self.__cell_dfs__(x_next, y_next, used)
        
    def mark_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        
        #Set flag or unset flag
        if self.field_closed[x][y] == 'C': self.field_closed[x][y] = 'F'
        elif self.field_closed[x][y] == 'F': self.field_closed[x][y] = 'C'
    
    def caim_prop(self, x, y):
        mines = 0
        frees = 0
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                if self.field_closed[x_next][y_next] == 'F': mines += 1
                if self.field_closed[x_next][y_next] == 'C': frees += 1
        return (mines, frees) 

    def kill_field(self):
        for x in range(self.sizeN):
            for y in range(self.sizeM):
                if self.field_closed[x][y] == 'C':
                    self.field_closed[x][y] = self.__field_opened__[x][y]
                elif self.field_closed[x][y] == 'F' and self.__field_opened__[x][y] != 'M':
                    self.field_closed[x][y] = 'P'
                    

class MSBot():
    __screen__ = None
    __console__ = None

    def __init__(self, screen, console):
        self.__screen__  = screen
        self.__console__ = console
    
    def step1_simple(self):
        field = self.__screen__.__field__
        
        self.__console__.append('Start m&f brutforcing')
        for x in range(field.sizeN):
            for y in range(field.sizeM):
                if field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if frees == 0: continue
                if mines == field.field_closed[x][y]:
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: yellow")
                    self.__console__.append('    Success: props ({}, {})'.format(mines, frees))
                    return True
                elif frees+mines == field.field_closed[x][y]:
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: yellow")
                    self.__console__.append('    Success: props ({}, {})'.format(mines, frees))
                    return True
        self.__console__.append('m&f Brutforce failed')
        return False
    
    def step2_random(self):
        field = self.__screen__.__field__
        
        assist = [[0.0] * (field.sizeM) for y in range(field.sizeM)] #all field are closed('C')
        self.__console__.append('Start r&a brutforcing')
        for x in range(field.sizeN):
            for y in range(field.sizeM):
                if type(field.field_closed[x][y]) != int or field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if mines == field.field_closed[x][y] and frees == 0: continue
                probability = (field.field_closed[x][y] - mines) / frees
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(field.sizeN) and y_next in range(field.sizeM):
                        if (field.field_closed[x_next][y_next] == 'C'): assist[x_next][y_next] += probability
        
        max_probability = 0
        max_cells = list()
        
        min_probability = 10000
        min_cells = list()
        
        for x in range(field.sizeN):
            for y in range(field.sizeM):
                if field.field_closed[x][y] != 'C': continue
                
                if (assist[x][y] - max_probability) > 0.00000001: 
                    max_probability = assist[x][y]
                    max_cells = list()
                if abs(assist[x][y] - max_probability) < 0.00000001: max_cells.append((x, y))
                
                if (assist[x][y] - min_probability) < -0.00000001: 
                    min_probability = assist[x][y]
                    min_cells = list()
                if abs(assist[x][y] - min_probability) < 0.00000001: min_cells.append((x, y))
        
        self.__console__.append('    ({}, {}):'.format(min_probability, max_probability))
        
        if max_probability > 1.33:
            self.__console__.append('    Mine found!:')
            self.__console__.append('    From {} cells'.format(len(max_cells)))
            (x, y) = random.choice(max_cells)
            self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
            self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: pink")
        else:
            self.__console__.append('    Free found!:')
            self.__console__.append('    From {} cells'.format(len(min_cells)))
            (x, y) = random.choice(min_cells)
            self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
            self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: pink")

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
 
def main():
    logging.basicConfig(filename = 'minesweeper.log', level=logging.DEBUG, format='(%(funcName)s) %(message)s')
    logging.disable(level=logging.INFO)
    app = QtGui.QApplication(sys.argv)
    scr = MSScreen()    
    scr.show()
    app.exec_()
    
if __name__ == '__main__':
    main()
        