from PySide import QtGui, QtCore
import logging

class MSButton(QtGui.QPushButton):
    #Let's catch left and right mouse click
    rightClicked = QtCore.Signal()
    leftClicked = QtCore.Signal()
    
    def __init__(self):
        """Constructor"""
        #Init button with fixed size
        super(MSButton, self).__init__()
        rect = QtGui.QDesktopWidget().availableGeometry()
        height = round(min(rect.width() *3/4 / 30, rect.height() *3/4 / 16))
        self.setFixedSize(height, height)
        
    def mousePressEvent(self,event):
        """Handle presses"""
        if   event.button() == QtCore.Qt.LeftButton:
            logging.debug('Left button pressed')
            self.rightClicked.emit()
        elif event.button() == QtCore.Qt.RightButton:
            logging.debug('Right button pressed')
            self.leftClicked.emit()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")