
from django.shortcuts import render, redirect
import pyad
from django.http import HttpResponse
from .settings import get_ad_connection
from rest_framework.response import Response
from rest_framework.decorators import api_view
import pythoncom
from pyad.pyadexceptions import comException


def create_user_page(request): 
    return render(request, 'server_app/create_user.html')

@api_view(['POST'])
def create_user(request):
    if get_ad_connection():
        AD_BASE_DN = "DC=justine-server,DC=com"
        username = request.data.get('username')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        middle_initial = request.data.get("middle_initial")
        OU = request.data.get("OU")

        optional_attributes={
            "givenName": first_name,  
            "sn": last_name,          # Last name
            "initials": middle_initial  # Middle initial
            }

        if not username:
            return Response({"status_message" : "No Username"})
        elif not password : 
            return Response({"status_message" : "No Password"})
        elif not first_name : 
            return Response({"status_message" : "No First Name"})
        elif not last_name : 
            return Response({"status_message" : "No Last Name"})
        elif not middle_initial : 
            return Response({"status_message" : "No Middle Inital"})



        try:
            container_object = pyad.adcontainer.ADContainer.from_dn(f"OU={OU},{AD_BASE_DN}")
            new_user = pyad.aduser.ADUser.create(
                username, 
                container_object, 
                password=password,
                optional_attributes=optional_attributes
                )
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

@api_view(['POST'])
def auth_user(request):
    if get_ad_connection():
        AD_BASE_DN = "DC=justine-server,DC=com"
        username = request.data.get("username")
        password = request.data.get("password")
        OU = "Student"

        try:
            container = pyad.adcontainer.ADContainer.from_dn(f"OU={OU},{AD_BASE_DN}")
            user = None

            # Find the user in the specified OU
            for obj in container.get_children():
                if username == obj.get_attribute("samaccountname")[0]:
                    user = obj
                    break

            if user is None:
                return Response({
                    "status": "False",
                    "status_message": "User not found"
                })

            try:
                # Authenticate the user
                user.authenticate(password)
                return Response({
                    "status": "True",
                    "status_message": "User successfully authenticated"
                })
            except comException as e:
                return Response({
                    "status": "False",
                    "status_message": "User authentication unsuccessful",
                    "error_message": str(e)
                })

        except AttributeError as e:
            return Response({
                "status": "False",
                "status_message": "Error in fetching user",
                "error_message": str(e)
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