import random

class MSBot():
    __screen__ = None
    __console__ = None

    def __init__(self, screen, console):
        self.__screen__  = screen
        self.__console__ = console
    
    def step1_simple(self):
        field = self.__screen__.__field__
        
        self.__console__.append('Start m&f bruteforcing')
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
        self.__console__.append('m&f Bruteforce failed')
        return False
    
    def step2_random(self):
        field = self.__screen__.__field__
        
        assist = [[0.0] * (field.sizeM) for y in range(field.sizeM)] #all field are closed('C')
        self.__console__.append('Start r&a bruteforcing')
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
