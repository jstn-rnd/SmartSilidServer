import re
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .settings import get_ad_connection
import pyad
from .configurations import AD_BASE_DN, domain_name
from .models import Computer, User, RFID, Scan
from django.contrib.auth import authenticate, login
import pythoncom
import win32com.client
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import check_password

# Gawing pywin32 based imbes na pyad 
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
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
            type = type, 
            hasWindows = 1
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
            
            
            admin_group = pyad.adgroup.ADGroup.from_cn("Domain Admins")
            new_faculty.add_to_group(admin_group)
            
            
            faculty_db.save()

            new_scan = Scan(
                faculty = faculty_db
            )

            new_scan.save()

            return Response({"status_message" : "User succesfully created"})
        
        return Response({
            "status_message" : "Cannot create user, error in database"
        })
            
    except Exception as e:
        print(str(e))
        return Response({"status_message" : f"Error in creating user : {str(e)}"})
    

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def get_all_faculty_and_rfid(request):
    faculties = User.objects.all()
    
    json_response = []
    for faculty in faculties: 
        scan = Scan.objects.filter(faculty = faculty).first()
        
        if not scan : 
            scan = Scan(
                faculty = faculty
            )
            scan.save()
            print()

        data = {
            "id" : faculty.id,
            "username" : faculty.username,
            "first_name" : faculty.first_name, 
            "middle_initial" : faculty.middle_initial, 
            "last_name" : faculty.last_name,
            "type" : faculty.type,
            "rfid" : scan.rfid.rfid if scan.rfid else None, 
        }

        if faculty.hasWindows == 1 :
            json_response.append(data)

    rfid_json = []
    rfids = RFID.objects.all()

    for rfid in rfids: 
        scan = Scan.objects.filter(rfid = rfid).first()
        if not scan : 
            data = {
                "rfid" : rfid.rfid
            }
            rfid_json.append(data)
    
    return Response({
        "status_message" : "Faculties obtained succesfully", 
        "faculties" : json_response, 
        "rfid" : rfid_json, 
    })
        
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def delete_faculty(request): 
    username = request.data.get("username")
    print(username)

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
        # parent_dn = f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
        # ad = win32com.client.Dispatch("ADsNameSpaces")
        # ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
        # faculty_ad = ad_obj.Create("user", f"CN={username}") # HIndi dito nag ccreate, niloload lang ganun
        # faculty_ad.DeleteObject(0)

        faculty_user = pyad.aduser.ADUser.from_cn(username)
        faculty_user.delete()

        faculty_object.delete()
        pythoncom.CoUninitialize()

        return Response({
            "status_message" : f"Faculty has been deleted successfully"
        })
        
    except Exception as e : 
        print(str(e))
        return Response({
            "error" : str(e),
            "status_message" : "Failed to delete section"
        })

# @api_view(["POST"])
# @permission_classes([IsAuthenticated])
# def delete_faculty(request): 
#     username = request.data.get("username")
#     print(username)

#     if not username : 
#         return Response({
#             "status_message" : "Missing input"
#         })
    
#     faculty_object = User.objects.filter(username=username).first()

#     if not faculty_object: 
#         return Response({
#             "status_message" : "Faculty not found"
#         })

    
#     try : 
      
#         pythoncom.CoInitialize()
#         parent_dn = f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
#         ad = win32com.client.Dispatch("ADsNameSpaces")
#         ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
#         user_object = ad_obj.Create("user", f"CN={username}") # HIndi dito nag ccreate, niloload lang ganun
#         user_object.DeleteObject(0)
#         faculty_object.delete()

#         return Response({
#             "status_message" : f"Faculty has been deleted successfully"
#         })
        
#     except Exception as e : 
#         # print(str(e))
#         print("Access check failed:", str(e))
#         return Response({
#             "error" : str(e),
#             "status_message" : "Failed to delete section"
#         })
    
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_all_faculty(request):
    faculties = User.objects.filter(hasWindows = 1)
    
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
@permission_classes([IsAuthenticated])
def update_faculty(request): 
    id = request.data.get("id")
    username = request.data.get("username", None)
    first_name = request.data.get("first_name", None)
    last_name = request.data.get("last_name", None)
    middle_initial =request.data.get("middle_initial", None)
    type = request.data.get("type", None)

    errors = []

    print("middle" + middle_initial)

    if not id : 
        return Response({
            "status_message" : "Missing or invalid input"
        })
    
    faculty = User.objects.filter(id=id).first()
    print(faculty.username)

    if not faculty: 
        return Response({
            "status_message" : "Faculty not found"
        })
    
    if faculty.hasWindows != 1 : 
        return Response({
            "status_message" : "Invalid Account"
        })
    
    try: 
        pythoncom.CoInitialize()
        ad = win32com.client.Dispatch("ADsNameSpaces")
        user_dn = f"CN={faculty.username},OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
        user_ad_obj = ad.GetObject("", f"LDAP://{user_dn}")
        print(1)
        
        if username and username != faculty.username: 
            if len(username) > 20: 
                errors.append("Username too long")
            
            faculty_dn = f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
            container = ad.GetObject("", f"LDAP://{faculty_dn}")
            
            container.MoveHere(f"LDAP://{user_dn}", f"CN={username}")
           
            faculty.username = username

            user_dn = f"CN={faculty.username},OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
            user_ad_obj = ad.GetObject("", f"LDAP://{user_dn}")

            user_ad_obj.sAMAccountName = username 
            user_ad_obj.userPrincipalName = username
            
        
        if first_name and first_name != faculty.first_name: 
            user_ad_obj.givenName = first_name
            faculty.first_name = first_name
        
        if last_name and last_name != faculty.last_name: 
            user_ad_obj.sn = last_name
            faculty.last_name = last_name

        if middle_initial and middle_initial != faculty.middle_initial and len(middle_initial) == 1 :
            user_ad_obj.initials = middle_initial.upper()
            faculty.middle_initial = middle_initial.upper()

        if type and type != faculty.type: 
            choices = ["admin", "faculty"]

            if type in choices : 
                faculty.type = type
            
            errors.append("User type is wrong")

        user_ad_obj.setInfo()
        faculty.save()
        pythoncom.CoUninitialize()

        return Response({
            "status_message" : "Update is completed",
            "errors" : errors
        })

    except Exception as e: 
        return Response({
            "status_message" : f"Update has some errors {str(e)}",
            "errors" : errors
        })

    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def get_faculty_by_id(request):
    id = request.data.get("id")

    if not id: 
        return Response({
            "status_message" : "Invalid input, not faculty id"
        })
    
    faculty = User.objects.filter(id = id).first()

    if not faculty: 
        return Response({
            "status_message" : "Faculty not found"
        })
    
    if faculty.hasWindows != 1 : 
        return Response({
            "status_message" : "Invalid account"
        })
    
    data = {
        "id" : faculty.id, 
        "username" : faculty.username, 
        "first_name" : faculty.first_name, 
        "middle_initial" : faculty.middle_initial, 
        "last_name" : faculty.last_name, 
        "type" : faculty.type
    }

    return Response({
        "status_message" : "Faculty has been fetched successfully", 
        "faculty_info" : data
    })


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # Extract username and password from the request
        username = request.data.get('username')
        password = request.data.get('password')

        # Manually authenticate the user using Django's authenticate method
        user = authenticate(request, username=username, password=password)

        if user.hasWindows != 1: 
            return Response ({
                "status_message" : "Invalid Account"
            })

        if user is not None:
            # If the user is authenticated, generate the JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            print(user)

            # Return the tokens and user ID in the response
            response_data = {
                'access': str(access_token),
                'refresh': str(refresh),
                'user_id': user.id,  # Include user ID in the response
                'type': user.type
            }
            return Response(response_data)
        else:
            return Response({"detail": "Invalid credentials"})
        

@api_view(["POST"])
def sign_up_admin(request): 
    username = request.data.get('username', None)
    password = request.data.get('password')
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    middle_initial = request.data.get("middle_initial", '')
    type = "admin"

    optional_attributes={
        "givenName": first_name,  
        "sn": last_name,          
        "initials": middle_initial  
        }
        
    if username == None : 
        username = first_name + "." + last_name + "." + middle_initial

    if len(username) > 20:
        return Response({
            "status_message" : f"Username {username} is too long"
        })
    
    if not (len(password) >= 8 and re.search(r"[A-Z]", password) and re.search(r"[a-z]", password) and re.search(r"[0-9]", password)):
        return Response({
            "status_message" : "Invalid password format"
        })
    
    try: 
        existing_user = User.objects.filter(type = "admin").first()

        if existing_user: 
            return Response({
                "status_message" : "Admin already exist"
            })
        
        existing_user = User.objects.filter(username = username).first()

        if existing_user: 
            return Response({
                "status_message" : "User already exist"
            })

        faculty_db = User(
            username = username,
            first_name = first_name,
            last_name = last_name, 
            middle_initial = middle_initial,
            type = "admin", 
            hasWindows = 1
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

            admin_computer = Computer.objects.filter(is_admin = 1).first()
            scan = Scan(
                faculty = faculty_db, 
                computer = admin_computer 
            )
            scan.save()

            return Response({"status_message" : "User succesfully created"})
        
        return Response({
            "status_message" : "Cannot create user, error in database"
        })
            
    except Exception as e:
        return Response({"status_message" : f"Error in creating user : {str(e)}"})
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_faculty_by_faculty(request):
    id = request.data.get('id')
    new_password = request.data.get('new_password')
    old_password = request.data.get('old_password')
    
    try :
        
        faculty = User.objects.filter(id = id).first()
    
        if not faculty : 
            return Response({
                "status_message" : "No user/faculty found"
            })

        if check_password(old_password, faculty.password) : 

            username = faculty.username
            pythoncom.CoInitialize()
            ad = win32com.client.Dispatch("ADsNameSpaces")
            user_dn = f"CN={username},OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
            user_ad_obj = ad.GetObject("", f"LDAP://{user_dn}")
            user_ad_obj.SetPassword(new_password)
            faculty.set_password(new_password)
            faculty.save()
            pythoncom.CoUninitialize()

            return Response({"status_message" : "Student password change succesful"})

        return Response({
            "status_message" : "old password is wrong"
        })
    
    except Exception as e:
           
        return Response({
            "status_message" : "Student password change is unsuccesful",
            "error_message" : str(e)
            })
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password_faculty_by_admin(request):
    id = request.data.get('id')
    new_password = request.data.get('new_password')
    
    try :
        
        faculty = User.objects.filter(id = id).first()
    
        if not faculty : 
            return Response({
                "status_message" : "No user/faculty found"
            })

        username = faculty.username
        pythoncom.CoInitialize()
        ad = win32com.client.Dispatch("ADsNameSpaces")
        user_dn = f"CN={username},OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}"
        user_ads_obj = ad.GetObject("", f"LDAP://{user_dn}")
        user_ads_obj.SetPassword(new_password)
        faculty.set_password(new_password)
        faculty.save()
        pythoncom.CoUninitialize()

        return Response({"status_message" : "Student password change succesful"})

    except Exception as e:
           
        return Response({
            "status_message" : "Student password change is unsuccesful",
            "error_message" : str(e)
            })
    



   