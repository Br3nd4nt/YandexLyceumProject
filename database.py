import sqlite3
import os
from event import Event



class Database:
    def __init__(self):
        self.name = 'events.sqlite'
        self.path = os.path.join(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Events'), self.name)
        if not os.path.isdir(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Events')) or self.name not in os.listdir(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Events')):
            self.create()
        self.con = sqlite3.connect(self.path)
        self.cur = self.con.cursor()

    def create(self):
        # print(self.name)
        if not os.path.isdir(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Events')):
            os.mkdir(os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'Events'))
        open(self.path, 'w+').close()
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
        con = sqlite3.connect(self.path)
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


if __name__ == '__main__':
    db = Database()
    db.createEvent(Event(1, 'a', 1, 1, 1, 1, 1, 1, 1, 'asdad', False, 'False'))
    print(db.getAllEvents())