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

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# -------------------------------------------- SETTINGS FILE HANDLING

settings_path = os.path.expanduser('~/Documents/KONAMI/eFootball PES 2020/')
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
        logger.warning("No backup or something is wrong with file structure. Skipping")


# ------------------------------------------ DEFINE GAME VARIABLES

pes_launcher = App(r'"D:\\Steam\\steamapps\\common\\eFootball PES 2020\\PES2020.exe"')
pesName = 'eFootball PES 2020'
pes = App() # Global variable to be used for app reference after initialization
pes_region = None
team_nr = 0
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
def isok(img, seconds, similarity=0.89):
    pes.focus()
    # Update PES window
    global pes_region
    pes_region = pes.window()
    #pes_region.highlight(1)
    #logger.debug('PES height: %s, width: %s, position(x,y): %s, %s', pes_region.getH(), pes_region.getW(), pes_region.getX(), pes_region.getY())

    if pes_region.exists(Pattern(img).similar(similarity), seconds):
        time.sleep(0.7)
        logger.info('%s match found', img)
        # DEBUG:
        pes_region.exists(Pattern(img).similar(similarity), seconds).highlight(2)
        return True
    else:
        logger.warning('%s not found', img)
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
    logger.info('Starting interaction with %s', pes.getName())
    pes.focus()
    if isok('img/press-button.jpg', 180):
        press_A()
    if isok('img/online-confirm.jpg', 25) or isok('img/no-new-updates.JPG', 20):
        press_A()
    if isok('img/this-week-pick-up.JPG', 30):
        press_B()
    if isok('img/game-screen.JPG', 30, 0.7):
        turn_down(1)
    if isok('img/myclub-enter.JPG', 60, 0.7):
        press_A()
        if isok('img/sure-start.JPG', 15):
            press_A()
    if isok('img/live-update.JPG', 7):
        press_A()
    if isok('img/featured-players.JPG', 8):
        press_A()
    # if isok('img/proceed-btn.JPG', 25):
    #     press_A()
    # if isok('img/no-new-updates.JPG', 25):
    #     press_A()
    # if isok('img/proceed-small.JPG', 120):
    #     press_A()

    # TODO if auction then hope:
    if isok('img/auction-report.jpg', 10):
        press_A()
        if isok('img/big-ok.JPG', 15):
            press_A()
    # Loaded successfully
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
    global team_nr
    team_nr = squad
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
        #TODO find another way:
        #pes_region.saveScreenCapture('./shot', 'test1')
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
        if isok('img/experience.JPG', 2):
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

    # If contract expires players only (for now)
    if isok('img/contract-confirm1.JPG', 10):
        turn_right(1)
        press_A()

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

# Sign players using all available trainers one by one, skip 5stars (argument as nr of fivestars)
def sign_all(fivestars=0):
    # Initialize starting from home screen
    if base_ok(10):
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
                    logger.warning('No scouts left, all signed')
                    press_A()
                    break
                # If there is scouts - use them
                #   If there is fivestars - skip them
                # TODO Think of logick for skipping fivestars if there is
                if fivestars > 0:
                    for i in range(fivestars):
                        if isok('sign/five-star.JPG', 1, 0.96):
                            logger.info('%s in list is Five star player', i)
                            turn_down(1)
                        else:
                            logger.info('No fivestar players %s', i)
                    if isok('sign/five-star.JPG', 1, 0.96):
                        logger.info('More 4-5 stars than provided or all other used. Escaping.')
                        press_B()
                        break
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

def sell_scouts():
    scout_number = 0
    if base_ok(3):
        logger.info('Sell scouts script started')
        turn_right(4)
    if isok('sign/scout.JPG',3):
        press_A()
    if isok('sign/sign-enter.JPG', 4):
        turn_down(2)
        turn_right(1)
    if isok('sign/sell-enter.JPG',3):
        press_A()
    if isok('sign/no-scouts-left.JPG',3):
        press_A()
        time.sleep(0.5)
        press_B()
    else:
        while isok('sign/unchecked.JPG',2,0.99):
            press_A()
            turn_down(1)
            scout_number += 1
        if isok('sign/last-checked.JPG',0.7):
             press_X()
        if isok('sign/confirm-sell.JPG',0.7):
            turn_right(1)
            press_A()
        if isok('sign/reward-received.JPG',0.7):
            press_A()
            logger.info('%s scouts sold, reward is received',scout_number)
        if isok('sign/no-scouts-left.JPG',0.5):
            press_A()
            time.sleep(0.5)
            press_B()
    if isok('sign/scout.JPG',5):
        turn_left(4)
    if base_ok():
        logger.info('Sell scouts script has finished')



# Remove all players others than squad

def players_convert():
    team_color = ''
    # if base_ok():
    #      logger.info('Starting players to EXP trainers convertion')
    #      # logger.info('Switch to team %s', str(team_nr))
    #      # # Change to desired team DEBUG
    #      #team_change(1)
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

    def which_color():
        if on_reserves():
            turn_up(1)
            turn_right(1)
        if isok('conv/white-ball.JPG', 5):
            team_is = 1
            logger.info('Team of whites %s', str(team_is))
        if isok('conv/bronze-ball.JPG', 5):
            team_is = 2
            logger.info('Team of bronze %s',str(team_is))
    # Open reserves
    def open_reserves():
        while not on_reserves():
            turn_down(1)
            turn_left(1)
        press_A()

    # Ensure on reserves
    def find_victim():
        if isok('conv/reserves-list.JPG', 5):
            # create variable
            ball_path = 'None'
            if team_nr == 1:
                del ball_path
                ball_path='conv/white-ball.JPG'
            if team_nr == 2:
                del ball_path
                ball_path='conv/bronze-ball.JPG'
            # Jump down
            pes.focus()
            # Scroll to the end
            keyDown(Key.DOWN)
            time.sleep(5)
            keyUp(Key.DOWN)
            while not isok('conv/black-ball.JPG', 2):
                # and not isok('conv/gold-ball.JPG',2) and not isok('conv/silver-ball.JPG', 2)
                for i in range(6):
                    if isok('conv/black-ball.JPG',0.5):
                        logger.info('Found black ball, exiting')
                        break
                    if isok(ball_path, 0.5):
                        logger.info('Found %s', ball_path)
                        return True
                    else:
                        turn_right(1)
                turn_up(1)
            press_B()
            time.sleep(1)
            press_B()
            time.sleep(1)
            logger.warning('Other than white or bronze ball found, escaping script')
            return False

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

    #TODO think on logick of how to execute, how many, when etc
    for i in range(1,3):
        if base_ok():
            logger.info('Starting players to EXP trainers convertion')
            team_change(i)
        if base_ok():
            press_A()
        while True:
            open_reserves()
            if find_victim():
                exec_victim()
            else:
                break

# TESTS
#TODO: put it all together

# INITIALIZE GAME (make sure settings are ready, game has started and app instance created).
def initialize_pes():
    global pes
    App.focus(pesName)
    pes = App(pesName)
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
    global pes_region
    pes_region= pes.window()
    return pes_region

# initialize_pes()
# pes.focus()
# print(pes.getPID(), pes.getName(), pes.hasWindow(), pes_region.getH(),pes_region.getW())
# playing_loop(10)
#pes_region.saveScreenCapture('./shot','screen2')

#TODO: implement pes_region.[....] to ifisok() to limit search area, same for other stuff
# while True:
#     if pes_region.exists(Pattern('sign/sign-enter.JPG').similar(0.9), 3):
#             time.sleep(1)
#             print('Pattern found')
#     else:
#         print('Not found')

########################################################### CONSTRUCTION AREA
initialize_pes()
pes.focus()
pes_region.saveScreenCapture('./shot','test4')
# pes_x = pes_region.getX()
# pes_y = pes_region.getY()
# pes_w = pes_region.getW()
# pes_h = pes_region.getH()
# print(pes_x, pes_y, pes_w, pes_h)
# print(pes.getPID(), pes.getName(), pes.hasWindow(), pes_region.getX(), pes_region.getY(), pes_region.getH(),pes_region.getW())
# dupa = pes_region.exists(Pattern('shot/money.JPG').similar(0.8), 5)
# print('DUpa: ', dupa.getH(), dupa.getW())
# dupa.highlight(1)
#
# player_position = [1, 2, 3, 4]
# player_rating = [1, 2, 3, 4]
# contract_duration = [1, 2, 3, 4]
#
# def pictaker(coordinates):
#     # create pic based on received coordinates
#     print('Something')
#
# def coordset():
#     # get standard positions and align it to pes window
#     print('Something')
#
# def screen_reader(coordinates, expected_value):
#     # gets coordinates and expected value there - returns boolean if value match one in area or not
#     print('Value')



###########################################################

# Play one game after another changing squads in between
#TODO find place for playing loop, find logick for number of games played etc.
def playing_loop(number=1000):
    initialize_pes()
    if base_ok():
        logger.info('Game is on, no need to start')
    else:
        start_game()
    game_number = 0
    for i in range(number):
        play_one()
        game_number += 1
        logger.info('Number of games played: %s', str(game_number))
        team_change(2)
        play_one()
        game_number += 1
        logger.info('Number of games played: %s', str(game_number))
        team_change(1)
        # pes_region.saveScreenCapture('./shot', 'test2')
        #original = cv2.imread("./shot/test1.png")
        #duplicate = cv2.imread("./shot/test2.png")
        # if original.shape == duplicate.shape:
        #     logger.info('Game seems to be working fine, continuing')
        # else:
        #     pes.close()
        #     time.sleep(20)
        #     playing_loop()

    # return
#playing_loop(10)

