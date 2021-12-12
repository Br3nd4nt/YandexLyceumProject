from PyQt5.QtCore import QTime, QDate


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