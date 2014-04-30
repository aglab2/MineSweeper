from PySide import QtGui, QtCore
import sys
import time
import threading
import logging
from multiprocessing import Queue #@UnresolvedImport
from MSField import MSField
from MSButton import MSButton
from MSBot import MSBot
from MSScoreboard import MSScoreboard

class Connectors(QtCore.QObject):
    console_signal = QtCore.Signal(str)
    button_signal = QtCore.Signal(int, int, str)

class Repeater(threading.Thread):
    def __init__(self, screen, queue, period = 0.1):
        threading.Thread.__init__(self)
        self.setName('Repeater')
        self._screen = screen
        self._period = period
        self._run = True
        self._queue = queue
    
    def run(self):
        logging.info('Started')
        while self._run and self._screen._field.finit <= 0:
            try:
                self._screen._bot_thread.join()
            except Exception: pass
            self._screen._botstep.triggered.emit()
            try:
                self._screen._bot_thread.join()
            except Exception: pass
            while not self._queue.empty():
                time.sleep(self._period / 10)
            time.sleep(self._period)
            logging.info('Rewind!')
        logging.info('Stopped')
        
    def stop(self):
        self._run = False

class QueueHandler(threading.Thread):
    def __init__(self, queue, screen):
        threading.Thread.__init__(self)
        self.setName('Queue')
        self._queue = queue
        self._connectors = Connectors()
        self._working = True
        self._screen = screen
    
    def run(self):
        while self._working:
            while not self._queue.empty():
                ask = self._queue.get()
                if ask[0] == 'console':
                    self._connectors.console_signal.emit(ask[1])
                elif ask[0] == 'pressR':
                    self._screen._grid.itemAtPosition(ask[1][0], ask[1][1]).widget().right_clicked.emit()
                elif ask[0] == 'pressL':
                    self._screen._grid.itemAtPosition(ask[1][0], ask[1][1]).widget().left_clicked.emit()
                elif ask[0] == 'update':
                    if ask[1] == 0:
                        self._screen._mnf += 1
                        self._screen._val_mnf.setText('Number of m&f: {}'.format(self._screen._mnf))
                    elif ask[1] == 1:
                        self._screen._tnc_bp += 1
                        self._screen._val_tnc_bp.setText('Number of t&c bp: {}'.format(self._screen._tnc_bp)) 
                    elif ask[1] == 2:
                        self._screen._tnc_rd += 1
                        self._screen._val_tnc_rd.setText('Number of t&c rd: {}'.format(self._screen._tnc_rd))
                    elif ask[1] == 3:
                        self._screen._rna += 1
                        self._screen._val_rna.setText('Number of r&a: {}'.format(self._screen._rna))                
                else:
                    self._connectors.console_signal.emit('Unknown signal arrived!') 
            
            time.sleep(0.1)
         
    def stop(self): 
        self._working = False         
        
class MSScreen(QtGui.QMainWindow):  
    def __init__(self):
        """Constructor"""
        super(MSScreen, self).__init__()
        self._initUI()
        
    def _initUI(self):
        """Set menubar, name and icons"""
        exitAction = QtGui.QAction('Quit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit the application')
        exitAction.triggered.connect(self.close)
        
        startAction = QtGui.QAction('Begin', self)
        startAction.setShortcut('Ctrl+N')
        startAction.setStatusTip('Begin the application')
        startAction.triggered.connect(self._game_start)
        
        botAction = QtGui.QAction('Bot', self)
        botAction.setShortcut('Ctrl+B')
        botAction.setStatusTip('Turn on the bot')
        botAction.triggered.connect(self._bot_start)
        
        botStep = QtGui.QAction('Step', self)
        botStep.setShortcut('Ctrl+S')
        botStep.setStatusTip('Make next bot step')
        botStep.triggered.connect(self._bot_step)
        self._botstep = botStep
        
        #testBotAction = QtGui.QAction('Тест', self)        
        #testBotAction.setShortcut('Ctrl+T')
        #testBotAction.setStatusTip('Собрать статистику на выбранном уровне')
        #testBotAction.triggered.connect(self.__test_bot__)
        
        scoreAction = QtGui.QAction('Results', self)
        scoreAction.setShortcut('Ctrl+R')
        scoreAction.setStatusTip('Show results')
        scoreAction.triggered.connect(self._load_scoreboard)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Menu')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(startAction)
        
        cheatMenu = menubar.addMenu('Cheats')
        cheatMenu.addAction(botAction)
        cheatMenu.addAction(botStep)
        
        helpMenu = menubar.addMenu('Help')
        helpMenu.addAction(scoreAction)
        #helpMenu.addAction(testBotAction)

        self.setWindowTitle('Minesweeper')
        self.setWindowIcon(QtGui.QIcon('M.png'))
        self._queue = Queue()
        self._queue_handler = QueueHandler(self._queue, self)
        self._queue_handler._connectors.console_signal.connect(self.console_append, QtCore.Qt.QueuedConnection)
        self._queue_handler.start()
    
    def set_names(self, i, j, val):
        if (self._game_finished()): return 

        """Set new field names if game is not finished already"""
        if (self._game_finished()): return 
        
        cur_button = self._grid.itemAtPosition(i, j).widget()
        cur_geom = cur_button.geometry()
        icon_size = QtCore.QSize(cur_geom.width()*3/4, cur_geom.height()*3/4)
                
        if self._field.field_closed[i][j] == 0: #if cell == 0 set no icon+gray color
            cur_button.setIcon(QtGui.QIcon(str('')))
            cur_button.setIconSize(icon_size)
            cur_button.setStyleSheet("background-color: gray")
        else:            
            cur_button.setIcon(QtGui.QIcon(str(self._field.field_closed[i][j])+'.png'))
            cur_button.setIconSize(icon_size)
            cur_button.setStyleSheet("background-color: white")

   
    def _get_button_action(self):
        """Open cell action"""
        if self._field.finit == 1: return
        call_button = self.sender()
        
        column, row = self._grid.getItemPosition(self._grid.indexOf(call_button))[0:2]
        
        if self._field._field_opened[column][row] != 0 and self._field.finit == -1:
            sizen = self._field.sizen
            sizem = self._field.sizem
            mines = self._field.mines
            while self._field._field_opened[column][row] != 0:
                self._field = MSField(sizen, sizem, mines, self)
        self._field.finit = 0
        
        self._field.defuse_cell(column, row)
        
        if self._field.finit == 2:
            percentage = round(self._field.kill_field()/self._field.sizem/self._field.sizen*100)
            self._field.finit = 1
            call_button.setStyleSheet("background-color: red")

            sb = MSScoreboard()
            state = 0
            if self._field.sizem == 16: state = 1
            if self._field.sizem == 30: state = 2
            sb.add_level(state, 0, percentage)
            
            msgBox = QtGui.QMessageBox()
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')
            msgBox.setText("Failed! You blew up in {} seconds. You have opened {}% of field".format(round(time.time() - self._timer,2), percentage))
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Reset)  
            ret = msgBox.exec_()
            if (ret == QtGui.QMessageBox.Reset):
                self._new_field_create(self._field.sizen, self._field.sizem, self._field.mines)
            return True 
    
    def _get_button_toggle(self):
        """Set flag action"""
        if self._field.finit == 1: return
        call_button = self.sender()
        column, row = self._grid.getItemPosition(self._grid.indexOf(call_button))[0:2]
        self._field.mark_cell(column, row)
    
    def _game_start(self):
        """Difficulty selection"""
        self.__botstate__ = 0
        msgBox = QtGui.QMessageBox()
        msgBox.setWindowIcon(QtGui.QIcon('M.png'))
        msgBox.setWindowTitle('Minesweeper')
        
        msgBox_layout = msgBox.layout()
        
        groupBox = QtGui.QGroupBox("Choose difficulty")
        radio1 = QtGui.QRadioButton("Beginner")
        radio2 = QtGui.QRadioButton("Intermediate")
        radio3 = QtGui.QRadioButton("Professional")
        radio1.setChecked(True)
        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(radio1)
        vbox.addWidget(radio2)
        vbox.addWidget(radio3)
        vbox.addStretch(1)
        groupBox.setLayout(vbox)
        msgBox_layout.addWidget(groupBox, 0, 0)
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)
        ret = msgBox.exec_()
        
        if (ret == QtGui.QMessageBox.Ok):
            sizen, sizem, mines = 0, 0, 0
            if radio1.isChecked(): sizen, sizem, mines = 8, 8, 10
            if radio2.isChecked(): sizen, sizem, mines = 16, 16, 40
            if radio3.isChecked(): sizen, sizem, mines = 16, 30, 99
            self._new_field_create(sizen, sizem, mines)
    
    def _new_field_create(self, sizen, sizem, mines):
        """Create a new field or replace the old one"""
        self._field = MSField(sizen, sizem, mines, self)
        
        #Create central widget for this game and overwrite previous one
        central_widget = QtGui.QWidget()
        self.setCentralWidget(central_widget)
        
        #Create grid and add buttons
        self._grid = QtGui.QGridLayout()
        self._grid.setSpacing(0)
        
        for i in range(self._field.sizen):
            for j in range(self._field.sizem):
                button = MSButton()
                button.right_clicked.connect(self._get_button_action)
                button.left_clicked.connect(self._get_button_toggle)
                self._grid.addWidget(button, i, j)
                self.set_names(i, j, 'C')
        
        vbox2 = QtGui.QVBoxLayout()
        self._val_mnf = QtGui.QLabel('Number of m&f: 0')
        self._val_tnc_bp = QtGui.QLabel('Number of t&c bp: 0')
        self._val_tnc_rd = QtGui.QLabel('Number of t&c rd: 0')
        self._val_rna = QtGui.QLabel('Number of r&a: 0')
        self._console = QtGui.QPlainTextEdit()
        self._console.setFixedWidth(QtGui.QDesktopWidget().availableGeometry().width() / 5)
        self._autobot = QtGui.QPushButton('Auto-Bot')
        self._autobot.clicked.connect(self._start_autobot)
        
        vbox2.addWidget(self._val_mnf)
        vbox2.addWidget(self._val_tnc_bp)
        vbox2.addWidget(self._val_tnc_rd)
        vbox2.addWidget(self._val_rna)
        vbox2.addWidget(self._console)
        vbox2.addWidget(self._autobot)
        
        self._console.hide()
        self._val_mnf.hide()
        self._val_tnc_bp.hide()
        self._val_tnc_rd.hide()
        self._val_rna.hide()
        self._autobot.hide()
        #Starting all things
        
        term_layout = QtGui.QHBoxLayout()
        term_layout.addLayout(self._grid)
        term_layout.addLayout(vbox2)
    
        central_widget.setLayout(term_layout)
        
        central_widget.setFixedSize(central_widget.sizeHint())
        self.setFixedSize(self.sizeHint()+central_widget.sizeHint())
        self._field.print_opened()        
        self._timer = time.time()
    
    def _bot_start(self):
        """Show all the components of bot and start the game"""
        self._console.show()
        self._val_mnf.show()
        self._val_tnc_bp.show()
        self._val_tnc_rd.show()
        self._val_mnf.show()
        self._val_rna.show()
        self._autobot.show()
        
        self._bot_work = False
        
        self.centralWidget().setFixedSize(self.centralWidget().sizeHint())
        self.setFixedSize(self.sizeHint())
        self._bot_thread = MSBot(self, self._queue, self)
        self._autobot_thread = Repeater(self, self._queue, 0.1)
        self._autobot_thread._run = False
        
        self._mnf = 0
        self._tnc_bp = 0
        self._tnc_rd = 0
        self._rna = 0
        
        #self.__botstate__ = 0

    def _bot_step(self):
        """Start bot thread"""
        if not self._bot_thread.is_alive():
            self._bot_thread = MSBot(self, self._queue, self)
            self._bot_thread.start()

    def _game_finished(self):
        """Check if game finished and finish game if field is solved"""
        if self._field.finit == 1: return True
            
        if self._field.is_solved() and self._field.finit != 2:
            self._field.finit = 1 
            
            sb = MSScoreboard()
            state = 0
            if self._field.sizem == 16: state = 1
            if self._field.sizem == 30: state = 2
            sb.add_level(state, 1, 100)
            
            msgBox = QtGui.QMessageBox()
            msgBox.setText("Congratulations! You have succeeded in {} seconds".format(round(time.time() - self._timer, 2)))
            msgBox.setWindowIcon(QtGui.QIcon('M.png'))
            msgBox.setWindowTitle('Minesweeper')
            msgBox.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Reset)  
            ret = msgBox.exec_()
            if (ret == QtGui.QMessageBox.Reset):
                self._new_field_create(self._field.sizen, self._field.sizem, self._field.mines)
                pass
            return True
        return False
    
    def _start_autobot(self):
        """In period start botstep"""
        if self._autobot_thread._run == True:
            self._autobot_thread.stop()
            try:
                self._autobot_thread.join()
            except Exception: pass
        else:
            self._autobot_thread = Repeater(self, self._queue)
            self._autobot_thread.start()
    
    def console_append(self, string):
        self._console.appendPlainText(string)
    
    def button_style(self, x, y, string):
        self._grid.itemAtPosition(x, y).widget().setStyleSheet(string)
        
    def _load_scoreboard(self):
        """Show the scoreboard"""
        sb = MSScoreboard()
        sb.show_score()
    
    def __test_bot__(self):
        """WIP"""
        self._game_start()
        self._bot_start()
        
def initGame():
    """Function to start the game"""
    app = QtGui.QApplication(sys.argv)
    scr = MSScreen()    
    scr.show()
    app.exec_()
    
    scr._queue_handler.stop()
    scr._autobot_thread.stop()
    scr._bot_thread.stop()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")