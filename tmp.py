from PyQt5 import uic

with open('c.py', 'w+') as f:
    uic.compileUi('mainScreen.ui', f)