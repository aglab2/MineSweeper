"""Class for leading scoreboard and showing it to user"""
from PySide import QtGui

class MSScoreboard():
    """Class itself"""

    def __init__(self):
        self._win = [0, 0, 0]
        self._fail = [0, 0, 0]
        self._wper = [0, 0, 0]
        self._cper = [0, 0, 0]
        self._count = [0, 0, 0]
        """Constructor with loader of scoreboard"""
        try:
            with open('scoreboard', 'r') as score_file:
                self._win[0] = int(score_file.readline())
                self._win[1] = int(score_file.readline())
                self._win[2] = int(score_file.readline())

                self._fail[0] = int(score_file.readline())
                self._fail[1] = int(score_file.readline())
                self._fail[2] = int(score_file.readline())

                self._wper[0] = float(score_file.readline())
                self._wper[1] = float(score_file.readline())
                self._wper[2] = float(score_file.readline())

                self._cper[0] = float(score_file.readline())
                self._cper[1] = float(score_file.readline())
                self._cper[2] = float(score_file.readline())

                self._count[0] = int(score_file.readline())
                self._count[1] = int(score_file.readline())
                self._count[2] = int(score_file.readline())
        except Exception: pass

    def __write_score__(self):
        """Write scoreboard to file"""
        try:
            with open('scoreboard', 'w') as score_file:
                score_file.write(str(self._win[0]) + '\n')
                score_file.write(str(self._win[1]) + '\n')
                score_file.write(str(self._win[2]) + '\n')

                score_file.write(str(self._fail[0]) + '\n')
                score_file.write(str(self._fail[1]) + '\n')
                score_file.write(str(self._fail[2]) + '\n')

                score_file.write(str(self._wper[0]) + '\n')
                score_file.write(str(self._wper[1]) + '\n')
                score_file.write(str(self._wper[2]) + '\n')

                score_file.write(str(self._cper[0]) + '\n')
                score_file.write(str(self._cper[1]) + '\n')
                score_file.write(str(self._cper[2]) + '\n')

                score_file.write(str(self._count[0]) + '\n')
                score_file.write(str(self._count[1]) + '\n')
                score_file.write(str(self._count[2]) + '\n')
        except Exception: pass


    def add_level(self, diff, state, per):
        """Recount new data"""
        if state == 0:
            self._fail[diff] += 1
        else:
            self._win[diff] += 1
        weight = self._cper[diff] * self._count[diff]
        self._cper[diff] = (weight+per) / (self._count[diff]+1)
        self._count[diff] += 1
        self._wper[diff] = self._win[diff] / self._count[diff] * 100
        self.__write_score__()

    def show_score(self):
        """Just show the scoreboard"""
        msg_box = QtGui.QMessageBox()
        msg_box.setText(
"""Scoreboard:
Beginners:
    Count:{}, Wins: {}, Fails:{}, Percentage:{}%, Average:{}%
Intermidiate:
    Count:{}, Wins: {}, Fails:{}, Percentage:{}%, Average:{}%
Professional:
    Count:{}, Wins: {}, Fails:{}, Percentage:{}%, Average:{}%""".format(
        self._count[0], self._win[0], self._fail[0],
        round(self._wper[0], 1), round(self._cper[0], 1),
        self._count[1], self._win[1], self._fail[1],
        round(self._wper[1], 1), round(self._cper[1], 1),
        self._count[2], self._win[2], self._fail[2],
        round(self._wper[2], 1), round(self._cper[2], 1)))
        msg_box.exec_()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")
