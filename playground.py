import logging
import os
import shutil
from keyboard import mouse

from lackey import *

# ---------------------------------------------- LOGGING HANDLING

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set format for logs
formatter = logging.Formatter('[%(levelname)s:%(asctime)s:%(funcName)20s() ]: %(message)s')

# File handler - file name, format, level
file_handler = logging.FileHandler('test2.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Stream hanlder
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

#pes = App(r'"C:\\WINDOWS\\system32\\notepad.exe"')
pesName = 'Untitled - Notepad'
#pes_real_name = pes.getName()
#pesID = pes.getPID()

logger.info('Pes name: %s, ', pesName)

def simulate_button(button):
    App.focus(pesName)
    time.sleep(0.8)
    keyDown(button)
    time.sleep(0.1)
    keyUp(button)
    logger.info('Button %s pressed',button)
    return

def new_press_button():
    simulate_button(Key.ENTER)
    return

def simulate_turn(direction,times):
    count = 0
    while times > count:
        count += 1
        simulate_button(direction)
        time.sleep(0.3)
    logger.info('Turned %s %s times', str(direction), count)
    del count

def new_turn_right_mechanis(n):
    simulate_turn(Key.RIGHT, n)
    return
    # return simulate_turn(turn_direction, n)



# new_press_button()
# new_turn_right_mechanis(5)