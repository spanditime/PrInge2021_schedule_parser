import os


class Parser:
    weekdays = {0:"Понедельник",
                1:"Вторник",
                2:"Среда",
                3:"Четверг",
                4:"Пятница",
                5:"Суббота",
                6:"Воскресенье"}

    def __init__(self):
        self.column = 0
        pass
    
    def getWeekdayName(self,day: int) -> str:
        return Parser.weekdays[day%7]

    def parseToJson(self,sheet_id,data,startRow,startCol,merges,themeColors):
        return None
