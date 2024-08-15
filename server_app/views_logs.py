from .models import UserLog, ComputerLogs, User, Computer
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserLogSerializer, ComputerSerializer

@api_view(['POST'])
def add_user_logs(request): 
    username = request.data.get("username")
    user = User.objects.filter(username = username).first()
    print(user.first_name)

    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")

    name_mac_match = Computer.objects.filter(computer_name = computer_name, mac_address = mac_address).first()
    mac_found = Computer.objects.filter(mac_address = mac_address).first()
    computer = " "

    if not name_mac_match: 
        if mac_found: 
            mac_found.mac_address = mac_address
            mac_found.save()
            computer = mac_found
        else :
            computer_data = {
                'computer_name' : computer_name, 
                'mac_address' : mac_address
            }
            newComputer = ComputerSerializer(data = computer_data)
            if newComputer.is_valid(): 
                newComputer.save()
                computer = Computer.objects.filter(computer_name = computer_name).first()

    else : 
        computer = name_mac_match
    
    data = {
        "user" : user.id, 
        "computer" : computer.id, 
        "dateTime" : request.data.get("dateTime")
    }
    userLogSerializer = UserLogSerializer(data = data)
    
    if userLogSerializer.is_valid():
        userLogSerializer.save()
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)
    return Response(userLogSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

def add_computer_logs(request): 
    script_users = """
        Get-ADComputer -Filter * -Properties LastLogonDate | Select-Object Name, LastLogonDate | ConvertTo-JSON
    """
    result = 5
    print(result)
    return HttpResponse(result)