from .models import UserLogs, ComputerLogs
from django.http import HttpResponse


def add_user_logs(request): 
    username = request.POST["username"]
    dateTime = request.POST["dateTime"]
    userLog = UserLogs(userName = username, dateTime = dateTime)
    userLog.save()
    
    return HttpResponse("okay")

def add_computer_logs(request): 
    script_users = """
        Get-ADComputer -Filter * -Properties LastLogonDate | Select-Object Name, LastLogonDate | ConvertTo-JSON
    """
    result = 5
    print(result)
    return HttpResponse(result)