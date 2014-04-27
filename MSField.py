"""Field class for Minesweeper"""

import random
import logging

class MSField():
    """Class itself"""

    def __init__(self, sizen, sizem, mines, screen):
        """Constructor of random field"""
        if mines > sizen*sizem:
            raise Exception('To many mines for this field size')
        #Initiate field and properties of fields
        mine_field = ['M']*mines + [0]*(sizen*sizem-mines) #mines+free spaces
        random.shuffle(mine_field)
        self.sizen = sizen
        self.sizem = sizem
        self.__mines__ = mines
        self.finit = -1
        self.__field_opened__ = [mine_field[self.sizem*i:self.sizem*(i+1)]
                                 for i in range(self.sizen)]
        self.field_closed = [['C']*(self.sizem)
                             for i in range(self.sizen)]
        self.__screen__ = screen

        #Count number of mines
        for i in range(self.sizen):
            for j in range(self.sizem):
                if self.__field_opened__[i][j] == 'M':
                    continue
                for caim in [(1, 1), (1, 0), (1, -1), (0, 1),
                             (-1, -1), (-1, 0), (-1, 1), (0, -1)]:
                    x_next, y_next = i+caim[0], j+caim[1]
                    if x_next in range(self.sizen) \
                    and y_next in range(self.sizem):
                        if self.__field_opened__[x_next][y_next] == 'M':
                            self.__field_opened__[i][j] += 1

    def print_opened(self):
        """Debug print opened"""
        for i in range(self.sizen):
            info_str = ''
            for j in range(self.sizem):
                info_str += str(self.__field_opened__[i][j])
            logging.info(info_str)
        logging.info('')

    def print_closed(self):
        """Debug print closed"""
        for i in range(self.sizen):
            info_str = ''
            for j in range(self.sizem):
                info_str += str(self.field_closed[i][j])
            logging.info(info_str)
        logging.info('')

    def is_solved(self):
        """Check if field contain any closed numbers"""
        for i in range(self.sizen):
            for j in range(self.sizem):
                if self.field_closed[i][j] != self.__field_opened__[i][j] and \
                self.__field_opened__[i][j] != 'M': return False
        return True

    def defuse_cell(self, i, j):
        """Handles open cell activity"""
        logging.debug('Started with ({}, {})'.format(i, j))
        logging.debug('    closed: {}'.format(self.field_closed[i][j]))
        logging.debug('    opened: {}'.format(self.__field_opened__[i][j]))

        #Check whether current field is full
        if self.field_closed[i][j] != 'C' and self.field_closed[i][j] != 'F':
            mines, frees = self.caim_prop(i, j)
            if mines == self.field_closed[i][j]:
                self.mine_cell(i, j)
            elif frees + mines == self.field_closed[i][j]:
                self.free_cell(i, j)
        else:
            self.__open_cell__(i, j)

    def mine_cell(self, i, j):
        """Caim method to set flags"""
        for caim in [(1, 1), (1, 0), (1, -1), (0, 1),
                     (-1, -1), (-1, 0), (-1, 1), (0, -1)]:
            x_next, y_next = i+caim[0], j+caim[1]
            if x_next in range(self.sizen) and y_next in range(self.sizem):
                if self.field_closed[x_next][y_next] != 'F':
                    self.__open_cell__(x_next, y_next)

    def free_cell(self, i, j):
        """Caim method to open cells"""
        for caim in [(1, 1), (1, 0), (1, -1), (0, 1),
                     (-1, -1), (-1, 0), (-1, 1), (0, -1)]:
            x_next, y_next = i+caim[0], j+caim[1]
            if x_next in range(self.sizen) and y_next in range(self.sizem):
                if self.field_closed[x_next][y_next] == 'C':
                    self.field_closed[x_next][y_next] = 'F'
                    self.__screen__.setNames(x_next, y_next, 'F')

    def __open_cell__(self, i, j):
        """Open cell and if caim val=0 call dfs on field"""
        if self.__field_opened__[i][j] == 'M':
            self.finit = 2
        if self.__field_opened__[i][j] == 0:
            self.__cell_dfs__(i, j, set())
        else:
            self.field_closed[i][j] = self.__field_opened__[i][j]
            self.__screen__.setNames(i, j, self.__field_opened__[i][j])

    def __cell_dfs__(self, i, j, used):
        """Caim dfs on cells with caim val = 0"""
        logging.info('Started with ({}, {})'.format(i, j))
        #Add cell to used if it is not already there
        if (i, j) in used:
            return
        used.add((i, j))
        #Open cell and call dfs from surrounding fields
        self.field_closed[i][j] = self.__field_opened__[i][j]
        self.__screen__.setNames(i, j, self.__field_opened__[i][j])

        if self.field_closed[i][j] != 0:
            return
        for caim in [(1, 1), (1, 0), (1, -1), (0, 1),
                     (-1, -1), (-1, 0), (-1, 1), (0, -1)]:
            x_next, y_next = i+caim[0], j+caim[1]
            if x_next in range(self.sizen) and y_next in range(self.sizem):
                self.__cell_dfs__(x_next, y_next, used)

    def mark_cell(self, i, j):
        """Set flag"""
        logging.debug('Started with ({}, {})'.format(i, j))

        #Set flag or unset flag
        if self.field_closed[i][j] == 'C':
            self.field_closed[i][j] = 'F'
            self.__screen__.setNames(i, j, 'F')
        elif self.field_closed[i][j] == 'F':
            self.field_closed[i][j] = 'C'
            self.__screen__.setNames(i, j, 'C')

    def caim_prop(self, i, j):
        """Get properties (mines&frees) of cell caim"""
        mines = 0
        frees = 0
        for caim in [(1, 1), (1, 0), (1, -1), (0, 1),
                     (-1, -1), (-1, 0), (-1, 1), (0, -1)]:
            x_next, y_next = i+caim[0], j+caim[1]
            if x_next in range(self.sizen) and y_next in range(self.sizem):
                if self.field_closed[x_next][y_next] == 'F':
                    mines += 1
                if self.field_closed[x_next][y_next] == 'C':
                    frees += 1
        return (mines, frees)

    def kill_field(self):
        """Just open all the mines on the field
        and check correctness of flags"""
        counter = 0
        for i in range(self.sizen):
            for j in range(self.sizem):
                if self.field_closed[i][j] == self.__field_opened__[i][j] or \
                (self.field_closed[i][j] == 'F' and \
                 self.__field_opened__[i][j] == 'M'):
                    counter += 1
                if self.field_closed[i][j] == 'C' and \
                self.__field_opened__[i][j] == 'M':
                    self.field_closed[i][j] = 'M'
                    self.__screen__.setNames(i, j, 'M')
                if self.field_closed[i][j] == 'F' and \
                self.__field_opened__[i][j] != 'M':
                    self.field_closed[i][j] = 'P'
                    self.__screen__.setNames(i, j, 'P')
        return counter

if __name__ == '__main__':
    raise Exception("Can't be executed from main")
