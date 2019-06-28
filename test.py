from lackey import *

# Start game
# def start_game():
#   print('Game is starting')
#   doubleClick('start-pes.jpg')
#   wait('press-button.jpg',seconds=360)
#   doubleClick('press-button.jpg')
#   keyDown(Key.ENTER)

pnotes = App(r"C:\Windows\System32\osk.exe")
notName = 'On-Screen Keyboard'
#Click automation
def proceed(a):
    wait(a, seconds=60)
    App.focus(notName)
    keyDown(Key.ENTER)

# change team
def team_change():
    wait('test2.jpg', seconds=60)
    App.focus(notName)
    #type('A')
    keyDown(Key.LEFT)
    return

#start_game()
# proceed('online-confirm.jpg')
# proceed('proceed-btn.JPG')
# proceed('big-ok.jpg')
# proceed('ack.JPG')
# proceed('auction-report.jpg')


team_change()

