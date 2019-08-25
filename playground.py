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

pes_launcher = App(r'"D:\\Steam\\steamapps\\common\\PRO EVOLUTION SOCCER 2019\\PES2019.exe"')
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
    logger.info('Button %s pressed', button)
    return

def press_A():
    simulate_button(Key.ENTER)
    return

def press_B():
    simulate_button(Key.ESC)
    return

def press_X():
    simulate_button(Key.BACKSPACE)
    return

def press_Y():
    simulate_button(Key.CTRL)
    return

def press_menu():
    simulate_button(Key.DIVIDE)
    return

# TODO think of how to pass object argument as variable tip - https://stackoverflow.com/questions/706721/how-do-i-pass-a-method-as-a-parameter-in-python
# First simulate turn mechanism, than methods for each direction using it
def simulate_turn(direction,times):
    count = 0
    while times > count:
        count += 1
        simulate_button(direction)
        time.sleep(0.3)
    logger.info('Turned %s %s times', str(direction), count)
    del count

def turn_right(n):
    simulate_turn(Key.RIGHT, n)
    return

def turn_left(n):
    simulate_turn(Key.LEFT, n)
    return

def turn_up(n):
    simulate_turn(Key.UP, n)
    return

def turn_down(n):
    simulate_turn(Key.DOWN, n)
    return

def notepad_test():
    notepad.open()
    notepad.focus()
    print(notepad.getName(),notepad.getPID(),notepad.hasWindow())
    time.sleep(3)
    notepad.close()
#notepad_test()

def pes_plays():
    # pes_launcher.open()    # - Launches PES
    # time.sleep(45)    # - wait until is running
    pes = App('PRO EVOLUTION SOCCER 2019')  # Initialize PES APP instance
    print('first', pes.getName(), pes.getPID(), pes.hasWindow())
    time.sleep(10)
    pesreg = pes.window()
    print(pesreg.getH(),pesreg.getW())
    # while True:
    #     pes.focus()
    #     print(pes.getName(), pes.getPID(), pes.hasWindow(), pes.getWindow())
    #     time.sleep(10)
    #     print(pes.isRunning(),pes.hasWindow(), pes.isValid())
    #     pes.focus()
    #     pes.window().highlight(4)
    #     #pes.close()

#pes_plays()

#todo: initialize game:
# 1. Make sure settings are correct
# 2. Run the game, wait until it is loaded
# 3. Create app instance to interact with later for games purposes

notepad_launcher = App(r'"C:\\WINDOWS\\system32\\notepad.exe"')
noteName = 'Untitled - Notepad'
note2020 = None

def starting_note():
    global note2020
    App.focus(noteName)
    note2020 = App(noteName)
    if not note2020.isRunning():
        notepad_launcher.open()
        logger.info('Note2020 has been launched, waiting for initialization')
        while True:
            note2020 = App(noteName)
            if note2020.isRunning(5):
                logger.info('App is started')
                break
            else:
                print('No such app is running')

starting_note()
while True:
    print('first', note2020.getName(), note2020.getPID(), note2020.hasWindow())
    time.sleep(3)
    note_region = note2020.window()
    note_region.setX(0)
    print(note_region.getW(),note_region.getH(), note_region.getY(), note_region.getX())