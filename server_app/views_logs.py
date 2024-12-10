from .models import Section, User, Computer, UserLog, Student
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserLogSerializer, ComputerSerializer
from datetime import datetime
from django.utils.dateparse import parse_date
from datetime import date
import math
from .utils import format_fullname
from .Utils.computer_utls import change_computer_name

@api_view(['POST'])
def add_user_logon(request): 
    username = request.data.get("userName")
    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")

    computer = change_computer_name(computer_name, mac_address)
    
    latest_log_on_computer = UserLog.objects.filter(computer = computer).order_by("-date", "-logonTime").first()

    if latest_log_on_computer:
        if not latest_log_on_computer.logoffTime : 
            latest_log_on_computer.logoffTime = datetime.now().time().strftime("%H:%M:%S")
            latest_log_on_computer.save()

    student = Student.objects.filter(username__iexact = username).first()

    if student: 
        logs = UserLog(
            user = format_fullname(student.first_name, student.middle_initial, student.last_name), 
            computer = computer.computer_name, 
            section = student.section.name,
            date = datetime.today().date(),
            logonTime = datetime.now().time().strftime("%H:%M:%S")
        )
        logs.save()

        return Response({'status_message': 'success'})
        
    elif not student: 
        user = User.objects.filter(username__iexact = username).first()
        logs = UserLog(
            user = format_fullname(user.first_name, user.middle_initial, user.last_name), 
            computer = computer.computer_name, 
            section = "faculty",
            date = datetime.today().date(),
            logonTime = datetime.now().time().strftime("%H:%M:%S")
        )
        logs.save()
        return Response({'status_message': 'success'})
    
    else : 
        return Response({'status_message': 'User/Student not found'})

@api_view(['POST'])
def add_user_logoff(request): 
    username = request.data.get("userName")
    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")
    date = datetime.today().date()
    logoffTime = datetime.now().time().strftime("%H:%M:%S")

    print(username)

    old_computer = Computer.objects.filter(computer_name = computer_name).first()
    computer = change_computer_name(computer_name, mac_address)

    if old_computer == computer:
        current_computer = computer
    else : 
        current_computer = old_computer

    computer_name = current_computer.computer_name
    
    student = Student.objects.filter(username__iexact = username).first()

    if student: 
        latest_user_log = UserLog.objects.filter(
            user = format_fullname(student.first_name, student.middle_initial, student.last_name),  
            computer = computer_name, 
            section = student.section.name,
            date = date, 
            logoffTime__isnull=True).order_by("-date", "-logonTime").first()

    elif not student: 
        user = User.objects.filter(username__iexact = username).first()
        fullname = format_fullname(user.first_name, user.middle_initial, user.last_name)

        latest_user_log = UserLog.objects.filter(
            user = fullname,  
            computer = computer_name, 
            section = "faculty",
            date = date, 
            logoffTime__isnull=True).order_by("-date", "-logonTime").first()
    
    else :
        return Response({
            "status_message" : "User not found"
        })

    latest_user_log.logoffTime = logoffTime
    latest_user_log.save()

    current_computer.status = 0 
    current_computer.save()
    
    return Response({'status_message': 'success'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_logs_computer(request):
    pagination = request.data.get("pagination", None)
    start_date = request.data.get("start_date", None)
    end_date = request.data.get("end_date", None)
    fullname = request.data.get("fullname", None)
    user_type = request.data.get("type", None)  # 'faculty' or 'student'
    computer_name = request.data.get("computer_name", None)
    section = request.data.get("section", None)

    # Default date range
    if not start_date and not end_date:
        start_date_params = date(1, 1, 1)
        end_date_params = date(9999, 12, 31)
    elif not start_date:
        start_date_params = date(1, 1, 1)
        end_date_params = parse_date(end_date)
    elif not end_date:
        start_date_params = parse_date(start_date)
        end_date_params = date(9999, 12, 31)
    else:
        start_date_params = parse_date(start_date)
        end_date_params = parse_date(end_date)

    if not pagination:
        pagination = 1

    pagination = float(pagination)
    logs = []
    items = int(pagination * 50)

    logs = UserLog.objects.filter(date__range=(start_date_params, end_date_params))

    if fullname:
        logs = logs.filter(user__icontains = fullname)

    if user_type == 'faculty':
        logs = logs.filter(section="faculty") 

    if user_type == 'student':
        logs = logs.exclude(section="faculty") 

    if section:       
        logs = logs.filter(section=section)
    
    if computer_name:
        logs = logs.filter(computer=computer_name)

    logs = logs.order_by("-date", "-logonTime")[:items*2]

    if pagination > 1:
        excluded = items - 1 - 50
    else:
        excluded = -1

    json_response = []
    for i in range(items):
        if i > excluded and i < len(logs):
            data = {
                "id": logs[i].id,
                "computer_name": logs[i].computer,
                "username": logs[i].user,
                "section" : logs[i].section,
                "date": logs[i].date,
                "logon": logs[i].logonTime,
                "logoff": logs[i].logoffTime
            }
        
            json_response.append(data)

    length = len(logs)
    pagination_length = length / 50

    if pagination_length % 1 != 0:
        pagination_length = math.floor(pagination_length)
        pagination_length += 1

    return Response({
        "status_message": "Logs obtained successfully",
        "logs": json_response,
        "pagination_length": pagination_length
    })
