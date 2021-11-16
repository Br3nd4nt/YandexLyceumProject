from PyQt5 import uic
from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QDate, QObject, QSize, QThread, QTime, pyqtSignal
import sqlite3
import os
import datetime
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtWidgets import QApplication, QListWidgetItem, QMainWindow
import platform
import sys
from PyQt5 import QtWidgets


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
        # print(f'creating "{event.name}"')
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


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        MainWindow.setMaximumSize(QtCore.QSize(800, 600))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(800, 600))
        self.centralwidget.setMaximumSize(QtCore.QSize(800, 600))
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 801, 601))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.EventList = QtWidgets.QListWidget(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.EventList.sizePolicy().hasHeightForWidth())
        self.EventList.setSizePolicy(sizePolicy)
        self.EventList.setMinimumSize(QtCore.QSize(400, 0))
        self.EventList.setObjectName("EventList")
        self.horizontalLayout.addWidget(self.EventList)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(0, -1, -1, -1)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.EventName = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.EventName.setObjectName("EventName")
        self.verticalLayout_2.addWidget(self.EventName)
        self.Date = QtWidgets.QCalendarWidget(self.horizontalLayoutWidget)
        self.Date.setObjectName("Date")
        self.verticalLayout_2.addWidget(self.Date)
        self.EventInfo = QtWidgets.QPlainTextEdit(self.horizontalLayoutWidget)
        self.EventInfo.setObjectName("EventInfo")
        self.verticalLayout_2.addWidget(self.EventInfo)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label.setTextFormat(QtCore.Qt.AutoText)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout_3.addWidget(self.label)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.StartTime = QtWidgets.QTimeEdit(self.horizontalLayoutWidget)
        self.StartTime.setObjectName("StartTime")
        self.horizontalLayout_3.addWidget(self.StartTime)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_4.addWidget(self.label_2)
        self.horizontalLayout_4.addLayout(self.verticalLayout_4)
        self.EndTime = QtWidgets.QTimeEdit(self.horizontalLayoutWidget)
        self.EndTime.setObjectName("EndTime")
        self.horizontalLayout_4.addWidget(self.EndTime)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.CreateEvent = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.CreateEvent.setObjectName("CreateEvent")
        self.verticalLayout_2.addWidget(self.CreateEvent)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Планировщик"))
        self.EventName.setPlaceholderText(_translate("MainWindow", "Название события"))
        self.EventInfo.setPlaceholderText(_translate("MainWindow", "Дополнительная информация"))
        self.label.setText(_translate("MainWindow", "Начало"))
        self.label_2.setText(_translate("MainWindow", "Конец"))
        self.CreateEvent.setText(_translate("MainWindow", "Создать"))

class MainWindow(QMainWindow, Ui_MainWindow ):
    
    def __init__(self):
        super().__init__()
        # uic.loadUi('layouts/mainScreen.ui', self)
        # uic.loadUi('mainScreen.ui', self)
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
            currentTime = datetime.datetime.now().time()
            today = datetime.datetime.now().date()
            expired = []
            for i in self.events:
                if today > i[5] or (currentTime >= i[2] and today == i[5]):
                    expired.append(i[0])
                elif currentTime >= i[1] and not i[4] and i[0] not in expired and today == i[5]:
                    # print(i)
                    self.notif.notify(i[3], 'Событие началось')
                    self.cur.execute(f'UPDATE Events SET current = True WHERE id={i[0]}')
                    self.con.commit()
                    i = (i[0], i[1], i[2], i[3], True)
                    # print(i)
            if len(expired) > 0:
                # print(currentTime)
                self.updateDB(*expired)
                self.listUpdateSignal.emit()
                # res = []
                # for i in self.cur.execute('SELECT id, startHour, startMinute, endHour, endMinute, name, current FROM Events ORDER BY id').fetchall():
                #     res.append((i[0], time(i[1], i[2], 0), time(i[3], i[4], 0), i[5], i[6]))
                # self.events = res
            QThread.msleep(1000)


class Ui_EventWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(631, 565)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 0, 631, 566))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.NameEdit = QtWidgets.QPlainTextEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(30)
        sizePolicy.setHeightForWidth(self.NameEdit.sizePolicy().hasHeightForWidth())
        self.NameEdit.setSizePolicy(sizePolicy)
        self.NameEdit.setMinimumSize(QtCore.QSize(0, 30))
        self.NameEdit.setMaximumSize(QtCore.QSize(630, 30))
        self.NameEdit.setObjectName("NameEdit")
        self.verticalLayout.addWidget(self.NameEdit)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_9.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setMinimumSize(QtCore.QSize(0, 30))
        self.label_7.setMaximumSize(QtCore.QSize(150, 30))
        self.label_7.setObjectName("label_7")
        self.horizontalLayout_9.addWidget(self.label_7)
        self.StartTime = QtWidgets.QTimeEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.StartTime.sizePolicy().hasHeightForWidth())
        self.StartTime.setSizePolicy(sizePolicy)
        self.StartTime.setMaximumSize(QtCore.QSize(150, 30))
        self.StartTime.setObjectName("StartTime")
        self.horizontalLayout_9.addWidget(self.StartTime)
        self.verticalLayout_3.addLayout(self.horizontalLayout_9)
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_6 = QtWidgets.QLabel(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMaximumSize(QtCore.QSize(150, 30))
        self.label_6.setObjectName("label_6")
        self.horizontalLayout_8.addWidget(self.label_6)
        self.EndTime = QtWidgets.QTimeEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.EndTime.sizePolicy().hasHeightForWidth())
        self.EndTime.setSizePolicy(sizePolicy)
        self.EndTime.setMaximumSize(QtCore.QSize(150, 30))
        self.EndTime.setObjectName("EndTime")
        self.horizontalLayout_8.addWidget(self.EndTime)
        self.verticalLayout_3.addLayout(self.horizontalLayout_8)
        self.pastCheckbox = QtWidgets.QCheckBox(self.verticalLayoutWidget)
        self.pastCheckbox.setMaximumSize(QtCore.QSize(150, 16777215))
        self.pastCheckbox.setObjectName("pastCheckbox")
        self.verticalLayout_3.addWidget(self.pastCheckbox)
        self.InfoEdit = QtWidgets.QPlainTextEdit(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.InfoEdit.sizePolicy().hasHeightForWidth())
        self.InfoEdit.setSizePolicy(sizePolicy)
        self.InfoEdit.setMaximumSize(QtCore.QSize(300, 16777215))
        self.InfoEdit.setObjectName("InfoEdit")
        self.verticalLayout_3.addWidget(self.InfoEdit)
        self.horizontalLayout_6.addLayout(self.verticalLayout_3)
        self.Calendar = QtWidgets.QCalendarWidget(self.verticalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Calendar.sizePolicy().hasHeightForWidth())
        self.Calendar.setSizePolicy(sizePolicy)
        self.Calendar.setMinimumSize(QtCore.QSize(200, 480))
        self.Calendar.setMaximumSize(QtCore.QSize(400, 16777215))
        self.Calendar.setObjectName("Calendar")
        self.horizontalLayout_6.addWidget(self.Calendar)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.deleteButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setItalic(False)
        self.deleteButton.setFont(font)
        self.deleteButton.setObjectName("deleteButton")
        self.horizontalLayout_7.addWidget(self.deleteButton)
        self.cancelButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout_7.addWidget(self.cancelButton)
        self.saveButton = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.saveButton.setObjectName("saveButton")
        self.horizontalLayout_7.addWidget(self.saveButton)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label_7.setText(_translate("MainWindow", "Начало"))
        self.label_6.setText(_translate("MainWindow", "Конец"))
        self.pastCheckbox.setText(_translate("MainWindow", "Событие прошло"))
        self.deleteButton.setText(_translate("MainWindow", "Удалить"))
        self.cancelButton.setText(_translate("MainWindow", "Отменить"))
        self.saveButton.setText(_translate("MainWindow", "Сохранить"))


class EventWindow(QMainWindow, Ui_EventWindow):
    def __init__(self):
        super().__init__()
        # uic.loadUi('layouts/eventScreen.ui', self)
        # uic.loadUi('eventScreen.ui', self)
        self.setupUi(self)
        self.db = Database()
        self.deleteButton.setStyleSheet('QPushButton {color: #FF0000}')
        self.deleteButton.clicked.connect(self.delete)
        self.cancelButton.clicked.connect(self.cancel)
        self.saveButton.clicked.connect(self.save)

    def show(self, id: int, MainWindow: QMainWindow):
        self.setWindowFlag(0x00040000)
        super().show()
        self.event = self.db.getEvent(id)
        # print(self.event)
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
    app.exec_()
    # sys.exit(app.exec_())
    # exit()