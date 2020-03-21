# import pytesseract
#
# for i in range(1000):
#     print(pytesseract.image_to_string('shot/money2.JPG', lang='equ+eng'), i)
import argparse
parser = argparse.ArgumentParser(description="PES-farming script. Use to automate sim matches.")
group = parser.add_mutually_exclusive_group()
group.add_argument("-r", "--restore", help="Restores PES original settings file to let you play normally", action="store_true")
group.add_argument("-p", "--prepare", help="Copies prepared PES settings file to let script navigate in game", action="store_true")
group.add_argument("-go", "--run", help="Run the script", action="store_true")
parser.add_argument("--hello", help="Say hello too", action="store_true")
args = parser.parse_args()
parser.

if args.restore :
    print("Hehehe")