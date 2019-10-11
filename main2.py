import logging
import os
import shutil
from keyboard import mouse
import pytesseract
from lackey import *
import json
try:
    from PIL import Image
except ImportError:
    import Image

# ---------------------------------------------- LOGGING HANDLING

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Set format for logs
formatter = logging.Formatter('[%(levelname)s:%(asctime)s:%(funcName)20s() ]: %(message)s')

# File handler - file name, format, level
file_handler = logging.FileHandler('test.log')
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
pes_frame = []
spots = {
    'money' : [987, 34, 113, 107],
    'player_position' : [861, 222, 178, 35], #[949, 223, 69, 33],
    'player_rating' : [921, 248, 93, 105],
    'contract_duration' : [1059, 476, 231, 67],
    'surname' : [904, 95, 363, 86], #[921, 146, 294, 35],
}
# Pic, coordinates related to reserves, string reserved for surname
# position = {
#     'gk': ['conv/gk.JPG', [1,1,1,0], '@'],
#     'lb': ['conv/lb.JPG', [1,0,0,0], '@'],
#     'clb': ['conv/cb.JPG', [1,1,0,0], '@'],
#     'crb': ['conv/cb.JPG', [1,2,0,0], '@'],
#     'rb': ['conv/rb.JPG', [1,3,0,0], '@'],
#     'cml': ['conv/cmf.JPG', [2,0,0,0], '@'],
#     'dmf': ['conv/dmf.JPG', [2,1,0,0], '@'],
#     'cmr': ['conv/cmf.JPG', [2,2,0,0], '@'],
#     'lwf': ['conv/lwf.JPG', [3,0,0,0], '@'],
#     'cf': ['conv/cf.JPG', [3,1,0,0], '@'],
#     'rwf': ['conv/rwf.JPG', [3,2,0,0], '@'],
# }
# ------------------------------------------- GAME
# Define navigation (works together with settings file for PES controller)

def simulate_button(button):
    pes.focus()
    time.sleep(0.3)
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

def press_rs():
    simulate_button(Key.ADD)
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
        pes_region.exists(Pattern(img).similar(similarity), seconds).highlight(1)
        logger.info('%s match found', img)
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

########################################################### CONSTRUCTION AREA
# Find coordinates of img pattern and write it down
def locate(im_path, time=5):
    dupa = pes_region.exists(Pattern(im_path).similar(0.8), time)
    #adjust = set_pes_frame()
    pic_coor = [
        dupa.getX() - pes_frame[0],
        dupa.getY() - pes_frame[1],
        dupa.getW(),
        dupa.getH()
        ]

    print('Coordinates: ',dupa.getX()-pes_frame[0], dupa.getY()-pes_frame[1], dupa.getW(), dupa.getH())
    dupa.highlight(1)
    return pic_coor


# Playground
#locate('shot/contract_duration.JPG')


# Takes current pes window XY and object name, checks object dictionary by provided name
# and updates global variable with real object XYWH adjusted to pes window
# TODO to set global relative coordinates for all objects on initialize (and not move window or set watcher),
#  or create variable and use coordset every time?
def coordset(pes_xy, object_name):
    #global spots
    obj_coordinates = spots[object_name].copy()
    # spots[object_name][0] = spots[object_name][0] + pes_xy[0]
    # spots[object_name][1] = spots[object_name][1] + pes_xy[1]
    obj_coordinates[0] = obj_coordinates[0] + pes_xy[0]
    obj_coordinates[1] = obj_coordinates[1] + pes_xy[1]
    logger.info('Object x=%s, y=%s, w=%s, h=%s', *obj_coordinates)
    return obj_coordinates


# Takes object name, checks it's relevant coordinates and recognizes value

def recognize(object_name, conf_options='outputbase digits'):
    pict = Region(*coordset(pes_frame, object_name))
    dupa = pytesseract.image_to_string(pict.getBitmap(), lang='equ+eng', config=conf_options)
    return dupa


###########################################################

#       ------------------------------------ PROCEDURES --------------------------------------

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
    if isok('img/live-update.JPG', 17):
        press_A()
    if isok('img/featured-players.JPG', 17):
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
    logger.info('Team number changed to: %s', team_nr)
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
    time.sleep(300)
    if isok('img/halftime.JPG',300):
    #    time.sleep(10)
        press_A()
    #else:
    #    press_A()
    if isok('img/second-half.JPG', 120):
    #    time.sleep(10)
    #else:
        press_A()
    # Skip highlights
    time.sleep(300)
    if isok('img/highlights.JPG', 400):
    #    time.sleep(10)
    #else:
        press_menu()

    # Experience
    if isok('img/next-finish.JPG', 30):
        press_A()
        # # Experience points (press A twice to proceed)
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
    #    time.sleep(1)
        press_A()
    #else:
    #    press_A()

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
                # if fivestars > 0:
                #     for i in range(fivestars):
                #         if isok('sign/five-star.JPG', 1, 0.96):
                #             logger.info('%s in list is Five star player', i)
                #             turn_down(1)
                #         else:
                #             logger.info('No fivestar players %s', i)
                #     if isok('sign/five-star.JPG', 1, 0.96):
                #         logger.info('More 4-5 stars than provided or all other used. Escaping.')
                #         press_B()
                #         break
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
# ----------------  PLAYERS CONVERTING ---------------------------
def on_reserves():
        # Define white or bronze team 0=no, 1=white, 2=bronze
        if isok('conv/reserves.JPG', 8):
            logger.info('On reserves')
            return True
        else:
            logger.warning('Not on reserves')
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
def to_reserves():
        while not on_reserves():
            keyDown(Key.DOWN)
            keyDown(Key.LEFT)
            time.sleep(3)
            keyUp(Key.DOWN)
            keyUp(Key.LEFT)
            # turn_down(5)
            # turn_left(5)
        #press_A()

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

def exec_victim(turns_down=2):
        logger.info('Looking for victim')
        press_X()
        if isok('conv/player-menu.JPG', 5):
            turn_down(turns_down)
        if isok('conv/convert.JPG', 5):
            press_A()
        if isok('conv/no.JPG', 5):
            turn_right(1)
            press_A()
        if isok('conv/converted.JPG', 5):
            press_A()

def players_convert():
    team_color = ''
    #TODO think on logick of how to execute, how many, when etc
    for i in range(1,3):
        if base_ok():
            logger.info('Starting players to EXP trainers convertion')
            team_change(i)
        if base_ok():
            press_A()
        while True:
            to_reserves()
            press_A()
            if find_victim():
                exec_victim()
            else:
                break

def smart_players_convert(rating=80):
    def safe_pl_rating():
        try:
            players_rating = int(recognize('player_rating'))
        except ValueError:
            players_rating = 85
        return players_rating

    def team_execute():
        if base_ok():
            logger.info('On base, entering team')
            press_A()
        with open('team1.json', 'r') as to_read:
            position = json.load(to_read)
        for key, value in position.items():
            logger.info('Position %s, name %s', key, value[2])
            to_reserves()
            turn_up(value[1][0])
            turn_right(value[1][1])
            turn_down(value[1][2])
            turn_left(value[1][3])
            time.sleep(0.5)
            if safe_pl_rating() < rating:
                logger.info('Converting player to EXP trainer')
                exec_victim(3)
            else:
                logger.warning('Player on position %s with rating %s or more is in the team, skipping this one', key,
                               rating)
                value[2] = recognize('surname', '')
                continue
        with open("team1.json", "w") as to_write:
            json.dump(position, to_write)
        del position
        press_B()

    def populate_team():
        if base_ok():
            logger.info('On base, entering team')
            press_A()
        #global position
        with open('team1.json', 'r') as to_read:
            position = json.load(to_read)

        for key, value in position.items():
            logger.info('Position %s, name %s', key, value[2])
            to_reserves()
            turn_up(value[1][0])
            turn_right(value[1][1])
            turn_down(value[1][2])
            turn_left(value[1][3])
            time.sleep(0.5)

            # Open reserves and go down
            logger.info('Looking for another player to play on %s position', key)
            time.sleep(1)
            press_A()
            to_reserves()
            press_A()
            # Use filter
            time.sleep(0.5)
            press_rs()
            turn_down(2)
            turn_left(1)
            turn_down(4)
            press_A()
            time.sleep(0.5)
            if isok('conv/filtered.JPG', 2):
                logger.info('Filter applied')
            keyDown(Key.DOWN)
            time.sleep(3)
            keyUp(Key.DOWN)
            while not isok('conv/on_team.JPG',3):
                time.sleep(0.5)
                found = False
                for i in range(6):
                    if isok(value[0],2):
                        logger.info('Found match for %s', value[0])
                        if safe_pl_rating() < rating:
                            logger.info('Player\'s rating is %s, which is smaller than %s',safe_pl_rating(), rating)
                            if value[2] != recognize('surname',''):
                                value[2] = recognize('surname','')
                                logger.info('New player %s set on position %s', value[2], key)
                                found = True
                                press_A()
                                break
                    if not found:
                        logger.info('Not %s, turning right', key)
                        turn_right(1)
                if found:
                    logger.info('Found new player for position %s, job done.', key)
                    break
                elif safe_pl_rating() >= rating:
                    logger.info('No low leveled players for %s position, picking any.', key)
                    turn_down(10)
    #                while not safe_pl_rating() < rating and value[2] != recognize('surname',''):
                    while not value[2] != recognize('surname', ''):
                        logger.info('Player not found in the row, going up')
                        turn_right(1)
                        turn_up(1)
                    logger.info('Another player found')
                    press_A()
                    break
                else:
                    logger.info('No suitable players in reserves row, up for 1 row')
                    turn_up(1)
            time.sleep(2)

            # TODO find_replacement (create function to find correct new player):
            # rating is ok, name is not same as in value[2], write name to value[2]
        with open("team1.json", "w") as to_write:
            json.dump(position, to_write)
        del position
        press_B()
    team_change(1)
    team_execute()
    logger.info('Team nr: %s recreated', int(team_nr))
    team_change(2)
    team_execute()
    logger.info('Team nr: %s recreated', int(team_nr))
    team_change(1)
    populate_team()
    logger.info('Team nr: %s recreated', int(team_nr))
    team_change(1)
    populate_team()
    logger.info('Team nr: %s recreated', int(team_nr))



# TESTS
#TODO: put it all together

# INITIALIZE GAME (make sure settings are ready, game has started and app instance created).
# Set PES frame
def set_pes_frame():
    global pes_frame
    pes_frame = [pes_region.getX(),
                 pes_region.getY(),
                ]
    return pes_frame

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
    set_pes_frame()
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



# Play one game after another changing squads in between
#TODO find place for playing loop, find logick for number of games played etc.
def playing_loop(number=1000, smart=False):
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
def smart_playing_loop(smart=0, number=1000):
    initialize_pes()
    if base_ok():
        logger.info('Game is on, no need to start')
    else:
        start_game()
    game_number = 0
    smart_start = smart
    def shift_change():
        sign_all()
        smart_players_convert()

    for i in range(number):
    #while True:
        if team_nr == 0 or team_nr == 2:
            team_change(1)
        else:
            team_change(2)
        play_one()
        time.sleep(1)
        game_number += 1
        logger.info('Number of games played: %s', str(game_number))
        if smart_start > 0:
            if game_number % (smart_start * 2) == 0:
                print('Debug: ',(game_number % (smart_start * 2)))
                shift_change()
                smart_start = 0
        elif game_number % 18 == 0:
            shift_change()


# pic_path = [
#     'img/press-button.jpg',
#     'img/club-house.JPG',
#     'img/online-confirm.jpg',
#     'img/this-week-pick-up.JPG',
#     'img/game-screen.JPG',
#     'img/myclub-enter.JPG',
#     'img/sure-start.JPG',
#     'img/live-update.JPG',
#     'img/featured-players.JPG',
#     'img/proceed-btn.JPG',
#     'img/no-new-updates.JPG',
#     'img/proceed-small.JPG',
#     'img/big-ok.JPG',
#     'img/squad-list.JPG',
#     'img/sim-game.JPG',
#     'img/kickoff.JPG',
#     'img/match-started.JPG',
#     'img/skip-graphic.JPG',
#     'img/halftime.JPG',
#     'img/second-half.JPG',
#     'img/highlights.JPG',
#     'img/next-finish.JPG',
#     'img/experience.JPG',
#     'img/experience.JPG',
#     'img/levelup.JPG',
#     'img/rating.JPG',
#     'img/reward.JPG',
#     'img/reward2.JPG',
#     'img/contract-manager-upd.JPG',
#     'img/contract-confirm1.JPG',
#     'img/pay-gp.JPG',
#     'img/sure-pay.JPG',
#     'img/contracts-renewed.JPG',
#     'sign/scout.JPG',
#     'sign/sign-enter.JPG',
#     'sign/choose-slot.JPG',
#     'sign/no-scouts.JPG',
#     'sign/five-star.JPG',
#     'sign/confirm.JPG',
#     'sign/chosed-trainer.JPG',
#     'sign/sure.JPG',
#     'sign/skip.JPG',
#     'sign/confirm-player.JPG',
#     'sign/next.JPG',
#     'sign/added.JPG',
#     'sign/choose-slot.JPG',
#     'sign/sign-enter.JPG',
#     'sign/scout.JPG',
#     'img/club-house.JPG',
#     'sign/scout.JPG',
#     'sign/sign-enter.JPG',
#     'sign/sell-enter.JPG',
#     'sign/no-scouts-left.JPG',
#     'sign/unchecked.JPG',
#     'sign/last-checked.JPG',
#     'sign/confirm-sell.JPG',
#     'sign/reward-received.JPG',
#     'sign/no-scouts-left.JPG',
#     'sign/scout.JPG',
#     'conv/reserves.JPG',
#     'conv/white-ball.JPG',
#     'conv/bronze-ball.JPG',
#     'conv/reserves-list.JPG',
#     'conv/white-ball.JPG',
#     'conv/bronze-ball.JPG',
#     'conv/black-ball.JPG',
#     'conv/gold-ball.JPG',
#     'conv/black-ball.JPG',
#     'conv/player-menu.JPG',
#     'conv/convert.JPG',
#     'conv/no.JPG',
#     'conv/converted.JPG',
#     'sign/sign-enter.JPG',
# ]
# Tesseract for output base digits
# tesseract money100.PNG stdout outputbase digits
position = {
    'gk': ['conv/gk.JPG', [1,1,1,0], '@'],
    'lb': ['conv/lb.JPG', [1,0,0,0], '@'],
    'clb': ['conv/cb.JPG', [1,1,0,0], '@'],
    'crb': ['conv/cb.JPG', [1,2,0,0], '@'],
    'rb': ['conv/rb.JPG', [1,3,0,0], '@'],
    'cml': ['conv/cmf.JPG', [2,0,0,0], '@'],
    'dmf': ['conv/dmf.JPG', [2,1,0,0], '@'],
    'cmr': ['conv/cmf.JPG', [2,2,0,0], '@'],
    'lwf': ['conv/lwf.JPG', [3,0,0,0], '@'],
    'cf': ['conv/cf.JPG', [3,1,0,0], '@'],
    'rwf': ['conv/rwf.JPG', [3,2,0,0], '@'],
}


# dictionary = {
#     'key' : [1, 2, 3, 4],
#
# }

# for i in mydict:
#     print(i, pytesseract.image_to_string(mydict[i],config='outputbase digits'))
#image_to_data(image, lang=None, config='', nice=0, output_type=Output.STRING, timeout=0)
# print(pytesseract.image_to_string(mydict[6], config='outputbase digits'))
# print(int(pytesseract.image_to_string(mydict[6], config='outputbase digits')))
initialize_pes()

with open('pic_path.json', 'r') as f:
    pic_path = json.load(f)

for path in pic_path:
    if isok(path, 1, 0.90):
        coordinates = locate(path,1)
        with open('position.json', 'r') as f:
            dictionary = json.load(f)

        if path in dictionary.keys():
            pic_path.remove(path)
            with open('pic_path.json', 'w') as f:
                json.dump(pic_path, f)
            continue
        else:
            dictionary[path] = coordinates
        with open('position.json','w') as f:
            json.dump(dictionary, f)
        break

# with open('pic_path.json', 'w') as f:
#     json.dump(pic_path, f)

#playing_loop(10)
# smart_players_convert()
#smart_playing_loop(6)