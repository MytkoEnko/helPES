from main import *
import threading
import json
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

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

# initialize_pes()
# pes.focus()
# pes_region = pes.window()
# print(pes_region.getH(),pes_region.getW())

# original = cv2.imread("./shot/screen1.png.png")
# duplicate = cv2.imread("./shot/test1.png")
# if original.shape == duplicate.shape:
#     print('Game seems to be working fine, continuing')
# else:
#     print('False')
# initialize_pes()
# pes.focus()
# print(pes.getPID(), pes.getName(), pes.hasWindow(), pes_region.getX(), pes_region.getY(), pes_region.getH(),pes_region.getW())

#pes_region.saveScreenCapture('./shot','test2')

# Preparation for image reader
zdymki = [
    'img/club-house.JPG',
    'img/online-confirm.jpg',
    'img/this-week-pick-up.JPG',
    'img/game-screen.JPG',
    'img/myclub-enter.JPG',
    'img/sure-start.JPG',
    'img/live-update.JPG',
    'img/featured-players.JPG',
    'img/proceed-btn.JPG',
    'img/no-new-updates.JPG',
    'img/proceed-small.JPG',
    'img/big-ok.JPG',
    'img/squad-list.JPG',
    'img/sim-game.JPG',
    'img/kickoff.JPG',
    'img/match-started.JPG',
    'img/skip-graphic.JPG',
    'img/halftime.JPG',
    'img/second-half.JPG',
    'img/highlights.JPG',
    'img/next-finish.JPG',
    'img/experience.JPG',
    'img/experience.JPG',
    'img/levelup.JPG',
    'img/rating.JPG',
    'img/reward.JPG',
    'img/reward2.JPG',
    'img/contract-manager-upd.JPG',
    'img/contract-confirm1.JPG',
    'img/pay-gp.JPG',
    'img/sure-pay.JPG',
    'img/contracts-renewed.JPG',
    'sign/scout.JPG',
    'sign/sign-enter.JPG',
    'sign/choose-slot.JPG',
    'sign/no-scouts.JPG',
    'sign/five-star.JPG',
    'sign/five-star.JPG',
    'sign/confirm.JPG',
    'sign/chosed-trainer.JPG',
    'sign/sure.JPG',
    'sign/skip.JPG',
    'sign/confirm-player.JPG',
    'sign/next.JPG',
    'sign/added.JPG',
    'sign/choose-slot.JPG',
    'sign/sign-enter.JPG',
    'sign/scout.JPG',
    'img/club-house.JPG',
    'sign/scout.JPG',
    'sign/sign-enter.JPG',
    'sign/sell-enter.JPG',
    'sign/no-scouts-left.JPG',
    'sign/unchecked.JPG',
    'sign/last-checked.JPG',
    'sign/confirm-sell.JPG',
    'sign/reward-received.JPG',
    'sign/no-scouts-left.JPG',
    'sign/scout.JPG',
    'conv/reserves.JPG',
    'conv/white-ball.JPG',
    'conv/bronze-ball.JPG',
    'conv/reserves-list.JPG',
    'conv/white-ball.JPG',
    'conv/bronze-ball.JPG',
    'conv/black-ball.JPG',
    'conv/gold-ball.JPG',
    'conv/black-ball.JPG',
    'conv/player-menu.JPG',
    'conv/convert.JPG',
    'conv/no.JPG',
    'conv/converted.JPG',
    'sign/sign-enter.JPG',
]
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
mydict = {
    'shot/money.JPG' : [],

}

# for i in mydict:
#     print(i, pytesseract.image_to_string(mydict[i],config='outputbase digits'))
#image_to_data(image, lang=None, config='', nice=0, output_type=Output.STRING, timeout=0)
# print(pytesseract.image_to_string(mydict[6], config='outputbase digits'))
# print(int(pytesseract.image_to_string(mydict[6], config='outputbase digits')))

# TODO UNCOMENT BELOW
# with open('position.json', 'r') as f:
#     dupa = json.load(f)
#
# for a,b in dupa.items():
#     b[2] = 'Dupa'
#
# with open('position.json','w') as f:
#     json.dump(dupa, f)

def print_hello():
    for i in range(4):
        time.sleep(2.5)
        print("Hello")


def print_hi():
    for i in range(4):
        time.sleep(7.5)
        print("Hi")


t1 = threading.Thread(target=print_hello)
t2 = threading.Thread(target=print_hi)
t1.start()
t2.start()
time.sleep(2)
print('Script done')

