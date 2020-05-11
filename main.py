import logging
import  sys
import os
import shutil
from keyboard import mouse
from lackey import *
import json
import vdf
import pytesseract
import argparse
try:
    from PIL import Image
except ImportError:
    import Image
import cv2
from azure_vm import *
from pesmail import send_mail

# ---------------------------------------------- ARGUMENTS PARSING

parser = argparse.ArgumentParser(description="PES-farming script. Use to automate sim matches.")
group = parser.add_mutually_exclusive_group()
group.add_argument("-r", "--restore", help="Restores PES original settings file to let you play normally", action="store_true")
group.add_argument("-p", "--prepare", help="Copies prepared PES settings file to let script navigate in game", action="store_true")
group.add_argument("-go", "--run", help="Run the script with defaults", action="store_true")
group.add_argument("-c", "--custom", help="Run script with function calls inside the #custom of main.py", action="store_true")
args = parser.parse_args()

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


def get_pes_exe():
    prgm_path = ""
    if os.environ.get("PROGRAMFILES(X86)") is None:  # this case is 32bit
        prgm_path = os.environ.get("PROGRAMFILES")
    else:
        prgm_path = os.environ.get("PROGRAMFILES(X86)")

    default_pes_path = prgm_path + '\Steam\steamapps\common\eFootball PES 2020\PES2020.exe'
    if isthere(default_pes_path):
        print('Pes installed in default location:' + default_pes_path)
        pes_config['general']['game_path'] = repr(default_pes_path).replace("'",'"')
        write_configurations()
        return repr(default_pes_path).replace("'",'"')
    else:
        lib_path = prgm_path + "\Steam\steamapps\libraryfolders.vdf"
        with open(lib_path, "r") as read_steam:
            steam_lib = vdf.load(read_steam)

        steam_library = {number: location for number, location in steam_lib['LibraryFolders'].items() if number.isdigit()}
        alternative_pes_path = ''

        for loc in steam_library.values():
            new_path = loc + '\steamapps\common\eFootball PES 2020\PES2020.exe'
            if isthere(new_path):
                alternative_pes_path = new_path
        logger.info("Pes installed in alternative location: %s", alternative_pes_path)
        pes_config['general']['game_path'] = alternative_pes_path
        write_configurations()
        return repr(alternative_pes_path).replace("'",'"')


# ------------------------------------------ DEFINE GAME VARIABLES
# Runtime variables:
pes_config = {}
pes_gui = False
converted_nr = 0
game_number = 0
gracefull_stop = False
aborted = False
shutdown = False

# Saved settings (variables)
# Load/prepare and load configuration.json
def load_configurations():
    if not isthere('configuration.json'):
        shutil.copy('template-configuration.json', 'configuration.json')

    if isthere('configuration.json'):
        with open('configuration.json', 'r') as to_read:
            global pes_config
            pes_config = json.load(to_read)

def write_configurations():
    global  pes_config
    with open('configuration.json', "w") as to_write:
        json.dump(pes_config, to_write)

load_configurations()

if len(pes_config['general']['game_path']) > 3:
    pes_path = r'{}'.format(repr(pes_config['general']['game_path']).replace("'",'"'))
else:
    pes_path = r'{}'.format(get_pes_exe())

pes_launcher = App(f'{pes_path}')
pesName = 'eFootball PES 2020'
pes = App() # Global variable to be used for app reference after initialization
pes_region = None
team_nr = 0
pes_frame = []
spots = {
    # use '@' to use default
    'money' : ([987, 67, 79, 29], '-psm 13'),
    'player_position' : ([957, 228, 51, 27], '-c tessedit_char_whitelist=BCDFMGKLRSW -psm 13'), #[949, 223, 69, 33],
    'player_rating' : ([921, 248, 93, 105], '-c tessedit_char_whitelist=0123456789 -psm 13'),
    'contract_duration' : ([1087, 484, 114, 46], '-c tessedit_char_whitelist=0123456789 -psm 13'),
    'surname' : ([904, 95, 363, 86],'@'), #[921, 146, 294, 35],
    'scouts' : ([553, 652, 83,26], '-psm 13'),
    'exp_trainers' : ([1111, 448, 42, 28], "-c tessedit_char_whitelist=0123456789 -psm 13")
}
error_count = 0
# Team template
# Pic, coordinates related to reserves, string reserved for surname, pic for filter, filter turns left:
position = {
    'gk': ['conv/gk.JPG', [1,1,1,0], '@', 'conv/gk_f.JPG', 1],
    'clb': ['conv/cb.JPG', [1,1,0,0], '@', 'conv/cb_f.JPG', 2],
    'crb': ['conv/cb.JPG', [1,2,0,0], '@', 'conv/cb_f.JPG', 2],
    'lb': ['conv/lb.JPG', [1,0,0,0], '@', 'conv/lb_f.JPG', 3],
    'rb': ['conv/rb.JPG', [1,3,0,0], '@', 'conv/rb_f.JPG', 4],
    'dmf': ['conv/dmf.JPG', [2,1,0,0], '@', 'conv/dmf_f.JPG', 5],
    'cml': ['conv/cmf.JPG', [2,0,0,0], '@', 'conv/cm_f.JPG', 6],
    'cmr': ['conv/cmf.JPG', [2,2,0,0], '@', 'conv/cm_f.JPG', 6],
    'lwf': ['conv/lwf.JPG', [3,0,0,0], '@', 'conv/lwf_f.JPG', 10],
    'rwf': ['conv/rwf.JPG', [3,2,0,0], '@', 'conv/rwf_f.JPG', 11],
    'cf': ['conv/cf.JPG', [3,1,0,0], '@', 'conv/cf_f.JPG', 13],
}
# with open('team1.json', "w") as to_write:
#     json.dump(position, to_write)
# ------------------------------------------- GAME
# Define navigation (works together with settings file for PES controller)
# Buttons
def simulate_button(button,long=0.1):
    pes.focus()
    time.sleep(0.3)
    keyDown(button)
    time.sleep(long)
    keyUp(button)
    logger.debug('Button %s pressed', button)
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
    simulate_button(Key.SHIFT, 0.6)
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
    if pes_gui:
        if aborted:
            sys.exit()
        pes.focus()
    # Update PES window
    global pes_region
    pes_region = pes.window()
    #pes_region.highlight(1)
    #logger.debug('PES height: %s, width: %s, position(x,y): %s, %s', pes_region.getH(), pes_region.getW(), pes_region.getX(), pes_region.getY())

    if pes_region.exists(Pattern(img).similar(similarity), seconds):
        time.sleep(0.7)
        #pes_region.exists(Pattern(img).similar(similarity), seconds).highlight(1)
        logger.debug('%s match found', img)
        return True
    else:
        logger.warning('%s not found', img)
        global error_count
        error_count +=1
        error_check()
        return False

# Errors number checking
def error_check(allowed=30):
    global error_count
    if error_count > allowed:
        logger.info('Global error count is higher than %s, switching off in 5 minutes',allowed)
        global pes_region
        pes_region.saveScreenCapture('./shot', 'screen_to_mail')
        time.sleep(5)
        send_mail(sendgrid_api_key=pes_config['secrets']['sendgrid_api_key'], to_email=pes_config['general']['email_address'])
        time.sleep(300)
        stop_vm(compute_client)
# press_A when matched photo (a) within timeout (b)
def proceed(a, b):
    isok(a, b)
    press_A()
    return


def base_ok(a=5):
    global error_count
    if isok('img/club-house.JPG', a):
        logger.info('On home menu')
        error_count = 0
        return True
    else:
        logger.error('Not on home base, can\' proceed')
        error_count +=13
        return False

########################################################### CONSTRUCTION AREA
# Find coordinates of img pattern and write it down
def locate(im_path):
    dupa = pes_region.exists(Pattern(im_path).similar(0.8), 5)
    #adjust = set_pes_frame()
    print('Coordinates: ',dupa.getX()-pes_frame[0], dupa.getY()-pes_frame[1], dupa.getW(), dupa.getH())
    dupa.highlight(1)

# Playground
#locate('shot/contract_duration.JPG')


# Takes current pes window XY and object name, checks object dictionary by provided name
# and updates global variable with real object XYWH adjusted to pes window
# TODO to set global relative coordinates for all objects on initialize (and not move window or set watcher),
#  or create variable and use coordset every time?
def coordset(pes_xy, object_name):
    #global spots
    obj_coordinates = spots[object_name][0].copy()
    # spots[object_name][0] = spots[object_name][0] + pes_xy[0]
    # spots[object_name][1] = spots[object_name][1] + pes_xy[1]
    obj_coordinates[0] = obj_coordinates[0] + pes_xy[0]
    obj_coordinates[1] = obj_coordinates[1] + pes_xy[1]
    logger.info('Object x=%s, y=%s, w=%s, h=%s', *obj_coordinates)
    return obj_coordinates


# Takes object name, checks it's relevant coordinates and recognizes value

def recognize(object_name, conf_options='outputbase digits'):
    if conf_options != 'outputbase digits':
        conf_options = conf_options
    elif spots[object_name][1] != '@':
        conf_options = spots[object_name][1]
    pict = Region(*coordset(pes_frame, object_name))
    pict_size = (pict.getW()*3,pict.getH()*3)
    image_value = pytesseract.image_to_string(cv2.resize(pict.getBitmap(),pict_size), lang='equ+eng', config=conf_options)
    time.sleep(1)
    #pict.highlight(1)
    return image_value


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
        #if isok('img/skip-graphic.JPG', 10):
        #   press_Y()
    # Halftime - click ok to start new match
    if isok('img/halftime.JPG', 650):
        press_A()
    if isok('img/second-half.JPG', 120):
        press_A()
    # Skip highlights 6' 6"
    if isok('img/highlights.JPG', 820):
        press_menu()
        #if isok('img/fulltime.JPG',10):
        #    press_A()
        #else:
        #    press_menu()

    # Experience
    if isok('img/next-finish.JPG', 230):
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
    #TODO choose to prolongue players contracts or not, use that signal to start shift_change()
    if isok('img/contract-confirm1.JPG', 10) and not isok('img/contract-renewal-manager.JPG',5):

        press_A()

    elif isok('img/contract-renewal-manager.JPG',5):
        turn_right(1)
        press_A()

        if isok('img/pay-gp.JPG', 10):
            press_A()

        if isok('img/sure-pay.JPG', 10):
            turn_right(1)
            press_A()

        if isok('img/contracts-renewed.JPG', 10):
            press_A()
            time.sleep(3)

        if isok('img/contracts-renewed.JPG', 10):
            press_A()

        if isok('img/contract-manager-upd.JPG', 10):
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
    global error_count
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
                time.sleep(0.5)
                if fivestars:
                    turn_down(fivestars)
                    if int(recognize('scouts').split('/')[0]) == int(fivestars):
                        press_B()
                        logger.info('No scouts left or only skipped left. Sign all script finished, going back')
                        break
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
                # If no scouts - break
                elif isok('sign/no-scouts.JPG', 3):
                    logger.warning('No scouts left, all signed')
                    press_A()
                    error_count -= 1
                    break
        # Get back to home once all sold
        if isok('sign/choose-slot.JPG', 5):
            press_B()
        if isok('sign/sign-enter.JPG', 5):
            press_B()
        if isok('sign/scout.JPG', 5):
            turn_left(4)

        if isok('img/club-house.JPG', 10):
            logger.info('sign_all script finished')
        else:
            error_count += 15
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
        if isok('conv/reserves.JPG', 8):
            logger.info('On reserves')
            return True
        else:
            global error_count
            error_count -= 1
            logger.warning('Not on reserves')
            return False

    # Open reserves
def to_reserves():
        while not on_reserves():
            keyDown(Key.DOWN)
            keyDown(Key.LEFT)
            time.sleep(3)
            keyUp(Key.DOWN)
            keyUp(Key.LEFT)

# NOT USED
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
# Convert player into EXP trainer
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
# TODO convert all low level players - recognize level and decide of converting:
def players_convert():
    team_color = ''
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

# Converts and populates squads of playing teams:
def smart_players_convert(which_teams=12, populate=True, execute=True):
    def safe_pl_rating():
        try:
            players_rating = int(recognize('player_rating'))
        except ValueError:
            players_rating = 85
        return players_rating

    def team_execute():
        if base_ok(9):
            logger.info('On base, entering team for execution')
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
            if isok('conv/no_player.JPG',1):
                logger.info('No player, skipping %s', key)
                continue
            else:
                global error_count
                error_count -= 1
                exec_victim(3)
            if pes_gui:
                global converted_nr
                converted_nr += 1
            # if safe_pl_rating() < rating:
            #     logger.info('Converting player to EXP trainer')
            #     exec_victim(3)
            # else:
            #     logger.warning('Player on position %s with rating %s or more is in the team, skipping this one', key,
            #                    rating)
            #     value[2] = recognize('surname', '')
            #     continue
        with open("team1.json", "w") as to_write:
            json.dump(position, to_write)
        del position
        while not base_ok(3):
            press_B()

    def populate_team(which_team=1):
        global error_count
        if base_ok(9):
            logger.info('On base, entering team for population')
            press_A()
        #global position
        if isok('conv/on_team.JPG', 5):
            logger.info('Entered team')
        if which_team == 1:
            team_file1 = 'team1.json'
            team_file2 = 'team2.json'
        else:
            team_file1 = 'team2.json'
            team_file2 = 'team1.json'

        with open(team_file1, 'r') as to_read:
            position1 = json.load(to_read)
        with open(team_file2, 'r') as to_read2:
            position2 = json.load(to_read2)

        for key, value in position1.items():
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
            time.sleep(0.5)
            to_reserves()
            press_A()
            # Use filter
            time.sleep(0.5)
            press_rs()
            #turn_left(value[4])
            if isok(value[3],1.5):
                logger.info('Position %s filter applied', key)
            else:
                while not isok(value[3],1):
                    turn_left(1)
            turn_down(2)
            if isok('conv/value_f.JPG',2,0.95):
                logger.info('Value filter applied')
            else:
                while not isok('conv/value_f.JPG',1.5,0.98):
                    turn_left(1)
            turn_down(4)
            press_A()
            time.sleep(0.5)
            if isok('conv/filtered.JPG', 2):
                logger.info('Filters applied')
                if error_count < 15:
                    error_count = 0
            keyDown(Key.DOWN)
            time.sleep(2)
            keyUp(Key.DOWN)
            while not isok('conv/on_team.JPG',3):
                error_count -= 1
                time.sleep(0.5)
                found = False
                for i in range(6):
                    #if isok(value[0],2):
                     #   logger.info('Found match for %s', value[0])
                        # if safe_pl_rating() < rating:
                        #     logger.info('Player\'s rating is %s, which is smaller than %s',safe_pl_rating(), rating)
                        #     if value[2] != recognize('surname',''):
                        #         value[2] = recognize('surname','')
                        #         logger.info('New player %s set on position %s', value[2], key)
                        #         with open("team1.json", "w") as to_write:
                        #             json.dump(position, to_write)
                        #found = True
                        #press_A()
                        #break
                    try:
                        surname = ''.join(char for char in recognize('surname','') if ord(char) < 128 and not char.isdigit() and not char == ' ')
                    except 'Tcl_AsyncDelete':
                        logger.warning('Tcl_AsyncDelete occured, trying again')
                        time.sleep(2)
                        surname = ''.join(char for char in recognize('surname','') if ord(char) < 128 and not char.isdigit() and not char == ' ')

                    print(surname)
                    team1_names = [value[2] for (key,value) in position1.items()]
                    team2_names = [value[2] for (key,value) in position2.items()]
                    known_names = team1_names + team2_names
                    if surname != '' and surname not in known_names:
                        value[2] = surname
                        logger.info('New player found: %s', surname)
                        found = True
                        with open(team_file1, "w") as to_write:
                            json.dump(position1, to_write)
                    if not found:
                        logger.info('Not %s, turning right', key)
                        turn_right(1)
                    if found == True:
                        logger.info('Found new player for position %s, job done.', key)
                        found = False
                        while not isok('conv/on_team.JPG',3):
                            press_A()
                        break
    #             elif safe_pl_rating() >= rating:
    #                 logger.info('No low leveled players for %s position, picking any.', key)
    #                 turn_down(10)
    # #                while not safe_pl_rating() < rating and value[2] != recognize('surname',''):
    #                 while not value[2] != recognize('surname', ''):
    #                     logger.info('Player not found in the row, going up')
    #                     turn_right(1)
    #                     turn_up(1)
    #                 logger.info('Another player found')
    #                 press_A()
    #                 break
                else:
                    logger.info('No suitable players in reserves row, up for 1 row')
                    turn_up(1)
            time.sleep(2)

            # TODO find_replacement (create function to find correct new player):
            # rating is ok, name is not same as in value[2], write name to value[2]
        del position1
        time.sleep(1)
        while not base_ok():
            press_B()

    if which_teams == 12:
        team_change(1)
        team_execute()
        logger.info('Team nr: %s recreated', int(team_nr))
        team_change(2)
        team_execute()
        logger.info('Team nr: %s recreated', int(team_nr))
        team_change(1)
        populate_team(1)
        logger.info('Team nr: %s recreated', int(team_nr))
        team_change(2)
        populate_team(2)
        logger.info('Team nr: %s recreated', int(team_nr))
    else:
        if True in (execute, populate):
            team_change(which_teams)
            if execute:
                team_execute()
                logger.info('Team nr: %s recreated', int(team_nr))
            if populate:
                populate_team(which_teams)
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
            if pes.isRunning(5) and pes.getName().lower()!='steam.exe':
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
def smart_playing_loop(file=False, smart=0, number=1000):
    initialize_pes()
    if base_ok():
        logger.info('Game is on, no need to start')
    else:
        start_game()
    fplayed = open('games_played.txt', 'r')
    fplayed_value = int(fplayed.read())
    if file == False:
        game_number = 0
    else:
        if fplayed_value == 0:
            game_number = 0
        else:
            game_number = fplayed_value
    fplayed.close()
    smart_start = smart
    def shift_change():
        sign_all()
        smart_players_convert()

    for i in range(number):
        global error_count
    #while True:
        if team_nr == 0 or team_nr == 2:
            team_change(1)
        else:
            team_change(2)
        play_one()
        time.sleep(1)
        game_number += 1
        write_to_file = open('games_played.txt', 'w+')
        write_to_file.write(str(game_number))
        write_to_file.close()
        logger.info('Number of games played: %s', str(game_number))
        logger.info('Number of errors occured: %s', str(error_count))
        if smart_start > 0:
            if game_number % (smart_start * 2) == 0:
                print('Debug: ',(game_number % (smart_start * 2)))
                shift_change()
                smart_start = 0
                game_number = 0
        else:
            if game_number % 20 == 0:
                shift_change()

    # TODO Communication error handling
    #  During match - "Lost pres ok", right after match:
    #  1.Connection lost
    #  2. Communication error
    #  3. Experience Points
    #  If out of match  - drops to main menu - new login to MyClub required




# -------------------------------------------- RUN SCRIPT (WITH ARGUMENTS)
if args.run:
    smart_playing_loop()
if args.restore:
    revertbackup()
if args.prepare:
    makebkp()

# Custom goes here:
if args.custom:
    print('Runing with custom')
    # playing_loop()
    # initialize_pes()
    # sign_all()
    # smart_players_convert()
    # #ddd = ''.join([char for char in recognize('surname','') if not char.isdigit() and not char == ' '] and not ord(char) < 128)
    # ddd = ''.join(char for char in recognize('surname','') if ord(char) < 128 and not char.isdigit() and not char == ' ')
    # print(ddd)
    # smart_playing_loop(True)
    # smart_playing_loop(False, 2, 1000)
    # smart_playing_loop(False,4,10)
    # for i in range(1000):
    #     surname = ''.join(
    #         char for char in recognize('surname', '') if ord(char) < 128 and not char.isdigit() and not char == ' ')
    #     print(surname, i)
    # TODO post tasks:
    # daily-bonus.JPG
    #
    #
    #pes_region.saveScreenCapture('./shot', 'screen_to_mail')
    #r'"D:\\Steam\\steamapps\\common\\eFootball PES 2020\\PES2020.exe"'


def dummy_playing_loop():
    for i in range(10):
        time.sleep(2)
        logger.info(f'Numbers of dummy games played: {i}')
        global game_number
        game_number +=1
        global error_count
        error_count += 2
        global team_nr
        team_nr = 1 if team_nr > 1 else 2
        if aborted:
            sys.exit()
        if gracefull_stop:
            break
    logger.info(f'Dummy playig loop finished')