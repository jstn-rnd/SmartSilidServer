from datetime import time, timedelta
from server_app.models import Schedule


def check_if_time_is_valid(start, end):
    
    if time(5,0) <= start <= time(21,0) and time(5,0) <= end <= time(21,0): 
        
        return True

    return False

def check_schedule_overlap(day, start, end):
    schedules = Schedule.objects.filter(weekdays=day, semester__isActive = True)

    for schedule in schedules:
        if start < schedule.end_time and end > schedule.start_time:
            return True

    return False

def start_is_not_greater_than_end(start, end): 
    return end > start

def check_schedule_overlap_with_specific_schedule(day, start, end, sched_id): 
    schedules = Schedule.objects.filter(weekdays=day, semester__isActive = True)

    for schedule in schedules: 
        if schedule.id != sched_id and (start < schedule.end_time and end > schedule.start_time):
            return schedule.subject
    
    return False
