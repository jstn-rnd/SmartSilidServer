from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect, render
from django.urls import reverse
import pyad
from django.conf import settings
from django.http import HttpResponseForbidden

from django.shortcuts import render, redirect
from .utils import convert_time

from .models import UserLogs, ComputerLogs

from django.contrib import messages
import subprocess 
import requests

from django.shortcuts import render, redirect, get_object_or_404
from .forms import WhitelistForm, BlacklistForm
from .models import Whitelist, Blacklist

from .utils import update_gpo
import logging
from .settings import get_ad_connection
import pythoncom
from django.http import JsonResponse
from django.middleware.csrf import get_token
from .utils import create_gpo, get_gpo, update_gpo 

def index(request):
    return render(request, 'server_app/index.html')

def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

def create_user_page(request): 
    return render(request, 'server_app/create_user.html')

def create_user(request):
    if get_ad_connection():
        AD_BASE_DN = "DC=justine-server,DC=com"
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')

        if not username or not password:
            return HttpResponse("Username and password are required")

        dn = f"CN={username},{AD_BASE_DN}"
        container_object = pyad.adcontainer.ADContainer.from_dn(f"OU=Student,{AD_BASE_DN}")
        try:
            new_user = pyad.aduser.ADUser.create(username, container_object, password=password)
            return HttpResponse("User succesfully created")
        except Exception as e:
            print(f"Failed to create user: {str(e)}")
            return HttpResponse(f"Failed to create user: {str(e)}")

    else:
        return HttpResponse("Failed to connect to Active Directory")
    
def read_user(request): 
    if get_ad_connection():
        AD_BASE_DN = "DC=justine-server,DC=com"

        try:
            container = pyad.adcontainer.ADContainer.from_dn(f"OU=Student,{AD_BASE_DN}")
            users = []
           
            for obj in container.get_children():
                
                user_data = obj.get_attribute("samaccountname")[0],
                print(user_data)
                users.append(user_data)
            
            users2 = list(zip(*users))[0]
            return render(request, 'server_app/read_user.html', {'users' : users2})

        except pyad.exceptions.ADObjectNotFound:
            return {"No user found."}

        except Exception as e:
            print(f"Failed to retrieve user: {str(e)}")
            return {"error": f"Failed to retrieve user: {str(e)}"}

    else:
        return {"error": "Failed to connect to Active Directory"}
    
def delete_user(request): 
    username = request.POST["username"]

    if get_ad_connection():
        AD_BASE_DN = "DC=justine-server,DC=com"

        try:
            search_filter = f"(SAMAccountName={username})"
            container = pyad.adcontainer.ADContainer.from_dn(f"OU=Student,{AD_BASE_DN}")
            for obj in container.get_children():
                user_data = obj.get_attribute("samaccountname")[0]
                if user_data == username:
                    try:
                        obj.delete()
                        return HttpResponse({'message': f'User {username} deleted successfully'})
                    except Exception as e:
                        return HttpResponse({'error': f'Failed to delete user: {str(e)}'})
                else : 
                    print(user_data)
                    return HttpResponse('error: User dont match')
            
        except pyad.exceptions.ADObjectNotFound:
            return HttpResponse(f"User with username '{username}' not found.")

        except Exception as e:
            print(f"Failed to delete user: {str(e)}")
            return HttpResponse(f"Failed to delete user: {str(e)}")

    else:
        return HttpResponse("Failed to connect to Active Directory")
    
def change_attribute_user(request): 
    if get_ad_connection():
        username = request.POST['username']
        OU = request.POST['OU']
        attributeChange = request.POST['attribute']
        value = request.POST['value']
        
        try :
            AD_BASE_DN = "DC=justine-server,DC=com"
            container = pyad.adcontainer.ADContainer.from_dn(f"OU={OU},{AD_BASE_DN}") 
            user = ''

            for obj in container.get_children():
                if username == obj.get_attribute("samaccountname")[0]:
                    user = obj
    
            user.set_password(value)

            return HttpResponse('Success')

        except pyad.exceptions.ADObjectNotFound:
            return HttpResponse("No user found.")

        except Exception as e:
            print(f"Failed to retrieve user: {str(e)}")
            return {"error": f"Failed to retrieve user: {str(e)}"}

    else:
        return {"error": "Failed to connect to Active Directory"}

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
    result = subprocess.check_output(["powershell", "-Command", script_users])
    print(result)
    return HttpResponse(result)

def manage_whitelist(request):
    if request.method == 'POST':
        form = WhitelistForm(request.POST)
        if form.is_valid():
            form.save()
            update_gpo()
            return redirect('manage_whitelist')
    else:
        form = WhitelistForm()
    whitelist = Whitelist.objects.all()
    return render(request, 'server_app/manage_whitelist.html', {'form': form, 'whitelist': whitelist})

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Blacklist
from .utils import add_url_to_blacklist, remove_url_from_blacklist
from django.views.decorators.http import require_POST


def manage_blacklist(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        url = request.POST.get('url')

        if not url:
            return HttpResponse("URL is required.", status=400)

        if action == 'add':
            try:
                add_url_to_blacklist(url)
                return redirect('manage_blacklist')  # Redirect or render a success template
            except Exception as e:
                return HttpResponse(f"Failed to add URL: {str(e)}", status=500)

        elif action == 'remove':
            try:
                remove_url_from_blacklist(url)
                return redirect('manage_blacklist')  # Redirect or render a success template
            except Exception as e:
                return HttpResponse(f"Failed to remove URL: {str(e)}", status=500)

        return HttpResponse("Invalid action.", status=400)

    # Handle GET requests
    blacklisted_urls = Blacklist.objects.all()
    return render(request, 'server_app/manage_blacklist.html', {'blacklisted_urls': blacklisted_urls})
