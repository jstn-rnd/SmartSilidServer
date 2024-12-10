# import pandas as pd
# from django.shortcuts import render, redirect
# from django.contrib import messages
# from .models import Student, Section

# def upload_students(request):
#     if request.method == 'POST' and request.FILES['file']:
#         excel_file = request.FILES['file']
#         try:
#             df = pd.read_excel(excel_file)
            
#             for index, row in df.iterrows():
#                 first_name = row['Firstname']
#                 middle_initial = row['MiddleInitial']
#                 last_name = row['Lastname']
#                 username = row['Username']
#                 section_name = row['Section']
#                 password = row['Password']
#                 confirm_password = row['ConfirmPassword']
                
#                 if password != confirm_password:
#                     messages.error(request, f"Passwords do not match for {username}. Skipping.")
#                     continue

#                 # Check if the section exists
#                 try:
#                     section = Section.objects.get(name=section_name)
#                 except Section.DoesNotExist:
#                     messages.error(request, f"Section '{section_name}' does not exist for {username}. Skipping.")
#                     continue

#                 # Check if the username already exists
#                 if Student.objects.filter(username=username).exists():
#                     messages.error(request, f"Username '{username}' already exists. Skipping.")
#                     continue
                
#                 # Create the student
#                 Student.objects.create(
#                     first_name=first_name,
#                     middle_initial=middle_initial,
#                     last_name=last_name,
#                     username=username,
#                     section=section
#                 )

#             messages.success(request, "Students have been uploaded successfully!")
#             return redirect('upload_students')  # Adjust the redirect as needed

#         except Exception as e:
#             messages.error(request, f"Error processing the file: {e}")
    
#     return render(request, 'server_app/upload_students.html')


# import pandas as pd
# from rest_framework.response import Response
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from .models import Student, Section

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def upload_students(request):
#     if 'file' not in request.FILES:
#         return Response({"error": "No file provided."}, status=400)

#     excel_file = request.FILES['file']
#     try:
#         df = pd.read_excel(excel_file)
#         errors = []

#         for index, row in df.iterrows():
#             first_name = row.get('Firstname')
#             middle_initial = row.get('MiddleInitial')
#             last_name = row.get('Lastname')
#             username = row.get('Username')
#             section_name = row.get('Section')
#             password = row.get('Password')
#             confirm_password = row.get('ConfirmPassword')

#             # Validate password match
#             if password != confirm_password:
#                 errors.append(f"Passwords do not match for {username}. Skipping.")
#                 continue

#             # Validate section existence
#             try:
#                 section = Section.objects.get(name=section_name)
#             except Section.DoesNotExist:
#                 errors.append(f"Section '{section_name}' does not exist for {username}. Skipping.")
#                 continue

#             # Validate if the username already exists
#             if Student.objects.filter(username=username).exists():
#                 errors.append(f"Username '{username}' already exists. Skipping.")
#                 continue

#             # Create the student
#             Student.objects.create(
#                 first_name=first_name,
#                 middle_initial=middle_initial,
#                 last_name=last_name,
#                 username=username,
#                 section=section
#             )

#         if errors:
#             return Response({"errors": errors}, status=207)  # 207: Multi-Status for partial success
#         return Response({"message": "Students have been uploaded successfully!"}, status=201)

#     except Exception as e:
#         return Response({"error": f"Error processing the file: {str(e)}"}, status=500)


import re
import pandas as pd
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from server_app.configurations import AD_BASE_DN
from server_app.settings import get_ad_connection
from .models import Student, Section, User
import pyad.aduser
import pyad.adcontainer
from pyad.pyadexceptions import win32Exception

# Regular expression for password validation
PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,}$'

def is_valid_password(password):
    return re.match(PASSWORD_REGEX, password) is not None

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_students_batch(request):
    if get_ad_connection():
        try:
            # Ensure a file is provided
            if 'file' not in request.FILES:
                return Response({"status_message": "No file provided"}, status=400)

            excel_file = request.FILES['file']
            df = pd.read_excel(excel_file)
            errors = []
            success_count = 0

            for index, row in df.iterrows():
                username = row.get('Username', None)
                password = row.get('Password')
                confirm_password = row.get('ConfirmPassword')
                first_name = row.get('Firstname')
                last_name = row.get('Lastname')
                middle_initial = row.get('MiddleInitial', '')
                section_name = row.get('Section', None)

                print(username)
                print(1)

                # Validate required fields
                if not password or not confirm_password or not username or not first_name or not last_name:
                    print(2)
                    errors.append({
                        "username" : username,
                        "error" : "Missing required fields. Skipping."})
                    continue

                if password != confirm_password:
                    print(3)
                    errors.append({
                        "username" : username,
                        "error" : "Passwords do not match."})
                    continue

                # Validate password complexity
                if not is_valid_password(password):
                    print(4)
                    errors.append({
                        "username" : username,
                        "error" : "Password does not meet complexity requirements. It must be at least 8 characters long, include 1 uppercase letter, and 1 number. Skipping."})
                    continue


                # Validate section existence
                section_object = Section.objects.filter(name=section_name).first()
                if not section_object:
                    print(5)
                    errors.append({
                        "username" : username,
                        "error" : "Section '{section_name}' does not exist "})
                    continue

                try:
                    # Prepare attributes for AD user creation
                    optional_attributes = {
                        "givenName": first_name,
                        "sn": last_name,
                        "initials": middle_initial
                    }

                    # Create AD user
                    container_object = pyad.adcontainer.ADContainer.from_dn(
                        f"OU={section_name},OU=Student,OU=SmartSilid-Users,{AD_BASE_DN}"
                    )
                    new_user = pyad.aduser.ADUser.create(
                        username,
                        container_object,
                        password=password,
                        optional_attributes=optional_attributes
                    )

                    # Save the student in the Django model if AD creation is successful
                    if new_user:
                        student = Student(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            middle_initial=middle_initial,
                            section=section_object
                        )
                        student.save()
                        success_count += 1
                    else:
                        errors.append({
                            "username" : username, 
                            "error" : "Failed to create AD user"
                        })

                except win32Exception as e: 
                    already_exist = "0x80071392" in str(e)
                    password_history_error = "0x800708c5" in str(e)

                    if password_history_error:
                        user = pyad.aduser.ADUser.from_cn(username)
                        user.delete()
                        error_message = "Password error! Ensure that password is not similar to username or past password"

                    if already_exist : 
                        error_message = " Username is already being used within the domain"

                    else : 
                        error_message = str(e)
                    
                    print(username)
                    print(str(e))
                    print(6)

                    errors.append({
                        "username": username,
                        "error": error_message
                    })

                except Exception as e:
                    print(7)
                    errors.append({
                        "username" : username, 
                        "error" : str(e)
                    })

            status_message = {
                "success_count" : success_count,
                "failed_entries" : errors
            }
            return Response({
                "status_message": status_message,
            }, status=207 if errors else 201)

        except Exception as e:
            return Response({"status_message": f"Error processing the file: {str(e)}"}, status=500)

    else:
        return Response({"status_message": "Failed to connect to Active Directory"}, status=500)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_faculty_batch(request):
    faculty_list = request.data.get('faculty_list', [])

    if not faculty_list or not isinstance(faculty_list, list):
        return Response({"status_message": "Invalid input, expected a list of faculty data."}, status=400)

    # Possible types for faculty
    choices = ["admin", "faculty"]
    failed_entries = []
    success_count = 0

    # Iterate through each faculty entry in the list
    for faculty_data in faculty_list:
        username = faculty_data.get('username', None)
        password = faculty_data.get('password')
        first_name = faculty_data.get('first_name')
        last_name = faculty_data.get('last_name')
        middle_initial = faculty_data.get("middle_initial", '')
        type = faculty_data.get("type", None)

        optional_attributes = {
            "givenName": first_name,
            "sn": last_name,
            "initials": middle_initial
        }

        # Validate type
        if type not in choices:
            failed_entries.append({
                "username": username,
                "error": "Invalid type"
            })
            continue

        # Generate default username if not provided
        if username is None:
            username = f"{first_name}.{last_name}.{middle_initial}"

        # Check username length
        if len(username) > 20:
            failed_entries.append({
                "username": username,
                "error": "Username is too long"
            })
            continue

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            failed_entries.append({
                "username": username,
                "error": "User already exists"
            })
            continue

        # Validate password (minimum 8 characters, at least one capital letter, and one number)
        if not validate_password(password):
            failed_entries.append({
                "username": username,
                "error": "Password does not meet complexity requirements"
            })
            continue

        # Create the User record and AD user if the AD connection is successful
        try:
            if get_ad_connection():
                faculty_db = User(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    middle_initial=middle_initial,
                    type=type,
                    hasWindows = 1
                )
                faculty_db.set_password(password)

                # Create AD user
                container_object = pyad.adcontainer.ADContainer.from_dn(f"OU=Faculty,OU=SmartSilid-Users,{AD_BASE_DN}")
                new_faculty = pyad.aduser.ADUser.create(
                    username,
                    container_object,
                    password=password,
                    optional_attributes=optional_attributes
                )

                # Save the User record in the database if the AD user creation is successful
                if new_faculty:
                    admin_group = pyad.adgroup.ADGroup.from_cn("Domain Admins")
                    new_faculty.add_to_group(admin_group)

                    faculty_db.save()
                    success_count += 1
                else:
                    failed_entries.append({
                        "username": username,
                        "error": "Failed to create AD user"
                    })
            else:
                failed_entries.append({
                    "username": username,
                    "error": "Failed to connect to Active Directory"
                })

        except win32Exception as e: 
            already_exist = "0x80071392" in str(e)
            password_history_error = "0x800708c5" in str(e)

            if password_history_error:
                user = pyad.aduser.ADUser.from_cn(username)
                user.delete()
                error_message = "Password error! Ensure that password is not similar to username or past password"

            if already_exist : 
                error_message = " Username is already being used within the domain"

            failed_entries.append({
                "username": username,
                "error": error_message
            })

        except Exception as e:
            failed_entries.append({
                "username": username,
                "error": str(e)
            })


    # Return a summary of the batch operation
    status_message = {
        "success_count": success_count,
        "failed_entries": failed_entries,
    }

    if failed_entries:
        return Response({"status_message": status_message})
    return Response({"status_message": status_message}, status=201)

def validate_password(password):
    """
    Validate that the password meets the complexity requirements:
    - At least 8 characters
    - Contains at least one uppercase letter
    - Contains at least one number
    """
    import re
    if (len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[0-9]', password)):
        return True
    return False
