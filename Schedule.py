import json
import datetime 
import os
import io
import Google
import Parser


# todo:
# create schema for schedule.json and time_schedule.json
# implement schema usage afterwards

class Schedule:
    weekdays = {0:"Понедельник",
                1:"Вторник",
                2:"Среда",
                3:"Четверг",
                4:"Пятница",
                5:"Суббота",
                6:"Воскресенье"}
    
    def __init__(self,filename, time_filename,google_shared_sheet: Google.GoogleSharedSheet, parser: Parser.Parser) -> None:
        self.time_schedule_json = None
        self.filename = filename
        self.time_filename = time_filename
        self.json = None
        self.google_sheet = google_shared_sheet
        self.parser = parser
        
        # initiating schedule from GoogleSharedSheet or from file
        if self.synchronize():
            pass
        elif not self.loadFromFile(filename):
            # replace with getting default from shcedule/schema.json after its done if synchronise failed 
            self.json = json.load("\{\}") 
            self.filename = "schedules/schedule.json"
            self.save()
        self.loadTimeSchedule()
        print(f"schedule:{self.json}\n\ntime schedule:{self.time_schedule_json}\n\n")

    def loadTimeSchedule(self):
        if os.path.exists(self.time_filename):
            file = io.open(self.time_filename, encoding='utf-8', mode = 'r')
            #b4 loading the file check if its valid using schema.json for schedule after its done
            self.time_schedule_json = json.load(file)
            return True
        return False
    
    def synchronize(self):
        result = self.parser.parseToJson(self.google_sheet)
        if result != None:
            self.json = result
            self.save()
            return True
        return False

    def loadFromFile(self,filename):
        if os.path.exists(filename):
            file = io.open(filename, encoding='utf-8')
            #b4 loading the file check if its valid using schema.json for schedule after its done
            self.json = json.load(file)["schedule"]
            self.filename = filename
            return True
        return False

    def saveToFile(self,filename) -> bool:
        with io.open(filename, encoding='utf-8',mode='w' if os.path.exists(filename) else 'x' ) as file:
            file.write(json.encoder.JSONEncoder.encode({"schedule":self.json}))

    def save(self):
        self.saveToFile(self.filename)
    
    def getToodayClassesTimeByIndex(self,dt,index):
        begins_t = datetime.datetime.strptime(self.time_schedule_json[index]["begins"],"%H:%M").time()
        ends_t   = datetime.datetime.strptime( self.time_schedule_json[index]["ends"] ,"%H:%M").time()
        begins   = datetime.datetime(dt.year,dt.month,dt.day,begins_t.hour,begins_t.minute)
        ends     = datetime.datetime(dt.year,dt.month,dt.day,ends_t.hour,ends_t.minute)
        return begins,ends

    def getCurrentClassesTime(self,dt):
        begins = None
        ends = None
        idx = '0'
        started = False
        for index in self.time_schedule_json:
            begins, ends = self.getToodayClassesTimeByIndex(dt, index)
            idx = int(index)
            if (dt - begins) < datetime.timedelta(0):
                break
            elif (dt - ends) <= datetime.timedelta(0):
                started = True
                break
            elif index == '6':
                return None, None, None, None
        return started, begins, ends, idx

    def getCurrentClasses(self,dt = datetime.datetime.now()):
        weekday = dt.weekday()
        isOddWeek = Schedule.isThisWeekOdd(dt)
        
        started, begins, ends, index = self.getCurrentClassesTime(dt)
        if weekday == 6 or started == None:
            return None, None, None, None, None
        info = None
        weekdaystr = Schedule.weekdays[weekday]
        for i in range(int(index),7):
            idx = str(i)
            begins,ends = self.getToodayClassesTimeByIndex(dt,idx)
            if idx in self.json[weekdaystr]:
                curr = self.json[weekdaystr][idx]
                if ("Нечет" if isOddWeek else "Чет") in curr:
                    info = curr["Нечет" if isOddWeek else "Чет"]
                    started = False if idx != index else started
                    index = idx
                    break
                elif "ЧетНечет" in curr:
                    info = curr["ЧетНечет"]
                    started = False if idx != index else started
                    index = idx
                    break
        if info == None:
            return None, None, None, None, None
        return index, begins, ends, started, info

    def getYearStartDate(dt):
        year_offset = -1 if dt.month < 9 else 0
        st = datetime.datetime(dt.year + year_offset, 9, 1)
        # st = st if st.weekday() < 5 else st = datetime.datetime(st.year, 9, 3)
        days_offset = st.weekday()
        st -= datetime.timedelta(days = days_offset)
        return st
    
    def isThisWeekOdd(dt = datetime.datetime.now()):
        delta = dt - Schedule.getYearStartDate(dt)
        return ((delta.days + 1) // 7 + (1 if (delta.days + 1) % 7 != 0 else 0))%2 == 1

