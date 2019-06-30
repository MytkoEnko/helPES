from lackey import *
from main import test2

pes = App(r"D:\Steam\steamapps\common\PRO EVOLUTION SOCCER 2019\PES2019.exe")
pesName = 'PRO EVOLUTION SOCCER 2019'
def isok(a, b):
    if exists(Pattern(a).similar(0.85), b):
        App.focus(pesName)
        time.sleep(0.7)
        return True
    else:
        return False

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

def sign_all():
    while True:
      if isok('sign/choose-slot.JPG', 9):
        tysny()
      if isok('sign/no-scouts.JPG', 3):
          # If no scouts - breake
        print('No scouts left, all signed')
        tysny()
        break
      if isok('sign/confirm.JPG', 9):
        tysny()
      if isok('sign/chosed-trainer.JPG', 9):
        turn_down(3)
        tysny()
      if isok('sign/sure.JPG', 9):
        turn_right(1)
        tysny()
      #Skip jugle
      if isok('sign/skip.JPG', 10):
        time.sleep(1.5)
        keyDown(Key.DIVIDE)
        time.sleep(0.1)
        keyUp(Key.DIVIDE)

      if isok('sign/confirm-player.JPG', 9):
        time.sleep(1.5)
        tysny()
      if isok('sign/next.JPG', 9):
        tysny()
      if isok('sign/added.JPG', 9):
        tysny()





