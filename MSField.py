import random
import logging

class MSField():
    __field_opened__ = list()
    field_closed = list()
    sizeN = 0
    sizeM = 0
    __mines__ = 0
    finit = 0
    
    def __init__(self, sizeN, sizeM, mines):
        if mines > sizeN*sizeM:
            raise Exception('To many mines for this field size')
        #Initiate field and properties of fields
        mine_field = ['M']*mines + [0]*(sizeN*sizeM-mines) #mines+free spaces
        random.shuffle(mine_field)
        self.sizeN = sizeN
        self.sizeM = sizeM
        self.__mines__ = mines
        self.finit = -1
        self.__field_opened__ = [mine_field[self.sizeM*i:self.sizeM*(i+1)] for i in range(self.sizeN)] 
        self.field_closed = [['C']*(self.sizeM) for i in range(self.sizeN)] #all field are closed('C')
        
        #Count number of mines
        for x in range(self.sizeN):
            for y in range(self.sizeM):
                if self.__field_opened__[x][y] == 'M': continue
                for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
                    x_next, y_next = x+caim[0], y+caim[1]
                    if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                        if (self.__field_opened__[x_next][y_next] == 'M'): self.__field_opened__[x][y] += 1
    
    #Debug print methods
    def print_opened(self):
        for i in range(self.sizeN):
            info_str = ''
            for j in range(self.sizeM):
                info_str += str(self.__field_opened__[i][j])
            logging.info(info_str)
        logging.info('')

    def print_closed(self):
        for i in range(self.sizeN):
            info_str = ''
            for j in range(self.sizeM):
                info_str += str(self.field_closed[i][j])
            logging.info(info_str)
        logging.info('')
            
    def is_solved(self):
        #Check if field contain any closed numbers
        
        for i in range(self.sizeN):
            for j in range(self.sizeM):
                if self.field_closed[i][j] != self.__field_opened__[i][j] and self.__field_opened__[i][j] !='M':
                    return False
        return True 
    
    def defuse_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        logging.debug('    closed: {}'.format(self.field_closed[x][y]))
        logging.debug('    opened: {}'.format(self.__field_opened__[x][y]))
        
        #Check whether current field is full
        if self.field_closed[x][y] != 'C' and self.field_closed[x][y] != 'F':
            mines, frees = self.caim_prop(x, y)
            if mines == self.field_closed[x][y]:
                self.mine_cell(x, y)  
            elif frees + mines == self.field_closed[x][y]:
                self.free_cell(x, y)
        else:
            self.__open_cell__(x, y)
    
    def mine_cell(self, x, y):
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                if self.field_closed[x_next][y_next] != 'F': self.__open_cell__(x_next, y_next)

    def free_cell(self, x, y):
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                if self.field_closed[x_next][y_next] == 'C': self.field_closed[x_next][y_next] = 'F'
    
    def __open_cell__(self, x, y):
        #Open number and if num=0 call dfs on field
        if self.__field_opened__[x][y] == 'M': self.finit = 2
        if self.__field_opened__[x][y] == 0:
            self.__cell_dfs__(x, y, set())
        else:
            self.field_closed[x][y] = self.__field_opened__[x][y]
    
    def __cell_dfs__(self, x, y, used):
        logging.info('Started with ({}, {})'.format(x, y))
        #Add cell to used if it is not already there
        if (x, y) in used: return 
        used.add((x, y))
        #Open cell and call dfs from surrounding fields
        self.field_closed[x][y] = self.__field_opened__[x][y]

        if self.field_closed[x][y] != 0: return 
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                self.__cell_dfs__(x_next, y_next, used)
        
    def mark_cell(self, x, y):
        logging.debug('Started with ({}, {})'.format(x, y))
        
        #Set flag or unset flag
        if self.field_closed[x][y] == 'C': self.field_closed[x][y] = 'F'
        elif self.field_closed[x][y] == 'F': self.field_closed[x][y] = 'C'
    
    def caim_prop(self, x, y):
        mines = 0
        frees = 0
        for caim in [(1,1), (1,0), (1,-1), (0,1), (0,-1), (-1,1), (-1,0), (-1,-1)]:
            x_next, y_next = x+caim[0], y+caim[1]
            if x_next in range(self.sizeN) and y_next in range(self.sizeM):
                if self.field_closed[x_next][y_next] == 'F': mines += 1
                if self.field_closed[x_next][y_next] == 'C': frees += 1
        return (mines, frees) 

    def kill_field(self):
        counter = 0
        for x in range(self.sizeN):
            for y in range(self.sizeM):
                if self.field_closed[x][y] == self.__field_opened__[x][y] or (self.field_closed[x][y] == 'F' and self.__field_opened__[x][y] == 'M'): counter += 1
                if self.field_closed[x][y] == 'C':
                    self.field_closed[x][y] = self.__field_opened__[x][y]
                elif self.field_closed[x][y] == 'F' and self.__field_opened__[x][y] != 'M':
                    self.field_closed[x][y] = 'P'
        return counter

if __name__ == '__main__':
    raise Exception("Can't be executed from main")