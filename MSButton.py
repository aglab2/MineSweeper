from PySide import QtGui, QtCore
import logging

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

if __name__ == '__main__':
    raise Exception("Can't be executed from main")