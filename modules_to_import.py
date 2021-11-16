from mainWindow import MainWindow
from PyQt5.QtWidgets import QApplication
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtCore import QSize, QThread, QTime
from PyQt5.QtGui import QBrush, QColor
from database import Database
from eventWindow import EventWindow
from event import Event
import datetime
from pastTimeThread import TimeChecker
import sqlite3
import os
from event import Event
from datetime import datetime, time, date
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sqlite3
from database import Database
from notification import Notification
from PyQt5 import uic
from PyQt5.QtCore import QTime, QDate
from PyQt5.QtWidgets import QMainWindow
from database import Database
from event import Event
from PyQt5.QtCore import QTime, QDate
import os
import platform