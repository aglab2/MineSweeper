import random
import copy
import logging
from PySide import QtCore
from threading import Thread

class Connectors(QtCore.QObject):
    console_signal = QtCore.Signal(str)
    button_signal = QtCore.Signal(int, int, str)

class MSBot(Thread):
    def __init__(self, screen, parent = None):
        """Constructor"""
        Thread.__init__(self)
        self.__screen__  = screen
        self.__connectors__ = Connectors()
            
    def run(self):
        logging.info('Started!')
        if self.mnf(): 
            logging.info('Stopped!')
            return
        if self.tnc(): 
            logging.info('Stopped!')
            return
        if self.rna(): 
            logging.info('Stopped!')
            return
        if self.strt(): 
            logging.info('Stopped!')
            return
        logging.info('Stopped!')
        
    def mnf(self):
        """Mines and frees bruteforce
        Check if around cell is enough mines
        If mines = M open all cells around this one
        If mines+frees = M all cells around this are mines
        Is bulletproof bruteforce if opened cells are correct"""
        field = self.__screen__.__field__
        #val_mnf = self.__screen__.__val_mnf__
        
        #self.emit(QtCore.SIGNAL("console_append(str)"), 'Start m&f bruteforcing')
        self.__connectors__.console_signal.emit('Start m&f bruteforcing')

        for x in range(field.sizen):
            for y in range(field.sizem):
                if field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if frees == 0: continue
                if mines == field.field_closed[x][y]:
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
                    #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: yellow")
                    #console.append('    Success: props ({}, {})'.format(mines, frees))
                    self.__connectors__.console_signal.emit('    Success!')
                    self.__screen__.__mnf__ += 1
                    self.__screen__.__val_mnf__.setText('Number of m&f: {}'.format(self.__screen__.__mnf__))
                    return True
                elif frees+mines == field.field_closed[x][y]:
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
                    #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: yellow")
                    #console.append('    Success: props ({}, {})'.format(mines, frees))
                    self.__connectors__.console_signal.emit('    Success!')
                    #self.__mnf__ += 1
                    #val_mnf.setText('Number of m&f: {}'.format(self.__mnf__))
                    return True
        #self.console_signal.emit('m&f Bruteforce failed')
        #console.append('m&f Bruteforce failed')
        return False
    
    def tnc(self):
        ret = False
        """Tank and caim bruteforce
        Bulletproof but slow as hell"""
        field = self.__screen__.__field__
        #console = self.__screen__.__console__
        caim_nums = list()
        caim_frees = list()

        self.__connectors__.console_signal.emit('Start t&c bruteforce!')

        for x in range(field.sizen):
            for y in range(field.sizem):
                is_frees = False
                is_nums = False
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(field.sizen) and y_next in range(field.sizem):
                        if field.field_closed[x_next][y_next] == 'C':
                            is_frees = True
                        if type(field.field_closed[x_next][y_next]) == int and field.field_closed[x_next][y_next] > 0:
                            is_nums = True
                            
                if is_frees and is_nums and type(field.field_closed[x][y]) == int: 
                    caim_nums.append((x, y))
                    #self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: blue")
                if is_frees and is_nums and field.field_closed[x][y] == 'C': 
                    caim_frees.append((x, y))
        
        free_seg_list = list()
        
        while caim_frees:
            cur_frees = [caim_frees[0], ]
            caim_frees.remove(caim_frees[0])
            
            is_changed = True
            while is_changed:
                is_changed = False
                for num in caim_nums:
                    in_seg = False
                    for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                        x_next, y_next = num[0]+caim[0], num[1]+caim[1]
                        if x_next in range(field.sizen) and y_next in range(field.sizem):
                            if (x_next, y_next) in cur_frees:
                                in_seg = True
                    
                    if in_seg == True:
                        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                            x_next, y_next = num[0]+caim[0], num[1]+caim[1]
                            if x_next in range(field.sizen) and y_next in range(field.sizem):
                                if (x_next, y_next) in caim_frees:
                                    cur_frees.append((x_next, y_next))
                                    caim_frees.remove((x_next, y_next))
                                    is_changed = True
            
            free_seg_list.append(cur_frees)       
        
        found_cells = dict()
        
        for cur_list in free_seg_list:
            #print(len(cur_list))
            if (len(cur_list) > 20): continue 
            
            tank_field = copy.copy(field)
            cur_nums = list()
            for num in caim_nums:
                for caim in [(1,0), (0,1), (0,-1), (-1,0)]:
                    x_next, y_next = num[0]+caim[0], num[1]+caim[1]
                    if x_next in range(tank_field.sizen) and y_next in range(tank_field.sizem):
                        if (x_next, y_next) in cur_list: 
                            cur_nums.append(num)
                            break
            
            mine_solutions = list()
        
            def tankRecurse(k):
                is_solved = True
                for num in cur_nums:
                    mines, frees = tank_field.caim_prop(num[0], num[1])
                    if mines > tank_field.field_closed[num[0]][num[1]]:
                        return
                    if mines < tank_field.field_closed[num[0]][num[1]]:
                        is_solved = False
                    if frees+mines < tank_field.field_closed[num[0]][num[1]]:
                        return

                if k == len(cur_list):
                    if not is_solved: return
                    solution = list()
                    for i in cur_list:
                        solution.append((i, tank_field.field_closed[i[0]][i[1]]))
                    mine_solutions.append(solution)
                    return
                
                tank_field.field_closed[cur_list[k][0]][cur_list[k][1]] = 'F'
                tankRecurse(k+1)
                tank_field.field_closed[cur_list[k][0]][cur_list[k][1]] = 'C'
                tankRecurse(k+1)

            tankRecurse(0)
            
            if len(mine_solutions) == 0:
                self.__connectors__.console_signal.emit('Something goes wrong...')
                return False
                
            only_mine = copy.copy(cur_list)
            only_free = copy.copy(cur_list)
            
            for cell in mine_solutions[0]:
                found_cells[cell[0]] = 0

            for solution in mine_solutions:
                for cell in solution:
                    if cell[1] == 'C': 
                        if cell[0] in only_mine:
                            only_mine.remove(cell[0])
            
                    if cell[1] == 'F':
                        found_cells[cell[0]] += 1
                        if cell[0] in only_free:
                            only_free.remove(cell[0])

            w_coef = len(mine_solutions)
            for cell in mine_solutions[0]:
                found_cells[cell[0]] = found_cells[cell[0]] / w_coef

            for cell in only_mine:
                ret = True
                self.__screen__.__grid__.itemAtPosition(cell[0], cell[1]).widget().leftClicked.emit()
                #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: orange")
            for cell in only_free:
                ret = True
                self.__screen__.__grid__.itemAtPosition(cell[0], cell[1]).widget().rightClicked.emit()
                #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: purple")

        if ret:            
            self.__screen__.__tnc_bp__ += 1
            self.__screen__.__val_tnc_bp__.setText('Number of t&c bp: {}'.format(self.__screen__.__tnc_bp__))
            self.__connectors__.console_signal.emit('    Success!')
            return True
        else:
            if found_cells:
                #print(found_cells)
                min_cells = list()
                min_probability = 2
                max_cells = list()
                max_probability = -2
                
                for cell in list(found_cells.keys()):
                    if found_cells[cell] > max_probability: 
                        max_probability = found_cells[cell]
                        max_cells = list()
                    if found_cells[cell] == max_probability: max_cells.append(cell)
                
                    if found_cells[cell] < min_probability: 
                        min_probability = found_cells[cell]
                        min_cells = list()
                    if found_cells[cell] == min_probability: min_cells.append(cell)
                #print(min_cells)
                #print(max_cells)
                
                #if min_probability < 0.2 and 1-max_probability < 0.2: return False
                if min_probability == 1-max_probability:
                    if len(min_cells) > len(max_cells):
                        rand_cell = random.choice(min_cells)
                        self.__screen__.__grid__.itemAtPosition(rand_cell[0], rand_cell[1]).widget().rightClicked.emit()
                    else:
                        rand_cell = random.choice(max_cells)
                        self.__screen__.__grid__.itemAtPosition(rand_cell[0], rand_cell[1]).widget().leftClicked.emit()

                
                if min_probability <= 1-max_probability:
                    rand_cell = random.choice(min_cells)
                    self.__screen__.__grid__.itemAtPosition(rand_cell[0], rand_cell[1]).widget().rightClicked.emit()
                else:
                    rand_cell = random.choice(max_cells)
                    self.__screen__.__grid__.itemAtPosition(rand_cell[0], rand_cell[1]).widget().leftClicked.emit()
                
                self.__screen__.__tnc_rd__ += 1
                self.__screen__.__val_tnc_rd__.setText('Number of t&c rd: {}'.format(self.__screen__.__tnc_rd__))
                return True
        #else:
            #self.console_signal.emit('t&c Bruteforce failed')
         
        return False
         
    def rna(self):
        """Random and assist bruteforce
        Count probability of mine in every cell and set mine or flag depending on assist
        Isn't bulletproof bruteforce!
        """
        field = self.__screen__.__field__
        #console = self.__screen__.__console__
        #val_rna = self.__screen__.__val_rna__

        assist = [[0] * (field.sizem) for y in range(field.sizem)]
        
        counter = 0
        free_cells = list()
        
        self.__connectors__.console_signal.emit('Start r&a bruteforce!')
        #console.append('Start r&a bruteforcing')
        for x in range(field.sizen):
            for y in range(field.sizem):
                if field.field_closed[x][y] == 'C':
                    counter += 1
                    free_cells.append((x, y))
                    
                if type(field.field_closed[x][y]) != int or field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if frees == 0: continue
                probability = (field.field_closed[x][y] - mines) / frees * 840
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(field.sizen) and y_next in range(field.sizem):
                        if (field.field_closed[x_next][y_next] == 'C'): assist[x_next][y_next] += probability
        
        if counter <= 10:
            #console.append('    Override standart check!')
            cell = random.choice(free_cells)
            self.__screen__.__grid__.itemAtPosition(cell[0], cell[1]).widget().rightClicked.emit()
            return True
        
        max_probability = -1
        max_cells = list()
        
        min_probability = 200000
        min_cells = list()
        
        for x in range(field.sizen):
            for y in range(field.sizem):
                if field.field_closed[x][y] != 'C': continue
                if assist[x][y] == 0: continue
                
                assist[x][y] = round(assist[x][y] / 10)
                if assist[x][y] > max_probability: 
                    max_probability = assist[x][y]
                    max_cells = list()
                if assist[x][y] == max_probability: max_cells.append((x, y))
                
                if assist[x][y] < min_probability: 
                    min_probability = assist[x][y]
                    min_cells = list()
                if assist[x][y] == min_probability: min_cells.append((x, y))
        
        
        if (max_probability == -1 and min_probability == 200000): 
            return False
        
        max_probability = max_probability - 70
        min_probability = 70 - min_probability
        
        #console.append('    ({}, {}):'.format(min_probability, max_probability))

        if abs(max_probability - min_probability) < 20:
            #console.append('    Random!')
            #console.append('    From {}+{} cells'.format(len(max_cells), len(min_cells)))
            
            #self.__rna__ += 1
            #val_rna.setText('Number of r&a: {}'.format(self.__rna__))

            if (random.random() > 0.5):
                (x, y) = random.choice(max_cells)
                self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
                #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: pink")
            else:
                (x, y) = random.choice(max_cells)
                self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
                #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: pink")
            return True
        
        if max_probability >= min_probability:
            #console.append('    Mine found!:')
            #console.append('    From {} cells'.format(len(max_cells)))
            #self.__rna__ += 1
            #val_rna.setText('Number of r&a: {}'.format(self.__rna__))
            (x, y) = random.choice(max_cells)
            self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
            #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: pink")
        else:
            #console.append('    Free found!:')
            #console.append('    From {} cells'.format(len(min_cells)))
            #self.__rna__ += 1
            #val_rna.setText('Number of r&a: {}'.format(self.__rna__))
            (x, y) = random.choice(min_cells)
            self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
            #self.emit(QtCore.SIGNAL("button_style(int, int, str)"), x, y, "background-color: pink")
        self.__screen__.__rna__ += 1
        self.__screen__.__val_rna__.setText('Number of r&a: {}'.format(self.__screen__.__rna__))
        self.__connectors__.console_signal.emit('    Success!')

        return True
    
    def strt(self):
        """Just open random cell at the beginning or if bug appears"""
        #console = self.__screen__.__console__
        #console.append('Start field')
        self.__connectors__.console_signal.emit('Start field!')
        field = self.__screen__.__field__
        self.__screen__.__grid__.itemAtPosition(round(field.sizen/2), round(field.sizem/2)).widget().rightClicked.emit()
        return True

if __name__ == '__main__':
    raise Exception("Can't be executed from main")