from PySide import QtGui

class MSScoreboard():
    __win__ = [0, 0, 0]
    __fail__ = [0, 0, 0]
    __wper__ = [0, 0, 0]
    __cper__ = [0, 0, 0]
    __count__ = [0, 0, 0]
    
    def __init__(self):
        """Constructor with loader of scoreboard"""
        try:
            with open('scoreboard', 'r') as f:
                self.__win__[0] = int(f.readline())
                self.__win__[1] = int(f.readline())
                self.__win__[2] = int(f.readline())
                
                self.__fail__[0] = int(f.readline())
                self.__fail__[1] = int(f.readline())
                self.__fail__[2] = int(f.readline())
                
                self.__wper__[0] = float(f.readline())
                self.__wper__[1] = float(f.readline())
                self.__wper__[2] = float(f.readline())
                
                self.__cper__[0] = float(f.readline())
                self.__cper__[1] = float(f.readline())
                self.__cper__[2] = float(f.readline())
                
                self.__count__[0] = int(f.readline())
                self.__count__[1] = int(f.readline())
                self.__count__[2] = int(f.readline())

        except Exception: pass      

    def __write_score__(self):
        """Write scoreboard to file"""
        try:
            with open('scoreboard', 'w') as f:
                f.write(str(self.__win__[0]) + '\n')
                f.write(str(self.__win__[1]) + '\n')
                f.write(str(self.__win__[2]) + '\n')

                f.write(str(self.__fail__[0]) + '\n')
                f.write(str(self.__fail__[1]) + '\n')
                f.write(str(self.__fail__[2]) + '\n')
                
                f.write(str(self.__wper__[0]) + '\n')
                f.write(str(self.__wper__[1]) + '\n')
                f.write(str(self.__wper__[2]) + '\n')
                
                f.write(str(self.__cper__[0]) + '\n')
                f.write(str(self.__cper__[1]) + '\n')
                f.write(str(self.__cper__[2]) + '\n')
                
                f.write(str(self.__count__[0]) + '\n')
                f.write(str(self.__count__[1]) + '\n')
                f.write(str(self.__count__[2]) + '\n')
        except Exception: pass        

        
    def add_level(self, diff, state, per):
        """Recount new data"""
        if state == 0:
            self.__fail__[diff] += 1
        else:
            self.__win__[diff] += 1
        self.__cper__[diff] = self.__cper__[diff] * self.__count__[diff] / (self.__count__[diff]+1) + per / (self.__count__[diff]+1)
        self.__count__[diff] += 1
        self.__wper__[diff] = self.__win__[diff] / self.__count__[diff] * 100
        self.__write_score__()

    def show_score(self):
        """Just show the scoreboard"""
        msgBox = QtGui.QMessageBox()
        msgBox.setText(
"""Scoreboard:
Beginners:
    Count:{}, Wins: {}, Fails:{}, Percentage:{}%, Average:{}%
Intermidiate:
    Count:{}, Wins: {}, Fails:{}, Percentage:{}%, Average:{}%
Professional:
    Count:{}, Wins: {}, Fails:{}, Percentage:{}%, Average:{}%""".format(
        self.__count__[0], self.__win__[0], self.__fail__[0], round(self.__wper__[0],1), round(self.__cper__[0],1), 
        self.__count__[1], self.__win__[1], self.__fail__[1], round(self.__wper__[1],1), round(self.__cper__[1],1), 
        self.__count__[2], self.__win__[2], self.__fail__[2], round(self.__wper__[2],1), round(self.__cper__[2],1), 
        ))
        msgBox.exec_()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")    