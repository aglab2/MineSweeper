import random
import logging
import sys
from PySide import QtGui, QtCore

caim = {0:[1,1], 1:[1,0], 2:[1,-1], 3:[0,1], 4:[0,-1], 5:[-1,1], 6:[-1,0], 7:[-1,-1]}

class MSButton(QtGui.QPushButton):
    rightClicked = QtCore.Signal()
    leftClicked = QtCore.Signal()
    
    def __init__(self):
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
    __size__ = 0
    __mine__ = 0
    __fini__ = 0
    
    def __init__(self, size, mine):
        if mine > size*size:
            raise Exception('To many mines for this field size')
        mine_field = ['M']*mine + [0]*(size**2-mine)
        random.shuffle(mine_field)
        self.__size__ = size
        self.__mine__ = mine
        self.__fini__ = 0
        self.__field_opened__ = [mine_field[self.__size__*i:self.__size__*(i+1)] for i in range(self.__size__)]
        self.__field_closed__ = [['C']*(self.__size__) for i in range(self.__size__)]
        
        for i in range(self.__size__):
            for j in range(self.__size__):
                if self.__field_opened__[i][j] == -1: continue
                for k in range(8):
                    if i+caim[k][0] in range(self.__size__) and j+caim[k][1] in range(self.__size__):
                        try:
                            if (self.__field_opened__[i+caim[k][0]][j+caim[k][1]] == 'M') : self.__field_opened__[i][j] += 1
                        except Exception: pass
        
    def print_opened(self):
        for i in range(self.__size__):
            info_str = ''
            for j in range(self.__size__):
                info_str += str(self.__field_opened__[i][j])
            logging.info(info_str)

    def print_closed(self):
        for i in range(self.__size__):
            info_str = ''
            for j in range(self.__size__):
                info_str += str(self.__field_closed__[i][j])
            logging.info(info_str)
            
    def is_solved(self):
        for i in self.__field_closed__: 
            if 'C' in i: return False
        return True 
    
    def open_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        logging.debug('    closed: {}'.format(self.__field_closed__[x][y]))
        logging.debug('    opened: {}'.format(self.__field_opened__[x][y]))
        if self.__field_closed__[x][y] != 'C' and self.__field_closed__[x][y] != 'F': return
        if self.__field_opened__[x][y] == 0:
            self.__cell_dfs__(x, y, set())
        else:
            self.__field_closed__[x][y] = self.__field_opened__[x][y]
                
    
    def __cell_dfs__(self, x, y, used):
        logging.debug('Started with ({}, {})'.format(x, y))
        if (x, y) in used: return 
        used.add((x, y))
        self.__field_closed__[x][y] = self.__field_opened__[x][y]

        if self.__field_closed__[x][y] != 0: return 
        for i in range(8):
            x_next, y_next = x+caim[i][0], y+caim[i][1]
            if x_next in range(self.__size__) and y_next in range(self.__size__):
                self.__cell_dfs__(x_next, y_next, used)
        
    def mark_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        logging.debug('    closed: {}'.format(self.__field_closed__[x][y]))
        logging.debug('    opened: {}'.format(self.__field_opened__[x][y]))

        if self.__field_closed__[x][y] == 'C': self.__field_closed__[x][y] = 'F'
        elif self.__field_closed__[x][y] == 'F': self.__field_closed__[x][y] = 'C'


class MSScreen(QtGui.QMainWindow):
    __field__ = MSField(8, 10)
    
    def __init__(self):
        super(MSScreen, self).__init__()
        self.__initUI__()
        
    def __initUI__(self):
        centralWidget = QtGui.QWidget()
        self.setCentralWidget(centralWidget)
        
        exitAction = QtGui.QAction('Выход', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из приложения')
        exitAction.triggered.connect(self.close)
        
        startAction = QtGui.QAction('Начать', self)
        startAction.setShortcut('Ctrl+S')
        startAction.setStatusTip('Начать приложение')
        startAction.triggered.connect(self.__game_start__)
        
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Меню')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(startAction)
        
        self.setWindowTitle('Minesweeper')
        self.setWindowIcon(QtGui.QIcon('M.png'))
        self.show()
            
    def setNames(self, names):
        if self.__field__.__fini__ == 1: return
        grid = self.centralWidget().layout()
        for i in range(self.__field__.__size__):
            for j in range(self.__field__.__size__):
                if names[i][j] == 0:
                    grid.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str('')))
                    grid.itemAtPosition(i, j).widget().setStyleSheet("background-color: gray")
                else:            
                    grid.itemAtPosition(i, j).widget().setIcon(QtGui.QIcon(str(names[i][j])+'.png'))
                    grid.itemAtPosition(i, j).widget().setStyleSheet("background-color: white")

        if self.__field__.is_solved():
            self.__field__.__fini__ = 1 
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Congratulations!")
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')    
            msgBox.exec_()
        else:
            logging.debug("Not solved yet...")
        
    def __get_button_action__(self):
        if self.__field__.__fini__ == 1: return
        call_button = self.sender()
        grid = self.centralWidget().layout()
        
        column, row = grid.getItemPosition(grid.indexOf(call_button))[0:2]
        if self.__field__.__field_opened__[column][row] == 'M':
                self.setNames(self.__field__.__field_opened__) 
                self.__field__.__fini__ = 1
                call_button.setStyleSheet("background-color: red")
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowIcon(QtGui.QIcon('M.png'))
                msgBox.setWindowTitle('Minesweeper')
                msgBox.setText("Failed!")
                msgBox.exec_()
                return
        
        self.__field__.open_cell(column, row)
        self.setNames(self.__field__.__field_closed__) 
    
    def __get_button_toggle__(self):
        if self.__field__.__fini__ == 1: return
        call_button = self.sender()
        grid = self.centralWidget().layout()
        
        column, row = grid.getItemPosition(grid.indexOf(call_button))[0:2]
        self.__field__.mark_cell(column, row)
        self.setNames(self.__field__.__field_closed__) 
    
    def __game_start__(self):
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
        
        size, mines = 0, 0
        if radio1.isChecked(): size, mines = 8, 10
        if radio2.isChecked(): size, mines = 16, 40
        if radio3.isChecked(): size, mines = 30, 100
        
        print(size, mines)
        
        self.__field__ = MSField(size, mines)
        
        centralWidget = self.centralWidget()
        grid = QtGui.QGridLayout()
        grid.setSpacing(0)
        
        for i in range(self.__field__.__size__):
            for j in range(self.__field__.__size__):
                button = MSButton()
                button.rightClicked.connect(self.__get_button_action__)
                button.leftClicked.connect(self.__get_button_toggle__)
                grid.addWidget(button, i, j)
        
        centralWidget.setLayout(grid)
        self.setNames(self.__field__.__field_closed__) 
        
        self.__field__.print_opened()
            
def main():
    logging.basicConfig(level=logging.DEBUG, format='(%(funcName)s) %(message)s')
    app = QtGui.QApplication(sys.argv)
    screen = MSScreen()    
    app.exec_()
    
if __name__ == '__main__':
    main()
        