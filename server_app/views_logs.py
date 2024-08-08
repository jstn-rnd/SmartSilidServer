from .models import UserLog, ComputerLogs, User
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['POST'])
def add_user_logs(request): 
    username = request.POST["username"]
    dateTime = request.POST["dateTime"]
    user = User.objects.filter(username = username).first()
    userLog = UserLog(user = user, dateTime = dateTime)
    userLog.save()
    
    return HttpResponse("okay")

def add_computer_logs(request): 
    script_users = """
        Get-ADComputer -Filter * -Properties LastLogonDate | Select-Object Name, LastLogonDate | ConvertTo-JSON
    """
    result = 5
    print(result)
    return HttpResponse(result)