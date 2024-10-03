from rest_framework.response import Response
from rest_framework.decorators import api_view
from .settings import get_ad_connection
import pyad
from .configurations import AD_BASE_DN, domain_name
from .models import User, RFID
from django.contrib.auth import authenticate, login
import pythoncom
import win32com.client

# Gawing pywin32 based imbes na pyad 
@api_view(['POST'])
def create_faculty(request):
    username = request.data.get('username', None)
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    middle_initial = request.data.get("middle_initial", '')
    type = request.data.get("type", None)

    optional_attributes={
        "givenName": first_name,  
        "sn": last_name,          
        "initials": middle_initial  
        }
    
    choices = ["admin", "faculty"]

    if not type in choices : 
        return Response({"status_message" : "Invalid Input"})
    
    if username == None : 
        username = first_name + "." + last_name + "." + middle_initial

    if len(username) > 20:
        return Response({
            "status_message" : f"Username {username} is too long"
        })

    try: 
        existing = User.objects.filter(username = username)

        if existing: 
            return Response({
                "status_message" : "User already exists"
            })

        faculty_db = User(
            username = username,
            first_name = first_name,
            last_name = last_name, 
            middle_initial = middle_initial,
            type = type
        )

        if faculty_db and get_ad_connection(): 
            faculty_db.set_password(password)

            container_object = pyad.adcontainer.ADContainer.from_dn(f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}")

            new_faculty = pyad.aduser.ADUser.create(
                username, 
                container_object, 
                password=password,
                optional_attributes=optional_attributes
                )
            
            faculty_db.save()

            return Response({"status_message" : "User succesfully created"})
        
        return Response({
            "status_message" : "Cannot create user, error in database"
        })
            
    except Exception as e:
        return Response({"status_message" : f"Error in creating user : {str(e)}"})
    

#admin shit 
@api_view(['POST'])
def authentication(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        return Response({
            "status": "True",
            "status_message": "User successfully authenticated"
        })
    else : 
        return Response({
            "status": "False",
            "status_message": "User not found"
        })
    

@api_view(['POST'])
def get_all_faculty_and_rfid(request):
    faculties = User.objects.all()
    
    json_response = []
    for faculty in faculties: 
        data = {
            "id" : faculty.id,
            "username" : faculty.username,
            "first_name" : faculty.first_name, 
            "middle_initial" : faculty.middle_initial, 
            "last_name" : faculty.last_name,
            "rfid" : [rfid_instance.rfid for rfid_instance in faculty.rfids.all()]
        }

        json_response.append(data)

    rfid_json = []
    rfids = RFID.objects.all()

    for rfid in rfids: 
        if not rfid.faculty : 
            data = {
                "rfid" : rfid.rfid
            }
            rfid_json.append(data)

    return Response({
        "status_message" : "Faculties obtained succesfully", 
        "faculties" : json_response, 
        "rfid" : rfid_json
    })
        
@api_view(["POST"])
def delete_faculty(request): 
    username = request.data.get("username")

    if not username : 
        return Response({
            "status_message" : "Missing input"
        })
    
    faculty_object = User.objects.filter(username=username).first()

    if not faculty_object: 
        return Response({
            "status_message" : "Faculty not found"
        })

    
    try : 
        pythoncom.CoInitialize()
        parent_dn = f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
        ad = win32com.client.Dispatch("ADsNameSpaces")
        ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
        faculty_ad = ad_obj.Create("user", f"CN={username}") # HIndi dito nag ccreate, niloload lang ganun
        faculty_ad.DeleteObject(0)

        faculty_object.delete()

        return Response({
            "status_message" : f"Faculty has been deleted successfully"
        })
        
    except Exception as e : 
        return Response({
            "error" : str(e),
            "status_message" : "Failed to delete section"
        })
    
@api_view(["POST"])
def get_all_faculty(request):
    faculties = User.objects.all()
    
    json_response = []
    for faculty in faculties: 
        data = {
            "id" : faculty.id,
            "username" : faculty.username,
            "first_name" : faculty.first_name, 
            "middle_initial" : faculty.middle_initial, 
            "last_name" : faculty.last_name,
        }

        json_response.append(data)

    return Response({
        "status_message" : "Faculties obtained succesfully", 
        "faculties" : json_response, 
    })
    
@api_view(["POST"])
def update_faculty(request): 
    id = request.data.get("id")
    username = request.data.get("username", None)
    first_name = request.data.get("first_name", None)
    last_name = request.data.get("last_name", None)
    middle_inital =request.data.get("middle_inital", None)
    type = request.data.get("type", None)

    errors = []

    if not id : 
        return Response({
            "status_message" : "Missing or invalid input"
        })
    
    faculty = User.objects.filter(id=id).first()

    if not faculty: 
        return Response({
            "status_message" : "Faculty not found"
        })
    
    try: 
        pythoncom.CoInitialize()
        ad = win32com.client.Dispatch("ADsNameSpaces")
        user_dn = f"CN={faculty.username},OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
        user_ad_obj = ad.GetObject("", f"LDAP://{user_dn}")
        print(1)
        
        if username: 
            if len(username) > 20: 
                errors.append("Username too long")
            user_ad_obj.sAMAccountName = username 
            user_ad_obj.userPrincipalName = username
            
            faculty_dn = f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
            container = ad.GetObject("", f"LDAP://{faculty_dn}")
            
            container.MoveHere(user_dn, f"CN={username}")
           
            faculty.username = username
            
        
        if first_name: 
            user_ad_obj.givenName = first_name
            faculty.first_name = first_name
        
        if last_name: 
            user_ad_obj.sn = last_name
            faculty.last_name = last_name

        if middle_inital:
            user_ad_obj.initials = middle_inital
            faculty.middle_initial = middle_inital

        if type : 
            choices = ["admin", "faculty"]

            if type in choices : 
                faculty.type = type
            
            errors.append("User type is wrong")

        user_ad_obj.setInfo()
        faculty.save()

        return Response({
            "status_message" : "Update is completed",
            "errors" : errors
        })

    except Exception as e: 
        return Response({
            "status_message" : f"Update has some errors {str(e)}",
            "errors" : errors
        })

    
