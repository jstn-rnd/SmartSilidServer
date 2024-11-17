from datetime import timezone
import subprocess
import time

from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_POST

from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from wakeonlan import send_magic_packet

from server_app.views_wol import get_ip_from_mac, normalize_mac
from .models import Computer, Schedule, RfidLogs, ClassInstance, User, RFID, User, Scan, Student
from .forms import ScheduleForm

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime 
from django.utils.dateparse import parse_date
from datetime import date
import math




# @csrf_exempt
# def check_rfid(request):
    
#     if request.method == 'POST':
#         RFID_input = request.POST.get('RFID')
#         print(RFID_input)

#         if RFID_input:
#             # Update the RFID approval status based on the schedule before checking
#             schedules = Schedule.objects.all()
#             for schedule in schedules:
#                 update_rfids_approval(schedule)  # Refresh approval statuses based on the schedule

#             try:
#                 # Check if RFID exists
#                 record = RFID.objects.get(RFID=RFID_input)
#                 response = {
#                     "status": "success",
#                     "message": "RFID exists",
#                     "ID": record.id,
#                     "RFID": record.RFID,
#                     "Approve": record.approved  # This will be based on the latest schedule check or manual update
#                 }
                
               
#             except RFID.DoesNotExist:
#                 # RFID does not exist, insert into database
#                 record = RFID.objects.create(RFID=RFID_input, approved=0)  # Default to 0 (denied)
#                 response = {
#                     "status": "success",
#                     "message": "RFID added successfully",
#                     "ID": record.id,
#                     "RFID": record.RFID,
#                     "Approve": record.approved
#                 }

#         else:
#             response = {"status": "error", "message": "No RFID received from ESP32"}

#         return JsonResponse(response)
#     else:
#         return JsonResponse({"status": "error", "message": "Invalid request method"})


def view_records(request):
    
    rfid = RFID.objects.all()
    
    context = {
        'tests': rfid,
    }
    
    return render(request, 'server_app/view_records.html', context)


@require_POST
def update_approve_status(request):
    test_id = request.POST.get('test_id')
    if test_id:
        try:
            test = Test.objects.get(id=test_id)
            approve_value = int(request.POST.get(f'approve_{test_id}', 0))
            test.approved = approve_value  # Manually approve or deny
            test.save()
        except Test.DoesNotExist:
            pass
    return redirect('view_records')



from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Schedule
from .forms import ScheduleForm
import pytz

def manage_schedules(request):
    if request.method == 'POST':
        
        print("POST request received")
        schedule_form = ScheduleForm(request.POST)
        if schedule_form.is_valid():
            print("Form is valid")
            schedule = schedule_form.save()
            print(f"Schedule saved: {schedule}")
            update_rfids_approval(schedule)  # Call the function to update RFIDs approval
            print("RFID approval update called")
            return redirect('manage_schedules')
        else:
            print("Form is not valid")
    else:
        schedule_form = ScheduleForm()

    schedules = Schedule.objects.all()
    rfids = RFID.objects.values_list('RFID', flat=True)
    return render(request, 'server_app/manage_schedules.html', {
        'schedule_form': schedule_form,
        'schedules': schedules,
        'rfids': rfids,
    })

def update_rfids_approval(schedule, rfid):
    local_tz = pytz.timezone('Asia/Manila')
    local_time = timezone.now().astimezone(local_tz)
    current_time = local_time.time()
    current_weekday = local_time.strftime('%a')

    faculty = schedule.faculty
    if schedule.start_time <= current_time <= schedule.end_time and current_weekday in schedule.get_weekdays_display():

        for rfid_instance in faculty.rfids.all(): 
            
            if rfid_instance.rfid == rfid:  
                rfid_instance.approved = 1
                rfid_instance.save()
                return schedule.id
            
            else : 
                print("Not match")
            
    else:
        for rfid in faculty.rfids.all(): 
            rfid.approved = 0
            rfid.save()
            #print(f"rfid : {rfid}, approve : {rfid.approved}")
           
    
    return -1


############################################################################
############################################################################
#API


@api_view(['POST'])
def check_rfid(request):
    RFID_input = request.data.get('RFID')
    local_tz = pytz.timezone('Asia/Manila')
    local_time = timezone.now().astimezone(local_tz)
    current_time = local_time.time()
    current_weekday = local_time.strftime('%a')

    print(RFID_input)

    if not RFID_input:
           return Response({
            "status_message" : "Invalid Input"
        })

    try : 
        rfid = RFID.objects.get(rfid=RFID_input)
        scan = Scan.objects.filter(rfid=rfid).first()

        if not scan : 
            rfid.approved = 0
            rfid.save()

            response = {
                "status": "success",
                "message": "RFID exists",
                "ID": rfid.id,
                "RFID": rfid.rfid,
                "Approve": rfid.approved  # This will be based on the latest schedule check or manual update
            }   

            return Response(response)     

        if scan.faculty != None: 
            faculty = scan.faculty
            schedule_id = -1 
            schedules = Schedule.objects.filter(faculty = faculty)

            for schedule in schedules:
                if schedule.start_time <= current_time <= schedule.end_time and current_weekday in schedule.get_weekdays_display():
                    rfid.approved = 1
                    schedule_id = schedule.id 
                    rfid.save()
                    break

                else : 
                    rfid.approved = 0        
                    rfid.save()

            if schedule_id >= 0: 
                schedule = Schedule.objects.filter(id = schedule_id).first()

                # class_instance = ClassInstance.objects.filter(schedule = schedule, date = datetime.today().date()).first()

                # if not class_instance: 
                #     class_instance = ClassInstance(
                #         schedule = schedule, 
                #         date = datetime.today().date(),
                #     )

                #     class_instance.save()

                # logs = RfidLogs(
                #     class_instance = class_instance, 
                #     faculty = datetime.today().date(), 
                #     scan_time = datetime.now().strftime("%H:%M:%S"), 
                # )

                # logs.save()

                print("Check")

                logs = RfidLogs(
                    schedule = schedule, 
                    user = scan.faculty.username, 
                    date = datetime.today().date(), 
                    scan_time = datetime.now().strftime("%H:%M:%S"), 
                )

                logs.save()

                if not scan.computer : 
                    print("Error")

                if scan.computer :
                     
                    normalized = normalize_mac(scan.computer.mac_address)
                    print(normalized)

                    send_magic_packet(normalized)
                    
                    time.sleep(20)

                    ip_address = get_ip_from_mac(normalize_mac)

                    subprocess.Popen(["mstsc", f"/v:{ip_address}"])      
                    
                
        elif scan.student != None: 
            student = scan.student
            section = student.section
            schedule_id = -1

            schedules = Schedule.objects.filter(section = section)

            for schedule in schedules:
                print(schedule.subject)

                if schedule.start_time <= current_time <= schedule.end_time and current_weekday in schedule.get_weekdays_display():
                    rfid.approved = 1
                    schedule_id = schedule.id 
                    print(f"#####{rfid.approved}")
                    rfid.save()
                    break

                else : 
                    print("%%%%%%%%%%%%%%%%%%")
                    rfid.approved = 0        
                    rfid.save()
            
            if schedule_id >= 0: 
                schedule = Schedule.objects.filter(id = schedule_id).first()
                
                logs = RfidLogs(
                    schedule = schedule, 
                    user = scan.student.username, 
                    date = datetime.today().date(), 
                    scan_time = datetime.now().strftime("%H:%M:%S"), 
                )

                logs.save()

                # class_instance = ClassInstance.objects.filter(schedule = schedule, date = datetime.today().date()).first()

                # if not class_instance: 
                #     class_instance = ClassInstance(
                #         schedule = schedule, 
                #         date = datetime.today().date(),
                #     )

                #     class_instance.save()

                # logs = RfidLogs(
                #     class_instance = class_instance, 
                #     student = scan.student, 
                #     scan_time = datetime.now().strftime("%H:%M:%S"), 
                # )

                # logs.save()
        
        print(f"RFID {rfid.rfid}")
        print(f"RFID Approve : {rfid.approved}")

        response = {
            "status": "success",
            "message": "RFID exists",
            "ID": rfid.id,
            "RFID": rfid.rfid,
            "Approve": rfid.approved  # This will be based on the latest schedule check or manual update
        }          
        

        
    except RFID.DoesNotExist:

        record = RFID.objects.create(rfid=RFID_input, approved=0)  # Default to 0 (denied)
        response = {
            "status": "success",
            "message": "RFID added successfully",
            "ID": record.id,
            "RFID": record.rfid,
            "Approve": record.approved
        }

    return Response(response)

# ### VERSION 1 
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def bind_rfid(request):  
#     rfid = request.data.get('rfid')
#     username = request.data.get('username')
#     print(1)
#     print(rfid)
#     print(username)

#     if not rfid:
#         print(2)
#         return Response({
#             "status_message" : "Missing or invalid input"
#         })
    
#     rfid_object = RFID.objects.filter(rfid = rfid).first()
#     user = User.objects.filter(username = username).first()

#     if not rfid_object: 
#         print(3)
#         return Response({
#             "status_message" : "Missing or invalid input"
#         })

#     if user : 
#         rfid_object.faculty = user
#         rfid_object.save()

#         print("Ok")
#         return Response({
#             "status_message" : "RFID was successfully binded to user"
#         }) 

    
#     print("Not ok")
#     rfid_object.faculty = None 
#     rfid_object.save()

#     return Response({
#         "status_message" : "RFID was successfully unbinded to user"
#     }) 


# VERSION 2 
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def bind_rfid(request):  
    rfid = request.data.get('rfid')
    username = request.data.get('username', None)
    type = request.data.get('type', None)
    
    if not rfid:
        return Response({
          "status_message" : "Missing or invalid input"
        })
    
    rfid_object = RFID.objects.filter(rfid = rfid).first()

    if not rfid_object: 
        return Response({
            "status_message" : "Missing or invalid input"
        })
    
    scan = Scan.objects.filter(rfid = rfid_object).first()
    
    if scan: 
        scan.rfid = None
        scan.save()

        return Response({
            "status_message" : "Rfid is already unassigned"
        })
    
    if type == "student" :
        user = Student.objects.filter(username = username).first()

        if not user: 
            return Response({
            "status_message" : "Student does not exist"
            })
        
        scan = Scan.objects.filter(student__username = username).first()

        if not scan: 
            scan = Scan(
                student = user, 
                rfid = rfid_object
            )

        if scan : 
            scan.rfid = rfid_object

        scan.save()

    if type == "faculty":
        user = User.objects.filter(username = username).first()

        if not user: 
            return Response({
            "status_message" : "Faculty does not exist"
            })
        
        scan = Scan.objects.filter(faculty__username = username).first()

        if not scan: 
            scan = Scan(
                faculty = user, 
                rfid = rfid_object
            )

        if scan : 
            scan.rfid = rfid_object

        scan.save()

    return Response({
        "status_message" : "RFID was successfully binded to user"
    }) 
    
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_all_rfid(request):

    rfids = RFID.objects.all()
    
    response = []
    for rfid in rfids: 
        response.append(rfid.rfid)

    return Response({
        "status_message" : "RFID successfully retrieved",
        "rfids" : response
    }) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_logs_rfid(request): 
    pagination = request.data.get("pagination", None)
    start_date = request.data.get("start_date", None)
    end_date = request.data.get("end_date", None)
    subject = request.data.get("subject", None)
    user = request.data.get("username", None)
    section = request.data.get("section", None)

    if not start_date and not end_date :
        start_date_params = date(1, 1, 1)
        end_date_params = date(9999, 12, 31)

    elif not start_date:
        start_date_params = date(1, 1, 1)
        end_date_params = parse_date(end_date) 

    elif not end_date :
        start_date_params = parse_date(start_date)
        end_date_params = date(9999, 12, 31)

    else :
        start_date_params = parse_date(start_date)
        end_date_params = parse_date(end_date) 

    if not pagination: 
        pagination = 1
    
    pagination = float(pagination)
    
    logs = []
    
    items = int(pagination * 50) 
    
    filters = {
    'date__range': (start_date_params, end_date_params)
    }

    if subject:
        filters['schedule__subject__icontains'] = subject

    if user:
        filters['user'] = user

    if section:
        filters['schedule__section__name'] = section

    logs = RfidLogs.objects.filter(**filters).order_by("-date", "-scan_time")[:items * 2]

    if pagination > 1 :
        excluded = items - 1 - 50
    else : 
        excluded = -1
    
    json_response = []
    for i in range(items):
        if i > excluded and i < len(logs):
            data = {
                "id" : logs[i].id,
                "username" : logs[i].user,
                "subject" : logs[i].schedule.subject,
                "section" : logs[i].schedule.section.name,
                "date" : logs[i].date,
                "start_time" : logs[i].scan_time,
            }
            json_response.append(data)
    
    length = len(logs)
    pagination_length = length / 50

    if pagination_length % 1 != 0:
        pagination_length = math.floor(pagination_length)
        pagination_length += 1  

           
    return Response({
        "status_message" : "Logs obtained succesfully",
        "logs" : json_response,
        "pagination_length" : pagination_length
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_rfid(request): 
    rfid = request.data.get("rfid")

    if not rfid:
        return Response({
            "status_message" : "Rfid is required"
        })    
    
    rfid = RFID.objects.filter(rfid=rfid)

    if not rfid: 
        return Response({
            "status_message" : "RFID not found"
        })
    
    rfid.delete()

    return Response({
        "status_message" : "RFID deleted successfully"
    })

