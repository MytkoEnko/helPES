import logging

import os
import time
import sys

from shutil import copy
from lackey import *
from json import load as json_load, dump as json_dump
from vdf import load as vdf_load
from pytesseract import image_to_string as pytesseract_image_to_string, get_tesseract_version as pytesseract_get_tesseract_version, pytesseract
import argparse
from cv2 import resize as cv2_resize
from pesmail import send_mail
from sys import exc_info

# ---------------------------------------------- ARGUMENTS PARSING

parser = argparse.ArgumentParser(description="helPES App. Use it to automate sim matches and else.")
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
file_handler = logging.FileHandler('helPES.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.DEBUG)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# ------------------------------------------ DEFINE GAME VARIABLES
# Runtime variables:
pes_config = {}
pes_gui = False
converted_nr = 0
game_number = 0
gracefull_stop = False
aborted = False
shutdown = False
error_threshold = 40
pes_path = ''
pesName = ''


# Check if path exists
def isthere(a):
    if os.path.exists(a):
        return True
    else:
        return False

# Load/prepare and load configuration.json
def load_configurations():
    if not isthere('configuration.json'):
        copy('template-configuration.json', 'configuration.json')

    if isthere('configuration.json'):
        with open('configuration.json', 'r') as to_read:
            global pes_config
            pes_config = json_load(to_read)

def write_configurations():
    global  pes_config
    with open('configuration.json', "w") as to_write:
        json_dump(pes_config, to_write)

load_configurations()

def get_pes_exe(version="21"):
    prgm_path = ""
    if os.environ.get("PROGRAMFILES(X86)") is None:  # this case is 32bit
        prgm_path = os.environ.get("PROGRAMFILES")
    else:
        prgm_path = os.environ.get("PROGRAMFILES(X86)")

    default_pes_path = prgm_path + f'\Steam\steamapps\common\eFootball PES 20{version}\PES20{version}.exe'
    if isthere(default_pes_path):
        logger.info('Pes installed in default location:' + default_pes_path)
        pes_config['general'][f'game_path{version}'] = default_pes_path
        write_configurations()
        return default_pes_path
    else:
        lib_path = prgm_path + "\Steam\steamapps\libraryfolders.vdf"
        with open(lib_path, "r") as read_steam:
            steam_lib = vdf_load(read_steam)

        steam_library = {number: location for number, location in steam_lib['LibraryFolders'].items() if number.isdigit()}
        alternative_pes_path = ''

        for loc in steam_library.values():
            new_path = loc + f'\steamapps\common\eFootball PES 20{version}\PES20{version}.exe'
            if isthere(new_path):
                alternative_pes_path = new_path
        if alternative_pes_path:
            logger.info(f"PES20{version} installed in alternative location: {alternative_pes_path}")
            pes_config['general'][f'game_path{version}'] = alternative_pes_path
            write_configurations()
            return alternative_pes_path
        else:
            return alternative_pes_path

# Update runtime variables default values
contract_1 = pes_config['gui']['team1_contract_var']
contract_2 = pes_config['gui']['team2_contract_var']
contract_m = pes_config['gui']['manager_contract_var']
max_player_cost = pes_config['gui']['players_cost_var']

def set_paths(version="01"):
    for i in "21","20":
        #if len(pes_config['general'][f'game_path{i}']) < 300:
        pes_config['general'][f'game_path{i}'] = r'{}'.format(get_pes_exe(i))
    if not pes_config['general']['pes_version']:
        pes_config['general']['pes_version'] = "21" if pes_config['general'][f'game_path21'] \
            else "20" if pes_config['general'][f'game_path21'] \
            else "NO_PES_INSTALLED"
        write_configurations()
    global pes_path
    if version == "01":
        pes_path = r'{}'.format(repr(pes_config['general'][f'game_path{pes_config["general"]["pes_version"]}']).replace("'",'"'))
    else:
        pes_path = r'{}'.format(repr(pes_config['general'][f'game_path{version}']).replace("'", '"'))
        pes_config['general']['pes_version'] = version
        write_configurations()

    global pesName
    pesName = f'eFootball PES 20{pes_config["general"]["pes_version"]}'

    global settings_path,settings_file,settings_backup,settings_pesbot
    settings_path = os.path.expanduser(f'~/Documents/KONAMI/eFootball PES 20{"21 SEASON UPDATE" if pes_config["general"]["pes_version"]  == "21" else "20"}/')
    settings_file = settings_path + 'settings.dat'
    settings_backup = settings_path + 'settings.dat.pes-bkp'
    settings_pesbot = f'settings{pes_config["general"]["pes_version"]}.dat'

set_paths()

# if len(pes_config['general']['game_path20']) > 3:
#     pes_path = r'{}'.format(repr(pes_config['general']['game_path20']).replace("'",'"'))
# else:
#     pes_path = r'{}'.format(get_pes_exe())

pes = App() # Global variable to be used for app reference after initialization
pes_region = None
team_nr = 0
pes_frame = []
spots = {
    # use '@' to use default
    'money' : ([987, 67, 79, 29], '-c tessedit_char_whitelist=0123456789, --psm 13'),
    'player_position' : ([957, 228, 51, 27], '-c tessedit_char_whitelist=BCDFMGKLRSW --psm 13'), #[949, 223, 69, 33],
    'player_rating' : ([921, 248, 93, 105], '-c tessedit_char_whitelist=0123456789 --psm 13'),
    'contract_duration' : ([1087, 484, 114, 46], '-c tessedit_char_whitelist=0123456789 --psm 5'),
    'surname' : ([904, 95, 363, 86],''), #[921, 146, 294, 35],
    'scouts' : ([553, 652, 83,26], 'tessedit_char_whitelist=0123456789/ --psm 13'),
    'exp_trainers' : ([1111, 448, 42, 28], "-c tessedit_char_whitelist=0123456789 --psm 13"),
    'coach_contract' : ([1092, 442, 103, 45], "-c tessedit_char_whitelist=0123456789 --psm 13"),
    'formation1' : ([827, 377, 111, 37], "@"),
    'formation2' : ([821, 526, 123, 38], "@")
}
areas = {
    'conv/10.JPG': [701, 294, 242, 77],
    'conv/15.JPG': [701, 294, 242, 77],
    'conv/20.JPG': [701, 294, 242, 77],
    'conv/25.JPG': [701, 294, 242, 77],
    'conv/30.JPG': [701, 294, 242, 77],
    "conv/gk_f.JPG" : [729, 229, 199, 61],
    "conv/lb_f.JPG": [729, 229, 199, 61],
    "conv/cb_f.JPG": [729, 229, 199, 61],
    "conv/rb_f.JPG": [729, 229, 199, 61],
    "conv/cm_f.JPG": [729, 229, 199, 61],
    "conv/dmf_f.JPG": [729, 229, 199, 61],
    "conv/lwf_f.JPG": [729, 229, 199, 61],
    "conv/cf_f.JPG": [729, 229, 199, 61],
    "conv/rwf_f.JPG": [729, 229, 199, 61],
    "conv/on_team.JPG" : [11, 219, 207, 285],
    "conv/reserves.JPG" : [879, 88, 374, 159],
    "conv/filtered.JPG" : [47, 64, 711, 546],
    "conv/player-menu.JPG" : [212, 148, 363, 224],
    "conv/convert.JPG" : [268, 253, 738, 228],
    "conv/no.JPG" : [234, 227, 860, 377],
    "conv/converted.JPG" : [166, 78, 951, 332],
    'img/rating.JPG' : [471, 92, 361, 108],
    'img/reward.JPG' : [395, 106, 508, 272],
    'img/press-button20.jpg' : [127, 360, 493, 250],
    'img/press-button21.jpg' : [127, 360, 493, 250],
    'img/this-week-pick-up.JPG' : [243, 33, 442, 107],
    'img/game-screen20.JPG' : [9, 32, 348, 227],
    'img/game-screen21.JPG' : [9, 32, 348, 227],
    'img/myclub-enter20.JPG': [9, 32, 348, 227],
    'img/myclub-enter21.JPG': [9, 32, 348, 227],
    'img/sure-start.JPG' : [46, 249, 439, 313],
    'img/proceed.JPG' : [9, 676, 552, 75],
    'img/club-house.JPG' : [296, 653, 260, 98],
    'img/sim-game20.JPG' : [85, 102, 450, 574],
    'img/sim-game21.JPG' : [85, 102, 450, 574],
    'img/kickoff.JPG' : [496, 595, 311, 127],
    'img/skip-graphic.JPG' : [971, 68, 295, 128],
    'img/highlights.JPG' : [11, 34, 530, 287],
    'img/next-finish.JPG' : [487, 532, 330, 175],
    'img/additional-content.JPG' : [895, 298, 282, 84],
    'img/contract-manager-upd.JPG' : [420, 72, 503, 122],
    'img/game-proceed.JPG' : [11, 657, 316, 96],
    'img/ok.JPG' : [164, 377, 999, 299],
    'img/coins.JPG' : [1085, 59, 50, 42],
    'sign/scout.JPG' : [348, 241, 531, 397],
    'sign/sign-enter.JPG': [86, 33, 649, 426],
    'sign/choose-slot.JPG': [44, 150, 532, 322],
    'sign/confirm.JPG': [9, 620, 638, 134],
    'sign/chosed-trainer.JPG': [26, 151, 492, 290],
    'sign/sure.JPG': [145, 142, 994, 463],
    'sign/skip.JPG': [11, 602, 510, 151],
    'sign/confirm-player.JPG': [627, 115, 204, 127],
    'sign/next.JPG': [12, 302, 861, 297],
    'sign/added.JPG': [412, 219, 459, 184],
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
#     json_dump(position, to_write)

# -------------------------------------------- PES SETTINGS FILE HANDLING

def makebkp():
    if isthere(settings_file) and isthere(settings_backup):
        logger.info("There is settings and settings backup files. We can start playing")
        return True
    if isthere(settings_file) and not isthere(settings_backup):
        logger.info("Creating backup and importing pes settings file")
        os.rename(settings_file, settings_backup)
        logger.info('Backup created: %s', os.listdir(settings_path))
        copy(settings_pesbot, settings_file)
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
    simulate_button(Key.MINUS, 0.6)
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

    # For specified images limit the area where "to look for"
    if img in areas.keys():
        area_holder = areas[img].copy()
        area_holder[0] += pes_region.getX()
        area_holder[1] += pes_region.getY()
        area_coord = Region(*area_holder)
    else:
        area_coord = pes_region


    # pes_region.highlight(1)
    # logger.debug('PES height: %s, width: %s, position(x,y): %s, %s', pes_region.getH(), pes_region.getW(), pes_region.getX(), pes_region.getY())

    if area_coord.exists(Pattern(img).similar(similarity), seconds):
        time.sleep(0.7)
        #pes_region.exists(Pattern(img).similar(similarity), seconds).highlight(1)
        logger.debug('%s match found', img)
        return True
    else:
        logger.warning('%s not found', img)
        global error_count
        error_count +=1
        if error_count >= error_threshold:
            pes_region.saveScreenCapture('./shot', 'screen_to_mail')
            logger.error(f'{error_count} errors occurred, this is more than {error_threshold}. Failing script.')
            sys.exit()
        return False

# press_A when matched photo (a) within timeout (b)
def proceed(a, b):
    isok(a, b)
    press_A()
    return


def base_ok(a=5):
    global error_count
    if isok('img/club-house.JPG', a):
        logger.info('On "Club House" menu')
        error_count = 0
        return True
    else:
        logger.error('Not on "Club House", can\' proceed')
        error_count +=13
        return False

########################################################### CONSTRUCTION AREA
# Find coordinates of img pattern and write it down
def locate(im_path):
    dupa = pes_region.exists(Pattern(im_path).similar(0.8), 5)
    #adjust = set_pes_frame()
    print(f'Coordinates: {dupa.getX()-pes_frame[0]}, {dupa.getY()-pes_frame[1]}, {dupa.getW()}, {dupa.getH()}')
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
    obj_coordinates[0] += pes_xy[0]
    obj_coordinates[1] += pes_xy[1]
    logger.info('Object x=%s, y=%s, w=%s, h=%s', *obj_coordinates)
    return obj_coordinates


# Takes object name, checks it's relevant coordinates and recognizes value

    #use custom tesseract bin:
pytesseract.tesseract_cmd = f'{os.path.realpath("./tesseract_bin/tesseract.exe")}'

def recognize(object_name, conf_options='outputbase digits'):
    try:
        if conf_options != 'outputbase digits':
            conf_options = conf_options
        elif spots[object_name][1] != '@':
            conf_options = spots[object_name][1]
        pict = Region(*coordset(pes_frame, object_name))
        pict_size = (pict.getW()*3,pict.getH()*3)
        image_value = pytesseract_image_to_string(cv2_resize(pict.getBitmap(),pict_size), lang='equ+eng', config=conf_options)
        time.sleep(1)
        # pict.highlight(1)
        return image_value
    except:
        logger.error(f'Could not recognize image: {exc_info()}')
        global pes_region
        pes_region = pes.window()
        pes_region.saveScreenCapture('./shot', 'screen_to_mail')
        return -1




###########################################################

#       ------------------------------------ PROCEDURES --------------------------------------

# Start game and go to "Club house" which is base point of the game
def start_game():
    global error_count
    logger.info('Starting interaction with %s', pes.getName())
    pes.focus()
    if isok(f'img/press-button{pes_config["general"]["pes_version"]}.jpg', 180):
        press_A()
        time.sleep(20)
    while True:
        error_count = 0
        if isok('img/this-week-pick-up.JPG', 2):
            press_B()
        elif isok('img/ok.JPG',2, 0.85):
            press_A()
        elif isok(f'img/game-screen{pes_config["general"]["pes_version"]}.JPG', 2, 0.7):
            turn_down(1)
            if isok(f'img/myclub-enter{pes_config["general"]["pes_version"]}.JPG', 1, 0.7):
                press_A()
                if isok('img/sure-start.JPG', 15):
                    press_A()
                    break
    # Proceed to home
    while True:
        error_count = 0
        if isok('img/proceed.JPG', 2) or isok('img/ok.JPG', 3, 0.85) or isok('img/close.JPG', 2):
            press_A()
        elif base_ok(2):
            logger.info("Game started successfully, logged in to game, can proceed with scripts")
            break

# Change team and get back to base
def team_change(squad):
    if base_ok(60):
        press_X()
        if isok('img/squad-list.JPG', 60):
            if isok('img/additional-content.JPG',3):
                turn_down(squad + 1)
            else:
                turn_down(squad)
            time.sleep(1)
            press_A()
        global team_nr
        team_nr = squad
        logger.info('Team number changed to: %s', team_nr)


# Play one game and get back to base
def play_one(mode=''):
    global contract_m, contract_1, contract_2

    def contract_renew(team=False):
        '''team=False for manager contract, team=True for team contracts'''
        global contract_m
        for _ in range(1):
            if not team:
                if isok('img/contract-manager-upd.JPG', 10):
                    press_A()
                    if contract_m != 0:
                        break

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

            if isok('img/contracts-renewed.JPG', 2):
                press_A()

            if not team and contract_m == 0 :
                if isok('img/contract-manager-upd.JPG', 10):
                    press_A()
                    contract_m = 25


    if base_ok(30):
        turn_left(3)
        # On sim game
        if isok(f'img/sim-game{pes_config["general"]["pes_version"]}.JPG', 30):
            press_A()
        # Sim match start
        if isok('img/kickoff.JPG', 30):
            press_A()
        # Match started - switch to stat look
        if isok('img/skip-graphic.JPG', 120):
            press_Y()
            #if isok('img/skip-graphic.JPG', 10):
            #   press_Y()
        time.sleep(200)
        if isok('img/next-finish.JPG', 320):
            press_A()

        # Skip highlights 6' 6"
        time.sleep(200)
        if isok('img/highlights.JPG', 620):
            press_menu()
            #if isok('img/fulltime.JPG',10):
            #    press_A()
            #else:
            #    press_menu()

        # Proceed to contracts:
        if isok('img/next-finish.JPG', 230):
            press_A()
        while True:
            time.sleep(1)
            if isok('img/game-proceed.JPG', 2) and not isok('img/contract-manager-upd.JPG', 1):
                press_A()
            elif isok('img/contract-manager-upd.JPG', 1):
                break

        #Update runtime contract duration variables
        contract_m -= 1
        if team_nr == 1:
            contract_1 -= 1
        elif team_nr == 2:
            contract_2 -= 1

        # Contract manager upd
        if isok('img/contract-manager-upd.JPG', 160):
            contract_renew()

        if isok('img/contract-confirm1.JPG', 5):
            if pes_gui and (mode == 'limited'):
                contract_renew(True)
                # Update team contract duration
                if team_nr == 1:
                    contract_1 += 10
                elif team_nr == 2:
                    contract_2 += 10

            elif mode == 'standard':
                if (team_nr == 1 and contract_1 == 0) or (team_nr == 2 and contract_2 == 0):
                    press_A()
                else:
                    contract_renew(True)

        # Confirm got back to club house
        if base_ok(30):
            global game_number
            game_number += 1
            logger.info('1 more game')




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
                        turn_up(1)
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

# Convert player into EXP trainer
def exec_victim(turns_down=2):
        logger.info('Executing victim')
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


# Converts and populates squads of playing teams:
def smart_players_convert(which_teams=12, populate=True, execute=True):
    '''This function performs converting to EXP trainers and assigning new
    players to selected teams (1, 2, 12)'''
    for team in range(2):
        if not isthere(f'team{team +1}.json'):
            copy('template-team.json', f'team{team +1}.json')

    def team_execute():
        if base_ok(9):
            logger.info('On base, entering team for execution')
            press_A()
        with open('team1.json', 'r') as to_read:
            position = json_load(to_read)
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

        with open("team1.json", "w") as to_write:
            json_dump(position, to_write)
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
            position1 = json_load(to_read)
        with open(team_file2, 'r') as to_read2:
            position2 = json_load(to_read2)

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
                error_count = 0
                while not isok(value[3],1):
                    turn_left(1)
            turn_down(2)
            if isok(f'conv/{max_player_cost}.JPG',2,0.95):
                logger.info('Value filter applied')
            else:
                while not isok(f'conv/{max_player_cost}.JPG',1.5,0.98):
                    turn_left(1)
            turn_down(4)
            press_A()
            time.sleep(0.5)
            if isok('conv/filtered.JPG', 2):
                logger.debug('Filters applied')
                if error_count < 15:
                    error_count = 1
            keyDown(Key.DOWN)
            time.sleep(2)
            keyUp(Key.DOWN)
            # Prepare list of already used players
            team1_names = [value[2] for (key, value) in position1.items()]
            team2_names = [value[2] for (key, value) in position2.items()]
            known_names = team1_names + team2_names
            while not isok('conv/on_team.JPG',3):
                error_count -= 1
                time.sleep(0.5)
                found = False
                for i in range(6):
                    try:
                        surname = ''.join(char for char in recognize('surname') if ord(char) < 128 and not char.isdigit() and not char == ' ')
                    except 'Tcl_AsyncDelete':
                        logger.warning('Tcl_AsyncDelete occured, trying again')
                        time.sleep(2)
                        surname = ''.join(char for char in recognize('surname') if ord(char) < 128 and not char.isdigit() and not char == ' ')

                    print(surname)
                    if surname != '' and surname not in known_names:
                        value[2] = surname
                        logger.info('New player found: %s', surname)
                        found = True
                        with open(team_file1, "w") as to_write:
                            json_dump(position1, to_write)
                    if not found:
                        logger.info('Not %s, turning right', key)
                        turn_right(1)
                    if found == True:
                        logger.info('Found new player for position %s, job done.', key)
                        found = False
                        while not isok('conv/on_team.JPG',3):
                            press_A()
                        break
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
    pes_launcher = App(f'{pes_path}')
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

#####################   NEW SCRIPTS GUI RELATED =======================
# temporary variables:


def convert_all_perform():
    global error_count
    if base_ok(3):
        logger.info(f'Starting conversion of all players of max cost {max_player_cost}')
        press_A()
        if isok('conv/on_team.JPG',5):
            logger.info('Entered team, proceeding to reserves')
            time.sleep(0.5)
            to_reserves()
            while True:
                if isok('conv/no_players_left.JPG', 0.5):
                    press_A()
                    while not base_ok(2):
                        error_count -= 10
                        press_B()
                    break
                press_A()
                # Use filter
                time.sleep(0.5)
                if isok('conv/reserves-list.JPG',1):
                    press_rs()
                    time.sleep(0.5)
                    turn_down(2)
                    if isok(f'conv/{max_player_cost}.JPG',1,0.95):
                        logger.info('Value filter applied')
                    else:
                        while not isok(f'conv/{max_player_cost}.JPG',1,0.98):
                            error_count -= 1
                            turn_left(1)
                    turn_down(4)
                    press_A()
                    time.sleep(0.5)
                    if isok('conv/filtered.JPG', 2):
                        logger.debug('Filter applied')
                        keyDown(Key.DOWN)
                        time.sleep(2)
                        keyUp(Key.DOWN)
                        exec_victim()
                        global converted_nr
                        converted_nr += 1
            logger.info(f'Converting all players of cost {max_player_cost} and below has finished.')







# -------------------------------------------- RUN SCRIPT (WITH ARGUMENTS)
if args.run:
    smart_playing_loop()
if args.restore:
    revertbackup()
if args.prepare:
    makebkp()

# Custom goes here:
if args.custom:
    initialize_pes()
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
    #
    #
    #pes_region.saveScreenCapture('./shot', 'screen_to_mail')
    #r'"D:\\Steam\\steamapps\\common\\eFootball PES 2020\\PES2020.exe"'



def dummy_playing_loop(number):
    for i in range(int(number)):
        time.sleep(2)
        logger.info(f'Numbers of dummy games played: {i+1}')
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