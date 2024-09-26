from .models import Schedule, User, Section
from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime

@api_view(['POST'])
def add_schedule(request): 
    
    subject = request.data.get("subject")
    section = request.data.get("section")
    start_time = request.data.get("start_time")
    end_time = request.data.get("end_time")
    weekdays = request.data.get("weekdays")
    faculty = request.data.get("faculty_name")

    faculty_object = User.objects.filter(username = faculty).first()
    section_object = Section.objects.filter(name = section).first()

    print(subject)
    print(section)
    print(start_time)
    print(end_time)
    print(weekdays)
    print(faculty)

    if subject and section_object and start_time and end_time and weekdays and faculty_object: 
        
        try:
            start_time_format = datetime.strptime(start_time, '%H:%M') 
            end_time_format = datetime.strptime(end_time, '%H:%M') 

            schedule = Schedule(
                faculty = faculty_object, 
                subject = subject, 
                section = section_object, 
                weekdays = weekdays, 
                start_time = start_time_format, 
                end_time = end_time_format
            )
            schedule.save()
            return Response({
                "status_message" : "Schedule succesfully added"
            })

        except Exception as e: 
            return Response({
                "status_message" : "Error in adding schedule",
                "error_message" : str(e)
            })

    else:
        return Response({
            "status_message" : "Missing or Invalid Input"
        }) 