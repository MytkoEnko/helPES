from lackey import *
from keyboard import mouse

# Start game
def start_game():
  # print('Game is starting')
  doubleClick('img/start-pes.jpg')
  if isok('press-button.jpg', 180):
      tysny()
  if isok('online-confirm.jpg', 25):
      tysny()
  if isok('myclub-enter.JPG', 60):
      tysny()
  if isok('proceed-btn.JPG', 25):
      tysny()
  if isok('ack.JPG', 25):
      tysny()
  if isok('proceed-small.JPG', 120):
      tysny()

  # if auction then hope:
  if isok('auction-report.jpg', 25):
      tysny()
  if isok('big-ok.JPG', 20):
      tysny()

  if isok('club-house.JPG', 20):
       print("At home")
  return

pes = App(r"D:\Steam\steamapps\common\PRO EVOLUTION SOCCER 2019\PES2019.exe")
pesName = 'PRO EVOLUTION SOCCER 2019'
# Click automation
# Send photo and delay it will focus on window and wait
def isok(a, b):
    if exists(Pattern('./img/' + a).similar(0.85), b):
        App.focus(pesName)
        time.sleep(0.7)
        return True
    else:
        return False

def proceed(a, b):
    if exists(Pattern('./img/' + a).similar(0.85), b):
       App.focus(pesName)
       tysny()
    return

def tysny():
    time.sleep(0.8)
    keyDown(Key.ENTER)
    time.sleep(0.1)
    keyUp(Key.ENTER)
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

# change team
def team_change(squad):
    if exists(Pattern('./img/club-house.JPG').similar(0.85), 60):
        App.focus(pesName)
        keyDown(Key.BACKSPACE)
        print('DOWN')
        time.sleep(0.1)
        keyUp(Key.BACKSPACE)
    if exists(Pattern('./img/squad-list.JPG').similar(0.85), 60):
        turn_down(squad)
        time.sleep(1)
        keyDown(Key.ENTER)
        time.sleep(0.1)
        keyUp(Key.ENTER)
    return

    #keyDown(Key.ESC)
    #keyboard.write('Hehehe')

def play_one():
    if isok('club-house.JPG', 30):
        turn_left(3)
    #
    if isok('sim-game.JPG', 30):
        tysny()
    # Sim match start
    if isok('kickoff.JPG', 30):
        tysny()
    # Match started - switch to stat look
    if isok('match-started.JPG', 160):
        tysny()
    if isok('skip-graphic.JPG', 120):
        keyDown(Key.CTRL)
        time.sleep(0.1)
        keyUp(Key.CTRL)
    # Halftime - click ok to start new match
    if isok('halftime.JPG', 650):
        tysny()
    if isok('second-half.JPG', 120):
        tysny()
    # Skip highlights
    if isok('highlights.JPG', 820):
        App.focus(pesName)
        time.sleep(1)
        keyDown(Key.DIVIDE)
        time.sleep(0.1)
        keyUp(Key.DIVIDE)

    # Experience
    if isok('next-finish.JPG', 30):
        tysny()

    # Experience points
    if isok('experience.JPG', 30):
        tysny()
        time.sleep(1)
        tysny()

    # Level up
    if isok('levelup.JPG', 20):
        tysny()

    # Changes rating
    if isok('rating.JPG', 20):
        tysny()

    # Rewards
    if isok('reward.JPG', 20):
        tysny()

    if isok('reward2.JPG', 20):
        tysny()

    # Contract manager upd
    if isok('contract-manager-upd.JPG', 160):
        tysny()

    if isok('contract-confirm1.JPG', 10):
        turn_right(1)
        tysny()

    # If contract expires players only (for now)

    if isok('pay-gp.JPG', 10):
        tysny()

    if isok('sure-pay.JPG', 10):
        turn_right(1)
        tysny()

    if isok('contracts-renewed.JPG', 10):
        tysny()

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

    return

#start_game()
playing_loop()
#proceed('club-house.JPG', 20)
#play_one()
#team_change(1)

def test1():
    App.focus(pesName)
    time.sleep(1)
    keyDown(Key.DIVIDE)
    time.sleep(0.1)
    keyUp(Key.DIVIDE)
    return
#test1()