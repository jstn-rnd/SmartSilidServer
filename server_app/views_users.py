
from django.shortcuts import render, redirect
import pyad
from django.http import HttpResponse
from .settings import get_ad_connection
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User
from django.contrib.auth import authenticate, login


def create_user_page(request): 
    return render(request, 'server_app/create_user.html')

#OU Creation 
# Hindi pa naayos yung type at section
@api_view(['POST'])
def create_user(request):
    if get_ad_connection():
        try:
            AD_BASE_DN = "DC=justine-server,DC=com"
            #username = request.data.get('username', None)
            password = request.data.get('password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            middle_initial = request.data.get("middle_initial", '')
            type = request.data.get("type", None)
            section = request.data.get("section", None)
            OU = None

            print(first_name + middle_initial + last_name + password)
            if type == "Faculty" or type == "Admin": 
                OU = type 
            else : 
                OU = section

            #if username == None : 
            username = first_name + "." + last_name + "." + middle_initial
            
            optional_attributes={
                "givenName": first_name,  
                "sn": last_name,          
                "initials": middle_initial  
                }
            
            container_object = pyad.adcontainer.ADContainer.from_dn(f"OU=Student,{AD_BASE_DN}")
            new_user = pyad.aduser.ADUser.create(
                username, 
                container_object, 
                password=password,
                optional_attributes=optional_attributes
                )
            
            if new_user : 
                user = User(
                    username = username,
                    first_name = first_name,
                    last_name = last_name, 
                    middle_initial = middle_initial,
                    type = "Student",
                    section = "None"
                )
                user.set_password(password)
                user.save()

            return Response({"status_message" : "User succesfully created"})
        except Exception as e:
            print(f"Failed to create user: {str(e)}")
            return Response({"status_message" : f"Failed to create user:3 {str(e)}"})

    else:
        return Response({"status_message" : "Failed to connect to Active Directory"})
    
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

        except Exception as e:
            print(f"Failed to retrieve user: {str(e)}")
            return {"error": f"Failed to retrieve user: {str(e)}"}

    else:
        return {"error": "Failed to connect to Active Directory"}

#admin shit 
@api_view(['POST'])
def auth_user(request):
    username = request.data.get("username")
    password = request.data.get("password")
    print(username + password)

    user = authenticate(request, username=username, password=password)

    if user is not None:
        print("yehey")
        return Response({
            "status": "True",
            "status_message": "User successfully authenticated"
        })
    else : 
        return Response({
            "status": "False",
            "status_message": "User not found"
        })


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