from .models import User, Computer, UserLog
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserLogSerializer, ComputerSerializer
from datetime import datetime

@api_view(['POST'])
def add_user_logon(request): 
    username = request.data.get("userName")
    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")

    name_mac_match = Computer.objects.filter(computer_name = computer_name, mac_address = mac_address).first()
    mac_found = Computer.objects.filter(mac_address = mac_address).first()
    computer = " "

    print(f"1 : {mac_address}")

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

    
    user = User.objects.filter(username = username).first()
    
    data = {
        "user" : user.id, 
        "computer" : computer.id, 
        "logonDateTime" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
    logoffDateTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    user = User.objects.filter(username = username).first()
    computer = Computer.objects.filter(computer_name = computer_name).first()
    latest_user_log = UserLog.objects.filter(user = user, computer = computer, logoffDateTime_isnull=True).order_by("-logonDateTime").first()
    latest_user_log.logoffDateTime = logoffDateTime
    latest_user_log.save()
    print(logoffDateTime)
    return Response({
        "latest_log" : latest_user_log.logoffDateTime,
        "user" : latest_user_log.user.username 
    })



