from datetime import time, timedelta
from server_app.models import Schedule


def check_if_time_is_valid(start, end):
    
    if time(6,0) <= start <= time(20,0) and time(6,0) <= end <= time(20,0): 
        
        return True

    return False

def check_schedule_overlap(day, start, end):
    schedules = Schedule.objects.filter(weekdays=day)

    for schedule in schedules:
        if start < schedule.end_time and end > schedule.start_time:
            return True

    return False
    
