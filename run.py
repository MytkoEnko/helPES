#from lackey import *
from main import *

if not pes.window():
    App.open("D:\\Steam\\steamapps\\common\\PRO EVOLUTION SOCCER 2019\\PES2019.exe")
    wait(30)
pes.focus()
with Region(pes.window()):


    # Elements you can run separately or creating loops

    #start_game()
    playing_loop()
    #proceed('club-house.JPG', 20)
    #play_one()
    #team_change(1)
    #sign_all()
pes.close()