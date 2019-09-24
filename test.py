from main import *
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
    1 : "./shot/money.JPG",
    2 : "./shot/money1.JPG",
    3 : "./shot/money3.JPG",
    4 : "./shot/money5.JPG",
    5 : "./shot/money33.PNG",
    6 : "./shot/money100.PNG",
}

# for i in mydict:
#     print(i, pytesseract.image_to_string(mydict[i],config='outputbase digits'))
#image_to_data(image, lang=None, config='', nice=0, output_type=Output.STRING, timeout=0)
# print(pytesseract.image_to_string(mydict[6], config='outputbase digits'))
# print(int(pytesseract.image_to_string(mydict[6], config='outputbase digits')))
with open('position.json', 'r') as f:
    dupa = json.load(f)

for a,b in dupa.items():
    b[2] = 'Dupa'

with open('position.json','w') as f:
    json.dump(dupa, f)

