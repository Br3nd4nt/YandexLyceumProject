from PyQt5 import uic
from PyQt5.QtCore import QDate, QObject, QSize, QThread, QTime, pyqtSignal
import sqlite3
import os
import datetime
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMainWindow
import platform
import sys


class Notification:
    def __init__(self):
        self.OS = platform.system()

    def notify(self, title, text):
        if self.OS == 'Darwin':
            os.system(f"""
                osascript -e 'display notification "{title}" with title "{text}"'
                """)
        elif self.OS == "win32" or self.OS == "win64":
            try:
                from win10toast import ToastNotifier
                toast = ToastNotifier()
                toast.showToast(title, text, duration=20)
            except Exception as e:
                print(e)


class Event:
    def __init__(self, id: int, name: str, year: int, month: int, day: int, SHour: int, SMinute: int, EHour: int, EMinute: int, info: str, past: bool, current: bool):
        self.id = id
        self.name = name
        self.year = year
        self.month = month
        self.day = day
        self.SHour = SHour
        self.SMinute = SMinute
        self.EHour = EHour
        self.EMinute = EMinute
        self.info = info
        self.past = past
        self.current = current

    def getLabel(self):
        month = '0' * (2 - len(str(self.month))) + str(self.month)
        day = '0' * (2 - len(str(self.day))) + str(self.day)
        sHour = '0' * (2 - len(str(self.SHour))) + str(self.SHour)
        sMinute = '0' * (2 - len(str(self.SMinute))) + str(self.SMinute)
        eHour = '0' * (2 - len(str(self.EHour))) + str(self.EHour)
        eMinute = '0' * (2 - len(str(self.EMinute))) + str(self.EMinute)
        label = f"{self.name} ({self.year}.{month}.{day} {sHour}:{sMinute} - {eHour}:{eMinute})"
        return label
    
    def getStartTime(self):
        return QTime(self.SHour, self.SMinute)

    def getEndTime(self):
        return QTime(self.EHour, self.EMinute)

    def getDate(self):
        return QDate(self.year, self.month, self.day)

    def __str__(self) -> str:
        return f'name: {self.name}\ndate: {self.year}.{self.month}.{self.day}\nstart: {self.SHour}:{self.SMinute}\nend: {self.EHour}:{self.EMinute}\nInfo: {self.info}\nhas pasted: {str(self.past)}\n'


class Database:
    def __init__(self):
        self.name = 'events.sqlite'
        if self.name not in os.listdir():
            self.create()
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

    def create(self):
        open(self.name, 'w+').close()
        creation_text = '''CREATE TABLE Events (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        name TEXT,
        year INTEGER,
        month INTEGER,
        day INTEGER,
        startHour INTEGER,
        startMinute INTEGER,
        endHour INTEGER,
        endMinute INTEGER, 
        info TEXT,
        past BOOL,
        current BOOL);'''
        con = sqlite3.connect(self.name)
        con.cursor().execute(creation_text)
        con.close()

    def close(self):
        self.con.close()

    def createEvent(self, event: Event):
        print(f'creating "{event.name}"')
        self.cur.execute(f"INSERT INTO Events(name,year,month,day,startHour,startMinute,endHour,endMinute,info,past,current) VALUES('{event.name}',{event.year},{event.month},{event.day},{event.SHour},{event.SMinute},{event.EHour},{event.EMinute},'{event.info}',{event.past},{event.current})")
        self.con.commit()

    def getAllEvents(self):
        res = self.cur.execute('SELECT * from Events ORDER BY past ASC, year ASC, month ASC, day ASC, startHour ASC, startMinute ASC').fetchall()
        for i in res:
            i = Event(*i)
        return res

    def getEvent(self, id: int):
        res = self.cur.execute(f'SELECT * FROM Events WHERE id = {id}').fetchall()
        return Event(*res[0])

    def deleteEvent(self, id: int):
        self.cur.execute(f'DELETE FROM Events WHERE id={id}')
        self.con.commit()

    def updateEvent(self, event: Event):
        self.cur.execute(f'''UPDATE Events SET name="{event.name}", 
        year={event.year}, 
        month={event.month}, 
        day={event.day}, 
        startHour={event.SHour}, 
        startMinute={event.SMinute},
        endHour={event.EHour}, 
        endMinute={event.EMinute}, 
        info="{event.info}", 
        past={event.past}
        WHERE id={event.id}''')
        self.con.commit()

    def EventExpired(self, id):
        self.cur.execute(f'UPDATE Events SET past=true WHERE id={id}')

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        # uic.loadUi('layouts/mainScreen.ui', self)
        uic.loadUi('mainScreen.ui', self)
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
        

class TimeChecker(QObject):
    listUpdateSignal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.notif = Notification()

    def updateDB(self, *id):
        for i in id:
            self.cur.execute(f'UPDATE Events SET past=true WHERE id={i}')
            self.con.commit()

    def run(self):
        self.con = sqlite3.connect('events.sqlite')
        self.cur = self.con.cursor()
        self.events = []
        while True:
            self.events.clear()
            for i in self.cur.execute('SELECT id, startHour, startMinute, endHour, endMinute, name, current, year, month, day FROM Events ORDER BY id').fetchall():
                self.events.append((i[0], datetime.time(i[1], i[2], 0), datetime.time(i[3], i[4], 0), i[5], i[6], datetime.date(i[7], i[8], i[9])))
            currentTime = datetime.now().time()
            today = datetime.now().date()
            expired = []
            for i in self.events:
                if today > i[5] or (currentTime >= i[2] and today == i[5]):
                    expired.append(i[0])
                elif currentTime >= i[1] and not i[4] and i[0] not in expired and today == i[5]:
                    print(i)
                    self.notif.notify(i[3], 'Событие началось')
                    self.cur.execute(f'UPDATE Events SET current = True WHERE id={i[0]}')
                    self.con.commit()
                    i = (i[0], i[1], i[2], i[3], True)
                    print(i)
            if len(expired) > 0:
                print(currentTime)
                self.updateDB(*expired)
                self.listUpdateSignal.emit()
                # res = []
                # for i in self.cur.execute('SELECT id, startHour, startMinute, endHour, endMinute, name, current FROM Events ORDER BY id').fetchall():
                #     res.append((i[0], time(i[1], i[2], 0), time(i[3], i[4], 0), i[5], i[6]))
                # self.events = res
            QThread.msleep(1000)


class EventWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi('layouts/eventScreen.ui', self)
        uic.loadUi('eventScreen.ui', self)
        self.db = Database()
        self.deleteButton.setStyleSheet('QPushButton {color: #FF0000}')
        self.deleteButton.clicked.connect(self.delete)
        self.cancelButton.clicked.connect(self.cancel)
        self.saveButton.clicked.connect(self.save)

    def show(self, id: int, MainWindow: QMainWindow):
        self.setWindowFlag(0x00040000)
        super().show()
        self.event = self.db.getEvent(id)
        print(self.event)
        self.mainWindow = MainWindow
        self.setup()
        
    def setup(self):
        self.setWindowTitle(self.event.name + ' - Изменение')
        self.StartTime.setTime(self.event.getStartTime())
        self.EndTime.setTime(self.event.getEndTime())
        self.Calendar.setSelectedDate(self.event.getDate())
        self.NameEdit.setPlainText(self.event.name)
        self.InfoEdit.setPlainText(self.event.info)
        self.pastCheckbox.setChecked(bool(self.event.past))

    def delete(self):
        #add confirmation
        self.db.deleteEvent(self.event.id)
        self.hide()
        self.mainWindow.show(True)

    def cancel(self):
        self.hide()
        self.setup()

    def save(self):
        name = str(self.NameEdit.toPlainText())
        date = self.Calendar.selectedDate()
        startTime = self.StartTime.time()
        endTime = self.EndTime.time()
        info = str(self.InfoEdit.toPlainText())
        past = self.pastCheckbox.isChecked()
        ChangedEvent = Event(self.event.id, name, date.year(), date.month(), date.day(), startTime.hour(), startTime.minute(), endTime.hour(), endTime.minute(), info, past, self.event.current)
        self.db.updateEvent(ChangedEvent)
        self.hide()
        self.mainWindow.show(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())