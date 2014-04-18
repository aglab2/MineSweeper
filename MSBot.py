import random

class MSBot():
    __screen__ = None
    __mnf__ = 0
    __rna__ = 0

    def __init__(self, screen):
        self.__screen__  = screen
        self.__mnf__ = 0
        self.__rna__ = 0
    
    def step1_mnf(self):
        field = self.__screen__.__field__
        console = self.__screen__.__console__
        val_mnf = self.__screen__.__val_mnf__
        
        console.append('Start m&f bruteforcing')
        for x in range(field.sizeN):
            for y in range(field.sizeM):
                if field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if frees == 0: continue
                if mines == field.field_closed[x][y]:
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: yellow")
                    console.append('    Success: props ({}, {})'.format(mines, frees))
                    self.__mnf__ += 1
                    val_mnf.setText('Number of m&f: {}'.format(self.__mnf__))
                    return True
                elif frees+mines == field.field_closed[x][y]:
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
                    self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: yellow")
                    console.append('    Success: props ({}, {})'.format(mines, frees))
                    self.__mnf__ += 1
                    val_mnf.setText('Number of m&f: {}'.format(self.__mnf__))
                    return True
        console.append('m&f Bruteforce failed')
        return False
    
    def step2_rna(self):
        field = self.__screen__.__field__
        console = self.__screen__.__console__
        val_rna = self.__screen__.__val_rna__

        assist = [[0] * (field.sizeM) for y in range(field.sizeM)] #assist
        
        console.append('Start r&a bruteforcing')
        for x in range(field.sizeN):
            for y in range(field.sizeM):
                if type(field.field_closed[x][y]) != int or field.field_closed[x][y] == 0: continue
                mines, frees = field.caim_prop(x, y)
                if frees == 0: continue
                probability = (field.field_closed[x][y] - mines) / frees * 840
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(field.sizeN) and y_next in range(field.sizeM):
                        if (field.field_closed[x_next][y_next] == 'C'): assist[x_next][y_next] += probability
            
        max_probability = -1
        max_cells = list()
        
        min_probability = 200000
        min_cells = list()
        
        for x in range(field.sizeN):
            for y in range(field.sizeM):
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
        
        
        if (max_probability == -1 and min_probability == 200000): return False
        
        max_probability = max_probability - 70
        min_probability = 70 - min_probability
        
        console.append('    ({}, {}):'.format(min_probability, max_probability))

        if abs(max_probability - min_probability) < 20:
            console.append('    Random!')
            console.append('    From {}+{} cells'.format(len(max_cells), len(min_cells)))
            
            self.__rna__ += 1
            val_rna.setText('Number of r&a: {}'.format(self.__rna__))

            if (random.random() > 0.5):
                (x, y) = random.choice(max_cells)
                self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
                self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: pink")
            else:
                (x, y) = random.choice(max_cells)
                self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
                self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: pink")
            return True
        
        if max_probability >= min_probability:
            console.append('    Mine found!:')
            console.append('    From {} cells'.format(len(max_cells)))
            self.__rna__ += 1
            val_rna.setText('Number of r&a: {}'.format(self.__rna__))
            (x, y) = random.choice(max_cells)
            self.__screen__.__grid__.itemAtPosition(x, y).widget().leftClicked.emit()
            self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: pink")
        else:
            console.append('    Free found!:')
            console.append('    From {} cells'.format(len(min_cells)))
            self.__rna__ += 1
            val_rna.setText('Number of r&a: {}'.format(self.__rna__))
            (x, y) = random.choice(min_cells)
            self.__screen__.__grid__.itemAtPosition(x, y).widget().rightClicked.emit()
            self.__screen__.__grid__.itemAtPosition(x, y).widget().setStyleSheet("background-color: pink")
        return True
    
    def step3_start(self):
        console = self.__screen__.__console__
        console.append('Start field')
        field = self.__screen__.__field__
        self.__screen__.__grid__.itemAtPosition(random.randint(0, field.sizeN-1), random.randint(0, field.sizeM-1)).widget().rightClicked.emit()

if __name__ == '__main__':
    raise Exception("Can't be executed from main")