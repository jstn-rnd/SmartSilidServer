from .models import User, Computer, UserLog
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserLogSerializer, ComputerSerializer
from datetime import datetime
from django.utils.dateparse import parse_date
from datetime import date

@api_view(['POST'])
def add_user_logon(request): 
    username = request.data.get("userName")
    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")

    name_mac_match = Computer.objects.filter(computer_name = computer_name, mac_address = mac_address).first()
    mac_found = Computer.objects.filter(mac_address = mac_address).first()
    computer = " "

    print(f"1 : {mac_address}")
    print(username)

    if not name_mac_match: 
        if mac_found: 
            mac_found.computer_name = mac_address
            mac_found.save()
            computer = mac_found
        else :
            print(f"2 : {mac_address}")
            computer_data = {
                'computer_name' : computer_name, 
                'mac_address' : mac_address
            }
            newComputer = ComputerSerializer(data = computer_data)
            if newComputer.is_valid(): 
                newComputer.save()
                computer = Computer.objects.filter(computer_name = computer_name).first()

    else : 
        print(f"3 : {mac_address}")
        computer = name_mac_match

    
    user = User.objects.filter(username__iexact = username).first()
    
    data = {
        "user" : user.id, 
        "computer" : computer.id, 
        "date" : datetime.today().date(),
        "logonTime" : datetime.now().time().strftime("%H:%M:%S")
    }
    userLogSerializer = UserLogSerializer(data = data)
    
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if userLogSerializer.is_valid():
        userLogSerializer.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response(userLogSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
def add_user_logoff(request): 
    username = request.data.get("userName")
    computer_name = request.data.get("computerName")
    date = datetime.today().date()
    logoffTime = datetime.now().time().strftime("%H:%M:%S")

    user = User.objects.filter(username = username).first()
    computer = Computer.objects.filter(computer_name = computer_name).first()
    latest_user_log = UserLog.objects.filter(user = user, computer = computer, date = date, logoffTime__isnull=True).order_by("-date", "-logonTime").first()
    latest_user_log.logoffTime = logoffTime
    latest_user_log.save()
    print(logoffTime)
    return Response({
        "latest_log" : latest_user_log.logoffTime,
        "user" : latest_user_log.user.username 
    })


@api_view(['POST'])
def get_logs(request):
    pagination = request.data.get("pagination", None)
    start_date = request.data.get("start_date", None)
    end_date = request.data.get("start_date", None)
    username = request.data.get("username", None)
    computer_name = request.data.get("computer_name", None)

    if not start_date and not end_date :
        start_date_params = date(1, 1, 1)
        end_date_params = date(9999, 12, 31)

    else :
        start_date_params = parse_date(start_date)
        end_date_params = parse_date(end_date) 

    if not pagination: 
        pagination = 1
    
    items = int(pagination * 50) 
    
    if computer_name:
        computer = Computer.objects.filter(computer_name__icontains = computer_name).all()
        logs = UserLog.objects.filter(computer = computer, date__range=(start_date_params, end_date_params)).order_by("-date")[:items]

    elif username: 
        user = User.objects.filter(username__icontains = username).all()
        logs = UserLog.objects.filter(user = user.id, date__range=(start_date_params, end_date_params)).order_by("-date")[:items]
    
    else :
        logs = UserLog.objects.filter(date__range=(start_date_params, end_date_params)).order_by("-date")[:items]

    if pagination > 1 :
        excluded = items - 1 - 50
    else : 
        excluded = -1
    
    json_response = []
    for i in range(items):
        if i >= excluded -1 and i < len(logs):
            data = {
                "computer_name" : logs[i].computer.computer_name,
                "username" : logs[i].user.username,
                "date" : logs[i].date,
                "logon" : logs[i].logonTime,
                "logoff" : logs[i].logoffTime
            }
            json_response.append(data)
           
    return Response({
        "status_message" : "Logs obtained succesfully",
        "logs" : json_response
    })
