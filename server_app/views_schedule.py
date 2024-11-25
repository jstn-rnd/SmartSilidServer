from .models import Schedule, User, Section, Semester
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from django.utils.dateparse import parse_date
from server_app.Utils.schedule_utils import check_if_time_is_valid, check_schedule_overlap, start_is_not_greater_than_end, check_schedule_overlap_with_specific_schedule
from .utils import format_fullname

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_schedule(request): 
    
    semester = request.data.get("semester_name")
    subject = request.data.get("subject")
    section = request.data.get("section")
    start_time = request.data.get("start_time")
    end_time = request.data.get("end_time")
    weekdays = request.data.get("weekdays")
    faculty = request.data.get("faculty_name")

    semester = Semester.objects.filter(name = semester).first()

    if not semester : 
        return Response({
            "status_message" : "Semester not found" 
        })

    faculty_object = User.objects.filter(username = faculty).first()
    section_object = Section.objects.filter(name = section).first()

    if subject and section_object and start_time and end_time and weekdays and faculty_object: 
        
        try:
            start_time_format = datetime.strptime(start_time, '%H:%M').time() 
            end_time_format = datetime.strptime(end_time, '%H:%M').time()

            valid = check_if_time_is_valid(start=start_time_format, end=end_time_format)
            not_overlap = check_schedule_overlap(day=weekdays, start=start_time_format, end=end_time_format)
            end_is_greater_than_start = start_is_not_greater_than_end(start_time_format, end_time_format)
            print(valid)
            print(not_overlap)
            print(end_is_greater_than_start)

            if valid and not not_overlap and end_is_greater_than_start: 
                schedule = Schedule(
                    faculty = faculty_object, 
                    subject = subject, 
                    section = section_object, 
                    weekdays = weekdays, 
                    start_time = start_time_format, 
                    end_time = end_time_format, 
                    semester = semester
                )
                schedule.save()
                return Response({
                    "status_message" : "Schedule succesfully added"
                })
            
            return Response({
                "status_message" : "Time may be invalid or overlaps on another schedule"
            })

        
        except Exception as e: 
            print(3)
            return Response({
                "status_message" : "Error in adding schedule",
                "error_message" : str(e)
            })

    else:
        return Response({
            "status_message" : "Missing or Invalid Input"
        }) 
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_all_schedule(request):
    
    active_semester = Semester.objects.filter(isActive = True).first()

    if not active_semester : 
        return Response({
            "status" : 0,
            "status_message" : "No active semesters"
        })
    
    schedules = Schedule.objects.filter(semester = active_semester)

    weekdays = Schedule.WEEKDAYS
    weekday_order = {abbr: index for index, (abbr, day) in enumerate(weekdays)}

    sorted_objects = sorted(schedules, key=lambda schedule: weekday_order[schedule.weekdays])

    json_response = []
    for schedule in sorted_objects:
        faculty = schedule.faculty
        fullname = format_fullname(faculty.first_name, faculty.middle_initial, faculty.last_name)
        data = {
            'id' : schedule.id,
            'subject' : schedule.subject,
            'section' : schedule.section.name,
            'start_time' : schedule.start_time,
            'end_time' : schedule.end_time,
            'weekdays' : schedule.weekdays,
            'faculty' : fullname,
        }

        json_response.append(data)

    return Response({
        "status" : 1,
        "status_message" : "Schedule has been obtained successfully",
        "current_semester" : active_semester.name, 
        "current_semester_id" : active_semester.id,
        "schedule" : json_response
       })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_schedule(request): 
    id = request.data.get("id")
    subject = request.data.get("subject", None)
    section = request.data.get("section", None)
    start_time = request.data.get("start_time", None)
    end_time = request.data.get("end_time", None)
    weekdays = request.data.get("weekdays", None)
    faculty = request.data.get("faculty_name", None)

    print(start_time)
    print(end_time)
    print(weekdays)

    if not id : 
        return Response({
            "status_message" : "Id field is required"
        })
    
    error_message = []
    schedule = Schedule.objects.filter(id=id).first()

    if not schedule: 
        return Response({
            "status_message" : "Schedule not found"
        })

    if subject: 
        schedule.subject = subject

    if section : 
        section_obj = Section.objects.filter(name = section).first()
       
        if section_obj: 
            schedule.section = section_obj

        else :
            error_message.append("Section is not found")

    if start_time: 
        try: 
            start = datetime.strptime(start_time, '%H:%M').time()
            end = schedule.end_time

            overlap = check_schedule_overlap_with_specific_schedule(schedule.weekdays, start, end, id)
            valid = check_if_time_is_valid(start=start, end=end)
            end_is_greater_than_start = start_is_not_greater_than_end(start, end)
            print("\nSTARTTIME")
            print(f"Nag ooverlap : {overlap}")
            print(f"Valid ba : {valid}\n")

            if not overlap and valid and end_is_greater_than_start: 
                schedule.start_time = start
            
            else : 
                error_message.append("Invalid start time")
                print("B")
        
        except ValueError as e:
            print("A")
            error_message.append("Invalid start time")

    if end_time: 
        try: 
            end = datetime.strptime(end_time, '%H:%M').time()
            start = schedule.start_time
            
            overlap = check_schedule_overlap_with_specific_schedule(schedule.weekdays, start, end, id)
            valid = check_if_time_is_valid(start=start, end=end)
            end_is_greater_than_start = start_is_not_greater_than_end(start, end)

            if not overlap and valid and end_is_greater_than_start: 
                schedule.end_time = end
            
            else : 
                error_message.append("Invalid end time")
        
        except ValueError as e:
            print(str(e))
            error_message.append("Invalid end time")
        
    if weekdays: 
        WEEKDAYS = Schedule.WEEKDAYS

        print(WEEKDAYS)

        for days in WEEKDAYS : 
            day = list(days)
            if weekdays == day[0]:
                schedule.weekdays = days[0] 



    if faculty: 
        faculty_object = User.objects.filter(username = faculty).first()

        if faculty_object : 
            schedule.faculty = faculty_object
        else : 
            error_message.append("Faculty not found")

    if not subject and not section and not start_time and not end_time and not weekdays and not faculty:
        error_message.append("No change parameters was passed")

    schedule.save()

    return Response({
        "status_message" : "Update was finished",
        "error_message" : error_message 
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_schedule(request): 
    id = request.data.get("id")

    if not id : 
        return Response({
            "status_message" : "ID is required"
        })
    schedule = Schedule.objects.filter(id= id).first()

    if not schedule : 
        return Response({
            "status_message" : "Schedule not found"
        })
    
    schedule.delete()

    return Response({
        "status_message" : "Schedule has been deleted succesfully"
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_semester(request): 
    semester_name = request.data.get("semester_name")

    semesters = Semester.objects.all()

    for semester in semesters : 
        semester.isActive = False
        semester.save()
    
    new_semester = Semester(
        name = semester_name, 
        isActive = True
    )

    new_semester.save()

    return Response({
        "status_message" : "Semester has been started succesfully"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def end_semester(request): 
    semesters = Semester.objects.all()

    for semester in semesters : 
        semester.isActive = False
        semester.save()

    return Response({
        "status_message" : "Semester has been ended succesfully"
    })
    
    

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def get_past_semesters(request): 

    semesters = Semester.objects.filter(isActive = False)

    response_json = []
    for semester in semesters: 
        data = {
            "semester_id" : semester.id, 
            "semester_name" : semester.name
        }
        response_json.append(data)

    return Response({
        "status" : 1, 
        "status_message" : "Past semester has been obtained successfully", 
        "past_semester" : response_json
        })    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_schedule_by_semester(request):
    semester_id = request.data.get("semester_id")

    if not semester_id: 
        return Response({
            "status" : 0, 
            "status_message" : "Missing or invalid input"
        })

    semester = Semester.objects.filter(id = semester_id).first()

    if not semester : 
        return Response({
            "status" : 0, 
            "status_message" : "Semester has not been found"
        })
    
    schedules = Schedule.objects.filter(semester = semester)

    response_json = []

    for schedule in schedules: 
        data = {
            'id' : schedule.id,
            'subject' : schedule.subject,
            'section' : schedule.section.name,
            'start_time' : schedule.start_time,
            'end_time' : schedule.end_time,
            'weekdays' : schedule.weekdays,
            'faculty' : schedule.faculty.username,
        }
        response_json.append(data)
    
    if semester :
        return Response({
            "status" : 1,
            "status_message" : "Schedules has been obtained successfully", 
            "semester" : semester.name, 
            "semester_id" : semester.id, 
            "schedules" : response_json
        })