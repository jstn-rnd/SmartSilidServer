from .models import User, Computer, UserLog, Student
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

@api_view(['POST'])
def add_user_logon(request): 
    username = request.data.get("userName")
    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")

    name_mac_match = Computer.objects.filter(computer_name = computer_name, mac_address = mac_address).first()
    mac_found = Computer.objects.filter(mac_address = mac_address).first()
    computer = " "

    if not name_mac_match: 
        if mac_found: 
            mac_found.computer_name = computer_name
            mac_found.status = 1
            mac_found.save()
            computer = mac_found
        else :
            print(f"2 : {mac_address}")

            newComputer = Computer(
                computer_name = computer_name, 
                mac_address = mac_address, 
                status = 1, 
            )

            if newComputer: 
                newComputer.save()
                computer = Computer.objects.filter(computer_name = computer_name).first()

    else : 
        name_mac_match.status = 1
        name_mac_match.save()
        computer = name_mac_match


    student = Student.objects.filter(username__iexact = username).first()

    latest_log_on_computer = UserLog.objects.filter(computer = computer).order_by("-date", "-logonTime").first()

    if latest_log_on_computer:
        if not latest_log_on_computer.logoffTime : 
            latest_log_on_computer.logoffTime = datetime.now().time().strftime("%H:%M:%S")
            latest_log_on_computer.save()

    if student: 
        logs = UserLog(
            student = student, 
            computer = computer, 
            date = datetime.today().date(),
            logonTime = datetime.now().time().strftime("%H:%M:%S")
        )
        logs.save()

        return Response({'status_message': 'success'})
        
    elif not student: 
        user = User.objects.filter(username__iexact = username).first()
        logs = UserLog(
            faculty = user, 
            computer = computer, 
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

    name_mac_match = Computer.objects.filter(computer_name = computer_name, mac_address = mac_address).first()
    mac_found = Computer.objects.filter(mac_address = mac_address).first()
    computer = " "
    
    if not name_mac_match: 
        if mac_found: 
            mac_found.computer_name = computer_name
            mac_found.status = 0
            mac_found.save()
            computer = mac_found
        else :
            print(f"2 : {mac_address}")

            newComputer = Computer(
                computer_name = computer_name, 
                mac_address = mac_address, 
                status = 0, 
            )

            if newComputer: 
                newComputer.save()
                computer = Computer.objects.filter(computer_name = computer_name).first()

    else : 
        name_mac_match.status = 0
        name_mac_match.save()
        computer = name_mac_match
    
    student = Student.objects.filter(username = username).first()

    if student: 
        latest_user_log = UserLog.objects.filter(
            student = student, 
            computer = computer, 
            date = date, 
            logoffTime__isnull=True).order_by("-date", "-logonTime").first()

    elif not student: 
        user = User.objects.filter(username = username).first()
        latest_user_log = UserLog.objects.filter(
            faculty = user, 
            computer = computer, 
            date = date, 
            logoffTime__isnull=True).order_by("-date", "-logonTime").first()
    
    else :
        return Response({
            "status_message" : "User not found"
        })

    latest_user_log.logoffTime = logoffTime
    latest_user_log.save()
    
    return Response({'status_message': 'success'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_logs_computer(request):
    pagination = request.data.get("pagination", None)
    start_date = request.data.get("start_date", None)
    end_date = request.data.get("end_date", None)
    username = request.data.get("username", None)
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

    # Initialize the query with the date range
    logs = UserLog.objects.filter(date__range=(start_date_params, end_date_params))

    # Apply the username filter if provided
    if username:
        if user_type == 'faculty':  # Only filter faculty
            logs = logs.filter(faculty__username__icontains=username, faculty__isnull=False)
        elif user_type == 'student':  # Only filter student
            logs = logs.filter(student__username__icontains=username, student__isnull=False)
        else:  # If no user type is specified, filter both faculty and student
            logs = logs.filter(
                (Q(faculty__username__icontains=username, faculty__isnull=False) |
                 Q(student__username__icontains=username, student__isnull=False))
            )

    # Apply the user_type filter if provided
    if user_type == 'faculty':
        logs = logs.filter(faculty__isnull=False)  # Only include logs where faculty is not null
    elif user_type == 'student':
    # If section is provided, filter by section
        if section:
            logs = logs.filter(student__isnull=False, student__section__name=section)
        else:
        # If section is not provided, just filter by student
            logs = logs.filter(student__isnull=False)
    # Apply the computer_name filter if provided
    if computer_name:
        logs = logs.filter(computer__computer_name=computer_name)

    # Pagination: Limit results and apply sorting
    logs = logs.select_related('faculty', 'student', 'computer').order_by("-date", "-logonTime")[:items*2]

    # Pagination exclusion logic
    if pagination > 1:
        excluded = items - 1 - 50
    else:
        excluded = -1

    json_response = []
    for i in range(items):
        if i > excluded and i < len(logs):
            if logs[i].faculty:
                data = {
                    "id": logs[i].id,
                    "computer_name": logs[i].computer.computer_name,
                    "username": logs[i].faculty.username,
                    "date": logs[i].date,
                    "logon": logs[i].logonTime,
                    "logoff": logs[i].logoffTime
                }
            elif logs[i].student:
                data = {
                    "id": logs[i].id,
                    "computer_name": logs[i].computer.computer_name,
                    "username": logs[i].student.username,
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
