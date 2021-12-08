from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QListWidgetItem
from PyQt5.QtCore import QSize, QThread, QTime
from PyQt5.QtGui import QBrush, QColor
from database import Database
from eventWindow import EventWindow
from event import Event
import datetime
from pastTimeThread import TimeChecker

import c

class MainWindow(QMainWindow, c.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi('layouts/mainScreen.ui', self)
        self.setupUi(self)
        self.db = Database()


        #BLACK MAGIC
        self.thread = QThread()
        self.timeChecker = TimeChecker()
        self.timeChecker.moveToThread(self.thread)
        self.timeChecker.listUpdateSignal.connect(self.updateList)
        self.thread.started.connect(self.timeChecker.run)
        self.thread.start()


        self.CreateEvent.clicked.connect(self.createEvent)
        self.listAllEvents()
        self.EditWindow = EventWindow()
        self.EventList.itemDoubleClicked.connect(self.listItemSelected)
        self.EventList.itemClicked.connect(self.listItemClicked)
        self.chosen = None
        CurrentTime = datetime.datetime.now()
        time = QTime(CurrentTime.hour, CurrentTime.minute)
        self.StartTime.setTime(time)
        time = time.addSecs(300)
        self.EndTime.setTime(time)


    def listItemClicked(self, item):
        self.chosen = self.EventList.row(item)
        
    def show(self, flag=False):
        super().show()
        if flag:
            self.updateList()

    def listAllEvents(self):
        res = self.db.getAllEvents()
        for i in res:
            DBEvent = Event(*i)
            event = QListWidgetItem()
            event.setText(DBEvent.getLabel())
            event.setData(1, i[1])
            if i[-2]:
                event.setForeground(QBrush(QColor(int('0xA0A0A0', 0))))
            event.setData(20, i[0])
            size = QSize(0, 30)
            event.setSizeHint(size)
            self.EventList.addItem(event)

    def listItemSelected(self, item: QListWidgetItem):
        self.EditWindow.show(item.data(20), self)

    def updateList(self):
        self.EventList.clear()
        self.listAllEvents()
        if self.chosen is not None:
            self.EventList.setCurrentRow(self.chosen)

    def createEvent(self):
        name = self.EventName.displayText()
        date = self.Date.selectedDate()
        startTime = self.StartTime.time()
        endTime = self.EndTime.time()
        info = self.EventInfo.toPlainText()
        NewEvent = Event(0, name, date.year(), date.month(), date.day(), startTime.hour(), startTime.minute(), endTime.hour(), endTime.minute(), info, False, False)
        self.db.createEvent(NewEvent)
        self.updateList()
        