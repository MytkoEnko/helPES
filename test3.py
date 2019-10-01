import pytesseract

for i in range(1000):
    print(pytesseract.image_to_string('shot/money2.JPG', lang='equ+eng'), i)
