from PySide import QtGui, QtCore

class MSButton(QtGui.QPushButton):
    #Let's catch left and right mouse click
    right_clicked = QtCore.Signal()
    left_clicked = QtCore.Signal()
    
    def __init__(self):
        """Constructor"""
        #Init button with fixed size
        super(MSButton, self).__init__()
        rect = QtGui.QDesktopWidget().availableGeometry()
        height = round(min(rect.width() *3/4 / 30, rect.height() *3/4 / 16))
        self.setFixedSize(height, height)
        
    def mousePressEvent(self, event):
        """Handle presses"""
        if   event.button() == QtCore.Qt.LeftButton:
            #logging.info('Left button pressed')
            self.right_clicked.emit()
            self.pressed.emit()
        elif event.button() == QtCore.Qt.RightButton:
            #logging.info('Right button pressed')
            self.left_clicked.emit()
            self.pressed.emit()
    
    def mouseReleaseEvent(self, event):
        if   event.button() == QtCore.Qt.LeftButton:
            #logging.info('Left button pressed')
            self.released.emit()
        elif event.button() == QtCore.Qt.RightButton:
            #logging.info('Right button pressed')
            self.released.emit()
    

if __name__ == '__main__':
    raise Exception("Can't be executed from main")
