from lackey import *
from keyboard import mouse


# Define game variables

pes = App(r"D:\Steam\steamapps\common\PRO EVOLUTION SOCCER 2019\PES2019.exe")
pesName = 'PRO EVOLUTION SOCCER 2019'

# Define navigation (works together with settings file for PES controller)

def press_A():
    App.focus(pesName)
    time.sleep(0.8)
    keyDown(Key.ENTER)
    time.sleep(0.1)
    keyUp(Key.ENTER)
    return
def press_B():
    App.focus(pesName)
    time.sleep(0.8)
    keyDown(Key.ESC)
    time.sleep(0.1)
    keyUp(Key.ESC)
    return
def press_X():
    App.focus(pesName)
    time.sleep(0.8)
    keyDown(Key.BACKSPACE)
    time.sleep(0.1)
    keyUp(Key.BACKSPACE)
    return
def press_Y():
    App.focus(pesName)
    time.sleep(0.8)
    keyDown(Key.CTRL)
    time.sleep(0.1)
    keyUp(Key.CTRL)
    return
def press_menu():
    App.focus(pesName)
    time.sleep(0.8)
    keyDown(Key.DIVIDE)
    time.sleep(0.1)
    keyUp(Key.DIVIDE)
    return

def turn_right(n):
    App.focus(pesName)
    count=0
    while n > count:
        count+=1
        keyDown(Key.RIGHT)
        time.sleep(0.1)
        keyUp(Key.RIGHT)
        time.sleep(1)
    del count
    return
def turn_left(n):
    App.focus(pesName)
    count=0
    while n > count:
        count+=1
        keyDown(Key.LEFT)
        time.sleep(0.1)
        keyUp(Key.LEFT)
        time.sleep(1)
    del count
    return
def turn_up(n):
    App.focus(pesName)
    count=0
    while n > count:
        count+=1
        keyDown(Key.UP)
        time.sleep(0.1)
        keyUp(Key.UP)
        time.sleep(1)
    del count
    return
def turn_down(n):
    App.focus(pesName)
    count=0
    while n > count:
        count+=1
        keyDown(Key.DOWN)
        time.sleep(0.1)
        keyUp(Key.DOWN)
        time.sleep(1)
    del count
    return

# Set check photo (a) and set timeout for check (b). It will focus on window.
def isok(a, b):
    if exists(Pattern(a).similar(0.85), b):
        App.focus(pesName)
        time.sleep(0.7)
        return True
    else:
        return False
# press_A when matched photo (a) within timeout (b)
def proceed(a, b):
    isok(a, b)
    press_A()
    return

# Start game and go to "Club house" which is base point of the game
def start_game():
  # print('Game is starting')
  # doubleClick('start-pes.jpg')
  if isok('press-button.jpg', 180):
      press_A()
  if isok('online-confirm.jpg', 25):
      press_A()
  if isok('myclub-enter.JPG', 60):
      press_A()
  if isok('proceed-btn.JPG', 25):
      press_A()
  if isok('ack.JPG', 25):
      press_A()
  if isok('proceed-small.JPG', 120):
      press_A()

  # if auction then hope:
  if isok('auction-report.jpg', 25):
      press_A()
  if isok('big-ok.JPG', 20):
      press_A()

  if isok('club-house.JPG', 20):
       print("At home")
  return

# Change team and get back to base
def team_change(squad):
    if isok('club-house.JPG', 60):
        press_X()
    if isok('squad-list.JPG', 60):
        turn_down(squad)
        time.sleep(1)
        press_A()
    return

    #keyDown(Key.ESC)
    #keyboard.write('Hehehe')

# Play one game and get back to base
def play_one():
    if isok('club-house.JPG', 30):
        turn_left(3)
    #
    if isok('sim-game.JPG', 30):
        press_A()
    # Sim match start
    if isok('kickoff.JPG', 30):
        press_A()
    # Match started - switch to stat look
    if isok('match-started.JPG', 160):
        press_A()
    if isok('skip-graphic.JPG', 120):
        press_Y()
    # Halftime - click ok to start new match
    if isok('halftime.JPG', 650):
        press_A()
    if isok('second-half.JPG', 120):
        press_A()
    # Skip highlights
    if isok('highlights.JPG', 820):
        press_menu()

    # Experience
    if isok('next-finish.JPG', 30):
        press_A()

    # Experience points
    if isok('experience.JPG', 30):
        press_A()
        time.sleep(0.8)
        press_A()

    # Level up
    if isok('levelup.JPG', 20):
        press_A()

    # Changes rating
    if isok('rating.JPG', 20):
        press_A()

    # Rewards
    if isok('reward.JPG', 20):
        press_A()

    if isok('reward2.JPG', 20):
        press_A()

    # Contract manager upd
    if isok('contract-manager-upd.JPG', 160):
        press_A()

    if isok('contract-confirm1.JPG', 10):
        turn_right(1)
        press_A()

    # If contract expires players only (for now)

    if isok('pay-gp.JPG', 10):
        press_A()

    if isok('sure-pay.JPG', 10):
        turn_right(1)
        press_A()

    if isok('contracts-renewed.JPG', 10):
        press_A()

    # Confirm got back to club house
    if isok('club-house.JPG', 30):
        print('1 more game')

    return

# Play one game after another changing squads in between
def playing_loop():
    game_number = 0
    while True:
        play_one()
        game_number+=1
        print('Number of games played: ' + str(game_number))
        team_change(1)
        play_one()
        game_number+=1
        print('Number of games played: ' + str(game_number))
        team_change(2)

    #return

# Sign players using all available trainers one by one
def sign_all():
    if isok('club-house.JPG', 10):
        print('sign_all script started')
    turn_right(4)
    if isok('sign/scout.JPG', 3):
        press_A()
    if isok('sign/sign-enter.JPG', 4):
        press_A()
    while True:
      if isok('sign/choose-slot.JPG', 9):
        press_A()
      if isok('sign/no-scouts.JPG', 3):
          # If no scouts - break
        print('No scouts left, all signed')
        press_A()
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
    if isok('sign/choose-slot.JPG', 5):
        press_B()
    if isok('sign/sign-enter.JPG', 5):
        press_B()
    if isok('sign/scout.JPG', 5):
        turn_left(4)
    if isok('club-house.JPG', 10):
        print('sign_all script finished')
    return



#TESTS
def test1():
    App.focus(pesName)
    time.sleep(1)
    keyDown(Key.ESC)
    time.sleep(0.1)
    keyUp(Key.ESC)
    return
#test1()

def test2():
    print('Import works')
