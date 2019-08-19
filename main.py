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
file_handler = logging.FileHandler('pes-f.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Stream hanlder
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# -------------------------------------------- SETTINGS FILE HANDLING

settings_path = os.path.expanduser('~/Documents/KONAMI/PRO EVOLUTION SOCCER 2019/')
settings_file = settings_path + 'settings.dat'
settings_backup = settings_path + 'settings.dat.pes-bkp'
settings_pesbot = 'settings.dat'


def isthere(a):
    if os.path.exists(a):
        return True
    else:
        return False


def makebkp():
    if isthere(settings_file) and isthere(settings_backup):
        logger.info("There is settings and settings backup files. We can start playing")
        return True
    if isthere(settings_file) and not isthere(settings_backup):
        logger.info("Creating backup and importing pes settings file")
        os.rename(settings_file, settings_backup)
        logger.info('Backup created: %s', os.listdir(settings_path))
        shutil.copy(settings_pesbot, settings_file)
        logger.info("Settings copied, folder contents: %s", os.listdir(settings_path))
    else:
        logger.warning("Something is wrong, please check settings folder")


def revertbackup():
    if isthere(settings_backup) and isthere(settings_file):
        logger.info("Backup is there, reverting:")
        os.remove(settings_file)
        logger.info("%s removed, starting revert from %s",
                    os.path.basename(settings_file),
                    os.path.basename(settings_backup))
        os.rename(settings_backup, settings_file)
        logger.info("Backup reverted to %s", os.path.basename(settings_file))
    else:
        logger.warn("No backup or something is wrong with file structure. Skipping")


# ------------------------------------------ DEFINE GAME VARIABLES

pes_launcher = App(r'"D:\\Steam\\steamapps\\common\\PRO EVOLUTION SOCCER 2019\\PES2019.exe"')
pesName = 'PRO EVOLUTION SOCCER 2019'
pes = App() # Global variable to be used for app reference after initialization
# ------------------------------------------- GAME
# Define navigation (works together with settings file for PES controller)

def simulate_button(button):
    pes.focus()
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

# Set check photo (a) and set timeout for check (b). It will focus on window.
def isok(a, b, c=0.89):
    pes.focus()
    if exists(Pattern(a).similar(c), b):
        time.sleep(0.7)
        logger.info('%s match found', a)
        return True
    else:
        logger.warning('%s not found', a)
        return False


# press_A when matched photo (a) within timeout (b)
def proceed(a, b):
    isok(a, b)
    press_A()
    return


def base_ok(a=5):
    if isok('img/club-house.JPG', a):
        logger.info('On home menu')
        return True
    else:
        logger.error('Not on home base, can\' proceed')
        return False


# Start game and go to "Club house" which is base point of the game
def start_game():
    logger.info('Starting interaction with %n', pes.getName())
    pes.focus()
    if isok('img/press-button.jpg', 180):
        press_A()
    if isok('img/online-confirm.jpg', 25):
        press_A()
    if isok('img/myclub-enter.JPG', 60):
        press_A()
    if isok('img/proceed-btn.JPG', 25):
        press_A()
    if isok('img/ack.JPG', 25):
        press_A()
    if isok('img/proceed-small.JPG', 120):
        press_A()

    # if auction then hope:
    if isok('img/auction-report.jpg', 25):
        press_A()
    if isok('img/big-ok.JPG', 20):
        press_A()

    if base_ok(20):
        logger.info("Game started successfully, logged in to game, can proceed with scripts")
    return


# Change team and get back to base
def team_change(squad):
    if base_ok(60):
        press_X()
    if isok('img/squad-list.JPG', 60):
        turn_down(squad)
        time.sleep(1)
        press_A()
    return


# Play one game and get back to base
def play_one():
    if base_ok(30):
        turn_left(3)
    # On sim game
    if isok('img/sim-game.JPG', 30):
        press_A()
    # Sim match start
    if isok('img/kickoff.JPG', 30):
        press_A()
    # Match started - switch to stat look
    if isok('img/match-started.JPG', 160):
        press_A()
    if isok('img/skip-graphic.JPG', 120):
        press_Y()
    # Halftime - click ok to start new match
    if isok('img/halftime.JPG', 650):
        press_A()
    if isok('img/second-half.JPG', 120):
        press_A()
    # Skip highlights
    if isok('img/highlights.JPG', 820):
        press_menu()

    # Experience
    if isok('img/next-finish.JPG', 30):
        press_A()

    # Experience points (press A twice to proceed)
    if isok('img/experience.JPG', 30):
        press_A()
        time.sleep(0.8)
        press_A()

    # Level up
    if isok('img/levelup.JPG', 20):
        press_A()

    # Changes rating
    if isok('img/rating.JPG', 20):
        press_A()

    #TODO Find a way to recognize and write down reward (income) and spendings (expenses on contracts)
    # Rewards
    if isok('img/reward.JPG', 20):
        press_A()

    if isok('img/reward2.JPG', 20):
        press_A()

    # Contract manager upd
    if isok('img/contract-manager-upd.JPG', 160):
        press_A()

    if isok('img/contract-confirm1.JPG', 10):
        turn_right(1)
        press_A()

    # If contract expires players only (for now)

    if isok('img/pay-gp.JPG', 10):
        press_A()

    if isok('img/sure-pay.JPG', 10):
        turn_right(1)
        press_A()

    if isok('img/contracts-renewed.JPG', 10):
        press_A()

    # Confirm got back to club house
    if base_ok(30):
        logger.info('1 more game')

    return

# TODO prepare scripts that simultaneously handle interrupters:
#  lost connection, screen freeze, auction update, confirmation only screens etc. Help:
#  https://answers.launchpad.net/sikuli/+question/199842
#  https://www.youtube.com/watch?v=hbGn1XxJzC4


# Play one game after another changing squads in between
#TODO find place for playing loop, find logick for number of games played etc.
def playing_loop():
    game_number = 0
    while True:
        play_one()
        game_number += 1
        logger.info('Number of games played: %s', str(game_number))
        team_change(1)
        play_one()
        game_number += 1
        logger.info('Number of games played: %s', str(game_number))
        team_change(2)

    # return


# Sign players using all available trainers one by one, skip 5stars (argument as nr of fivestars)
def sign_all(fivestars=1):
    # Initialize starting from home screen
    if isok('img/club-house.JPG', 10):
        logger.info('sign_all script started')
        turn_right(4)
        if isok('sign/scout.JPG', 3):
            press_A()
        if isok('sign/sign-enter.JPG', 4):
            press_A()
        # TODO create logick to return back to home screen once all sold (or only fivestar left)
        # While there is trainers sign them
        while True:
            if isok('sign/choose-slot.JPG', 9):
                press_A()
                # If no scouts - break
                if isok('sign/no-scouts.JPG', 3):
                    logger.warn('No scouts left, all signed')
                    press_A()
                    break
                # If there is scouts - use them
                #   If there is fivestars - skip them
                # TODO Think of logick for skipping fivestars if there is
                for i in range(fivestars):
                    if isok('sign/five-star.JPG', 1, 0.96):
                        logger.info('%s in list is Five star player', i)
                        turn_down(1)
                    else:
                        logger.info('No fivestar players %s', i)
                # Sign players
                if isok('sign/confirm.JPG', 9):
                    press_A()
                if isok('sign/chosed-trainer.JPG', 9):
                    turn_down(3)
                    press_A()
                if isok('sign/sure.JPG', 9):
                    turn_right(1)
                    press_A()
                if isok('sign/skip.JPG', 10):
                    press_menu()
                if isok('sign/confirm-player.JPG', 9):
                    time.sleep(1.5)
                    press_A()
                if isok('sign/next.JPG', 9):
                    press_A()
                if isok('sign/added.JPG', 9):
                    press_A()
        # Get back to home once all sold
        if isok('sign/choose-slot.JPG', 5):
            press_B()
        if isok('sign/sign-enter.JPG', 5):
            press_B()
        if isok('sign/scout.JPG', 5):
            turn_left(4)
        if isok('img/club-house.JPG', 10):
            logger.info('sign_all script finished')
        return

# Remove all players others than squad

def players_convert(team):
    # internal var
    # team_is = 0
    # if base_ok():
    #      logger.info('Starting players to EXP trainers convertion')
    #      logger.info('Switch to team %s', str(team))
    #      # Change to desired team
    #      team_change(team)
    # if base_ok():
    #      press_A()
    # Define if on reserves
    def on_reserves():
        # Define white or bronze team 0=no, 1=white, 2=bronze
        if isok('conv/reserves.JPG', 8):
            logger.info('On reserves')
            return True
        else:
            return False

    # def which_color():
    #     if on_reserves():
    #         turn_up(1)
    #         turn_right(1)
    #     if isok('conv/white-ball.JPG', 5):
    #         team_is = 1
    #         logger.info('Team of whites %s', str(team_is))
    #     if isok('conv/bronze-ball.JPG', 5):
    #         team_is = 2
    #         logger.info('Team of bronze %s',str(team_is))
    # # Open reserves
    def open_reserves():
        while not on_reserves():
            turn_down(1)
            turn_left(1)
        press_A()

    # Ensure on reserves
    def find_victim():
        if isok('conv/reserves-list.JPG', 5):
            # create variable
            # if team_is == 1:
            #     ball_path='conv/white-ball.JPG'
            # if team_is == 2:
            #     ball_path='conv/bronze-ball.JPG'
            # Jump down
            pes.focus()
            # Scroll to the end
            keyDown(Key.DOWN)
            time.sleep(5)
            keyUp(Key.DOWN)
            while not isok('conv/black-ball.JPG', 2):
                for i in range(6):
                    if isok('conv/bronze-ball.JPG', 5):
                        logger.info('Found %s', 'white ball')
                        return
                    else:
                        turn_right(1)
                turn_up(1)

    def exec_victim():
        logger.info('Looking for victim')
        press_X()
        if isok('conv/player-menu.JPG', 5):
            turn_down(2)
        if isok('conv/convert.JPG', 5):
            press_A()
        if isok('conv/no.JPG', 5):
            turn_right(1)
            press_A()
        if isok('conv/converted.JPG', 5):
            press_A()

    # on_reserves()
    #    which_color()
    #     exec_victim()
    #TODO think on logick of how to execute, how many, when etc
    while True:
        open_reserves()
        find_victim()
        exec_victim()

# TESTS
#TODO: put it all together

# INITIALIZE GAME (make sure settings are ready, game has started and app instance created.
def initialize_pes():
    global pes
    pes = App(pesName)
    print(pes.getName())
    if not pes.isRunning():
        makebkp()
        pes_launcher.open()
        logger.info('%s has been launched, waiting for initialization', pesName)
        # TODO: create logic for error if app not starting
        while True:
            pes = App(pesName)
            if pes.isRunning(5) and pes.getName()!='Steam.exe':
                logger.info('Global app is initialized and %s under PID %s can be used for reference', pes.getName(), pes.getPID())
                break
    else:
        logger.info('%s already running and initialized, we can proceed with scripts', pes.getName())