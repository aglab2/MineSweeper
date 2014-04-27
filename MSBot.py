import random
import copy
import time
import sys

from multiprocessing import Process #@UnresolvedImport

class MSBot(Process):
    def __init__(self, screen, queue=None, parent = None):
        """Constructor"""
        Process.__init__(self)
        self.__screen__  = screen
        self._queue = queue
            
    def run(self):
        if self.mnf(): return
        if self.tnc(): return
        if self.rna(): return
        if self.strt(): return
        
    def mnf(self):
        """Mines and frees bruteforce
        Check if around cell is enough mines
        If mines = M open all cells around this one
        If mines+frees = M all cells around this are mines
        Is bulletproof bruteforce if opened cells are correct"""
        field = self.__screen__.__field__
                    
        for x in range(field.sizen):
            for y in range(field.sizem):
                if field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if frees == 0: continue
                if mines == field.field_closed[x][y] or frees+mines == field.field_closed[x][y]:
                    self._queue.put(('pressR', (x, y)))
                    self._queue.put(('update', 0))
                    return True
        return False
    
    def tnc(self):
        ret = False
        """Tank and caim bruteforce
        Bulletproof but slow as hell"""
        field = self.__screen__.__field__
        caim_nums = list()
        caim_frees = list()
        self._queue.put(['console', 'Start t&c bruteforce!'])

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
                self._queue.put(['console', 'Something goes wrong...'])
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
                self._queue.put(('pressL', (cell[0], cell[1])))
            for cell in only_free:
                ret = True
                self._queue.put(('pressR', (cell[0], cell[1])))

        if ret:            
            self._queue.put(('update', 1))
            self._queue.put(['console', '    Success!'])
            time.sleep(1)
            return True
        else:
            if found_cells:
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

                if min_probability == 1-max_probability:
                    if len(min_cells) > len(max_cells):
                        rand_cell = random.choice(min_cells)
                        self._queue.put(('pressR', (rand_cell[0], rand_cell[1])))
                    else:
                        rand_cell = random.choice(max_cells)
                        self._queue.put(('pressL', (rand_cell[0], rand_cell[1])))

                elif min_probability <= 1-max_probability:
                    rand_cell = random.choice(min_cells)
                    self._queue.put(('pressR', (rand_cell[0], rand_cell[1])))
                else:
                    rand_cell = random.choice(max_cells)
                    self._queue.put(('pressL', (rand_cell[0], rand_cell[1])))

                self._queue.put(('update', 2))
                self._queue.put(['console', '    Success!'])
                time.sleep(1)
                return True
         
        return False
         
    def rna(self):
        """Random and assist bruteforce
        Count probability of mine in every cell and set mine or flag depending on assist
        Isn't bulletproof bruteforce!
        """
        field = self.__screen__.__field__

        assist = [[0] * (field.sizem) for y in range(field.sizem)]
        
        counter = 0
        free_cells = list()
        
        self._queue.put(['console', 'Start r&a bruteforce!'])
        
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
            cell = random.choice(free_cells)
            self._queue.put(('pressR', (cell[0], cell[1])))
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
        
        if abs(max_probability - min_probability) < 20:

            if (random.random() > 0.5):
                (x, y) = random.choice(max_cells)
                self._queue.put(('pressL', (x, y)))
            else:
                (x, y) = random.choice(min_cells)
                self._queue.put(('pressR', (x, y)))
            return True
        
        if max_probability >= min_probability:
            (x, y) = random.choice(max_cells)
            self._queue.put(('pressL', (x, y)))
        else:
            (x, y) = random.choice(min_cells)
            self._queue.put(('pressR', (x, y)))
        self._queue.put(('update', 3))
        self._queue.put(['console', '    Success!'])

        return True
    
    def strt(self):
        """Just open random cell at the beginning or if bug appears"""
        field = self.__screen__.__field__
        self._queue.put(('pressR', (round(field.sizen/2), round(field.sizem/2))))        
        return True

    def stop(self):
        sys.exit()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")