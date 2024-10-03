
from django.shortcuts import render, redirect
import pyad
from django.http import HttpResponse
from .settings import get_ad_connection
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import User, Section, Student
from .configurations import AD_BASE_DN
import pythoncom
import win32com.client


def create_user_page(request): 
    return render(request, 'server_app/create_user.html')

#OU Creation 
# Hindi pa naayos yung type at section
#Lagyan ng admin rights yung mga nasa faculty

@api_view(['POST'])
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

            if username == None : 
                username = first_name + "." + last_name + "." + middle_initial
                  
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

                return Response({"status_message" : "User succesfully created"})
            else : 
                return Response({"status_message" : "Section does not exist"})
                    
        except Exception as e:
            print(f"Failed to create user: {str(e)}")
            return Response({"status_message" : f"Failed to create user:3 {str(e)}"})

    else:
        return Response({"status_message" : "Failed to connect to Active Directory"})


@api_view(['POST'])
def delete_student(request):
    username = request.data.get("username")
    student = Student.objects.filter(username = username).first()
    section = student.section.name
    
    if student : 
        try :     
            pythoncom.CoInitialize()
            parent_dn = f"OU={section},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            ad = win32com.client.Dispatch("ADsNameSpaces")
            ad_obj = ad.GetObject("", f"LDAP://{parent_dn}")
            user_object = ad_obj.Create("user", f"CN={username}") # HIndi dito nag ccreate, niloload lang ganun
            user_object.DeleteObject(0)

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
            "status_message" : f"User {username} does not exist"
        })

@api_view(['POST'])
def change_password_student(request): 
    username = request.data.get('username')
    student = Student.objects.filter(username = username).first()
    value = request.data.get('new_password')
    
    if student: 
        
        try :
            section = student.section.name
            pythoncom.CoInitialize()
            ad = win32com.client.Dispatch("ADsNameSpaces")
            user_dn = f"CN={username},OU={section},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
            user_ad_obj = ad.GetObject("", f"LDAP://{user_dn}")
            user_ad_obj.SetPassword(value)

            return Response({"status_message" : "Student password change succesful"})

        except Exception as e:
           
            return Response({
                "status_message" : "Student password change is unsuccesful",
                "error_message" : str(e)
                })

    else:
        return Response({"status_message" : "Student not found"})
    
@api_view(['POST'])
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
def get_all_students(request):

    result = []
    students = Student.objects.all()

    for student in students:
        info = {
            "id" : student.id,
            "first_name" : student.first_name, 
            "last_name" : student.last_name, 
            "middle_initial" : student.middle_initial,
            "section" : student.section.name
        }
        result.append(info)
    
    return Response({
        "status_message" : "User obtained succesfully",
        "students" : result 
    })

