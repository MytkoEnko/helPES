from main import *
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
initialize_pes()
pes.focus()
# print(pes.getPID(), pes.getName(), pes.hasWindow(), pes_region.getX(), pes_region.getY(), pes_region.getH(),pes_region.getW())

pes_region.saveScreenCapture('./shot','test2')

# Preparation for image reader

# Tesseract for output base digits
# tesseract money100.PNG stdout outputbase digits
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