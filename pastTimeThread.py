from datetime import datetime, time, date
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sqlite3
from database import Database
from notification import Notification


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
        self.con = sqlite3.connect(Database().path)
        self.cur = self.con.cursor()
        self.events = []
        while True:
            self.events.clear()
            for i in self.cur.execute('SELECT id, startHour, startMinute, endHour, endMinute, name, current, year, month, day FROM Events ORDER BY id').fetchall():
                self.events.append((i[0], time(i[1], i[2], 0), time(i[3], i[4], 0), i[5], i[6], date(i[7], i[8], i[9])))
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