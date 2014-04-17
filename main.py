from MSScreen import initGame
import logging

logging.basicConfig(filename = 'minesweeper.log', level=logging.DEBUG, format='(%(funcName)s) %(message)s')
logging.disable(level=logging.INFO)
initGame()