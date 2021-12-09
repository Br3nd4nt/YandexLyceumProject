from PyQt5 import uic
from PyQt5.QtCore import QTime, QDate
from PyQt5.QtWidgets import QMainWindow
from database import Database
from event import Event

class EventWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('layouts/eventScreen.ui', self)
        # uic.loadUi(self)
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

