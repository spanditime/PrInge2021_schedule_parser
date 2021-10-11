from DubnaSchedule.Google import GoogleSharedSheet
from DubnaSchedule.Parser import Parser
from DubnaSchedule.Schedule import Schedule
from datetime import datetime

sheet = GoogleSharedSheet("1d3vlepJlRi2sxD9J8Le0GUz4mcRYugb2")
parser = Parser()
schedule = Schedule("schedules/schedule.json","schedules/time_schedule.json",parser)

schedule.synchronize(sheet,parser)

# use datetime.now() instead of datetime(2021,10,4,10,50) to get todays classes
print("Current:", schedule.getCurrentClasses(datetime(2021,10,4,10,50)))
print("Tooday:", schedule.getToodaysClasses(datetime(2021,10,4,10,50)))
