from main import *


#makebkp()
#revertbackup()
# start_game()
# players_convert(2)
# while True:
#     if isok('sign/five-star.JPG', 3, 0.96):
#         print('Five star player')
#         turn_down(1)
#     else:
#         print('Not fivestar')
#         turn_down(1)

initialize_pes()
pes.focus()
pes_region = pes.window()
print(pes_region.getH(),pes_region.getW())