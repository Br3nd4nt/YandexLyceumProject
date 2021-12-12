from mainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys
import os


if __name__ == '__main__':
    with open('requirements.txt') as f:
        for i in f.readlines():
            i.rstrip('\n')
            os.system(f'pip install {i}')
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
    