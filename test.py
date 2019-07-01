from main import *

# Remove all players others than squad
def players_convert(team):

    # internal var
    team_is = 0
    if base_ok():
         print('Starting players to EXP trainers convertion')
         print('Switch to team ' + str(team))
         # Change to desired team
         team_change(team)
    if base_ok():
         press_A()
    # Define if on reserves
    def on_reserves():
        # Define white or bronze team 0=no, 1=white, 2=bronze
        if isok('conv/reserves.JPG', 8):
            return True
        else:
            return False
    def which_color():
        if on_reserves():
            turn_up(1)
            turn_right(1)
        if isok('conv/white-ball.JPG', 5):
            team_is = 1
            print('Team of whites ' + str(team_is))
        if isok('conv/bronze-ball.JPG', 5):
            team_is = 2
            print('Team of bronze' + str(team_is))
    # Open reserves
    def open_reserves():
        while not on_reserves():
            turn_down(1)
            turn_left(1)
        press_A()

    # Ensure on reserves
    def find_victim():
        if isok('conv/reserves-list.JPG', 5):
            #create variable
            if team_is == 1:
                ball_path='conv/white-ball.JPG'
            if team_is == 2:
                ball_path='conv/bronze-ball.JPG'
            # Jump down
            App.focus(pesName)
            keyDown(Key.DOWN)
            time.sleep(5)
            keyUp(Key.DOWN)
            while not isok('conv/black-ball.JPG', 2):
                for i in range(6):
                    if isok(ball_path,5):
                        print('Found ' + str(team_is))
                        return
                    else:
                        turn_right(1)
                turn_up(1)
    def exec_victim():
        print('kill all')
    on_reserves()
    which_color()
    open_reserves()
    find_victim()
    exec_victim()

players_convert(2)