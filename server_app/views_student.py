
from django.shortcuts import render, redirect
import pyad
from django.http import HttpResponse
import pyad.aduser
from .settings import get_ad_connection
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import RFID, Computer, Scan, User, Section, Student
from .configurations import AD_BASE_DN
import pythoncom
import win32com.client
from pyad.pyadexceptions import win32Exception


def create_user_page(request): 
    return render(request, 'server_app/create_user.html')

#OU Creation 
# Hindi pa naayos yung type at section
#Lagyan ng admin rights yung mga nasa faculty


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_student(request):
    if get_ad_connection():

        try:
            username = request.data.get('username', None)
            password = request.data.get('password')
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            middle_initial = request.data.get("middle_initial", '')
            section = request.data.get("section", None)
        
            optional_attributes={
                "givenName": first_name,  
                "sn": last_name,          
                "initials": middle_initial  
                }

            if not username or not password or not first_name or not last_name or not middle_initial or not section : 
                return Response({
                    "error_message" : "Invalid or missing input"
                    })
            
            if len(username) > 20 or len(first_name) > 30 or len(last_name) > 30 or len(middle_initial) > 30 or len(password) > 30: 
                return Response({
                    "error_message" : "Some inputs may be too long, please recheck it"
                })
                  
            section_object = Section.objects.filter(name = section).first()

            if section_object : 
                container_object = pyad.adcontainer.ADContainer.from_dn(f"OU={section},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}")
                new_user = pyad.aduser.ADUser.create(
                    username, 
                    container_object, 
                    password=password,
                    optional_attributes=optional_attributes
                    )
                
                if new_user : 
                    student = Student(
                        username = username,
                        first_name = first_name,
                        last_name = last_name, 
                        middle_initial = middle_initial,
                        section = section_object
                    )
                    
                    student.save()

                scan = Scan(
                    student = student
                )

                scan.save()

                return Response({"status_message" : "User succesfully created"})
            else : 
                return Response({"status_message" : "Section does not exist"})
                    
        except win32Exception as e: 
            already_exist = "0x80071392" in str(e)
            password_history_error = "0x800708c5" in str(e)

            if password_history_error:
                user = pyad.aduser.ADUser.from_cn(username)
                user.delete()
                error_message = "Password error! Ensure that password is not similar to username or past password"

            if already_exist : 
                error_message = " Username is already being used within the domain"

            print("")
            return Response({"error_message" : error_message})

        except Exception as e:          
            error_code = "0x8007202f"

            if error_code in str(e): 
                error_message = "User might already exist or password format is incorrect"
            print(f"Failed to create user: {str(e)}")
            return Response({"error_message" : error_message})
        

    else:
        return Response({"error_message" : "Failed to connect to Active Directory"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_student(request):
    username = request.data.get("username")
    student = Student.objects.filter(username = username).first()

    print(student)
    section = student.section.name

    
    if student : 
        try :     
            pythoncom.CoInitialize()
            parent_dn = f"OU={section},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            ad = win32com.client.Dispatch("ADsNameSpaces")
            ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
            user_object = ad_obj.Create("user", f"CN={username}") # HIndi dito nag ccreate, niloload lang ganun
            user_object.DeleteObject(0)

            scan = Scan.objects.filter(student = student).first()

            if scan : 
                scan.delete()

            student.delete()

            return Response({
                "status_message" : f"User {username} has been deleted successfully"
            })
        
        except Exception as e : 
            return Response({
                "status_message" : "Failed to delete user",
                "error_message" : str(e)
            })
    
    else : 
        return Response({
            "error_message" : f"User {username} does not exist"
        })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_student(request): 
    username = request.data.get('username')
    student = Student.objects.filter(username = username).first()
    value = request.data.get('new_password')

    if len(value) > 30 :
        return Response({
            "error_message" : "Password is too long! Ensure that it is below 30 characters"
        }) 
    
    if student: 
        
        try :
            section = student.section.name
            pythoncom.CoInitialize()
            user = pyad.aduser.ADUser.from_cn(username)
            user.set_password(value)

            return Response({"status_message" : "Student password change succesful"})

        except win32Exception as e: 
            password_history_error = "0x800708c5" in str(e)

            if password_history_error:
                error_message = "Password error! Ensure that password is not similar to username or past password"


            return Response({"error_message" : error_message})
        
        except Exception as e:
           
            return Response({
                "status_message" : "Student password change is unsuccesful",
                "error_message" : str(e)
                })

    else:
        return Response({"status_message" : "Student not found"})
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_section(request): 
    username = request.data.get('username')
    new_section = request.data.get('new_section')
    student = Student.objects.filter(username = username).first()
    
    if student : 
        try : 
            section = student.section.name
            pythoncom.CoInitialize()
            ad = win32com.client.Dispatch("ADsNameSpaces")
            user_dn = f"CN={username},OU={section},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            user_ad_obj = ad.GetObject("", f"LDAP://{user_dn}")
            target_section_dn = f"OU={new_section},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            target_section_ad_obj = ad.GetObject("", f"LDAP://{target_section_dn}")
            target_section_ad_obj.MoveHere(user_ad_obj.ADsPath, f"CN={username}")

            new_section_db = Section.objects.filter(name = new_section).first()
            student.section = new_section_db
            student.save()

            return Response({"status_message" : "User has been succesfully moved into a different section"})

        except Exception as e : 
            return Response({
                "status_message" : "Failed to move section",
                "error" : str(e)
            })

    else : 
        return Response({"status_message" : "User not found"})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_students(request):

    result = []
    students = Student.objects.all()

    for student in students:
        scan = Scan.objects.filter(student = student).first()

        if not scan : 
            scan = Scan(
                student = student
            )
            scan.save()

        info = {
            "id" : student.id,
            "username" : student.username, 
            "first_name" : student.first_name, 
            "last_name" : student.last_name, 
            "middle_initial" : student.middle_initial,
            "section" : student.section.name, 
            "computer" : scan.computer.computer_name if scan.computer else None,
            "rfid" : scan.rfid.rfid if scan.rfid else None, 
        }
        result.append(info)

    rfid_json = []
    rfids = RFID.objects.all()

    for rfid in rfids: 
        scan = Scan.objects.filter(rfid=rfid).first()
        if not scan : 
            data = {
                "rfid" : rfid.rfid
            }
            rfid_json.append(data)
    
    computers = Computer.objects.all()
    sections = Section.objects.all()
    computers_json = []
    
    for section in sections: 
        section_json = []

        for computer in computers : 
        
            scan = Scan.objects.filter(
                faculty__isnull = True, 
                student__isnull = False, 
                computer = computer, 
                student__section = section).first()

            if not scan: 
                data = {
                    "computer" : computer.computer_name
                }
                section_json.append(data)
        
        data = {
            f"{section.name}" : section_json
        }
        computers_json.append(data)
        
    return Response({
        "status_message" : "User obtained succesfully",
        "students" : result, 
        "rfid" : rfid_json, 
        "computer" : computers_json
    })

   
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def update_student(request): 
    id = request.data.get("id")
    username = request.data.get("username", None)
    first_name = request.data.get("first_name", None)
    last_name = request.data.get("last_name", None)
    middle_initial =request.data.get("middle_initial", None)

    print(f"ID{id}")

    errors = []

    if not id : 
        return Response({
            "status_message" : "Missing or invalid input"
        })
    
    student = Student.objects.filter(id=id).first()
    print("####################################")
    print(student.username)

    if not student: 
        return Response({
            "status_message" : "Student not found"
        })
    
    if middle_initial and len(middle_initial) != 1 : 
        errors.append("Invalid length of middle initial")
    
    try: 
        pythoncom.CoInitialize()
        ad = win32com.client.Dispatch("ADsNameSpaces")
        student_dn = f"CN={student.username},OU={student.section.name},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
        student_ad_obj = ad.GetObject("", f"LDAP://{student_dn}")
        print(1)

        counter = 0
        while(counter <= 0) :
            if username and username != student.username: 
                if len(username) > 20: 
                    errors.append("Username too long")
                    counter += 1
                    break
                    
                # already_exist = pyad.aduser.ADUser.from_cn(username)

                # if already_exist : 
                #     errors.append("Username already exist")
                #     break
                
                section_dn = f"OU={student.section.name},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
                container = ad.GetObject("", f"LDAP://{section_dn}")
                print(2)

                container.MoveHere(f"LDAP://{student_dn}", f"CN={username}")

                print(3)
            
                student.username = username

                student_dn = f"CN={student.username},OU={student.section.name},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
                student_ad_obj = ad.GetObject("", f"LDAP://{student_dn}")

                print(4)

                student_ad_obj.sAMAccountName = username 
                student_ad_obj.userPrincipalName = username
            
            if first_name and first_name != student.first_name: 
                student_ad_obj.givenName = first_name
                student.first_name = first_name
            
            if last_name and last_name != student.last_name: 
                student_ad_obj.sn = last_name
                student.last_name = last_name

            if middle_initial and middle_initial != student.middle_initial and len(middle_initial) == 1 :
                student_ad_obj.initials = middle_initial.upper()
                student.middle_initial = middle_initial.upper()

            student_ad_obj.setInfo()
            student.save()
            counter += 1

        return Response({
            "status_message" : "Update is completed",
            "errors" : errors
        })

    except win32Exception as e: 
        already_exist = "0x80071392" in str(e)

        if already_exist : 
            error_message = " Username is already being used within the domain"

        return Response({"error_message" : error_message})

    except Exception as e:          
        error_code = "0x8007202f"
        password_error_code = "An invalid dn syntax has been specified"
        input_error_code = "A constraint violation occurred"

        if error_code in str(e): 
            error_message = "User might already exist or password format is incorrect"
        
        elif password_error_code in str(e): 
            error_message = "Error in updating username, username might already be in use within the domain"
        
        elif input_error_code in str(e): 
            error_message = "Error in updating student, please recheck your input"

        else :
            error_message = str(e)
        print(f"Failed to create user: {str(e)}")

        return Response({
            "error_message" : error_message
        }) 

