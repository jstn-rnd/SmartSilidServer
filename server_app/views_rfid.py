from datetime import timezone

from django.shortcuts import render, redirect

from django.views.decorators.csrf import csrf_exempt

from django.views.decorators.http import require_POST

from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Schedule, RfidLogs, User, RFID, RFID
from .forms import ScheduleForm

from rest_framework.response import Response
from rest_framework.decorators import api_view
from datetime import datetime 




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

def update_rfids_approval(schedule):
    local_tz = pytz.timezone('Asia/Manila')
    local_time = timezone.now().astimezone(local_tz)
    current_time = local_time.time()
    current_weekday = local_time.strftime('%a')

    faculty = schedule.faculty

    if schedule.start_time <= current_time <= schedule.end_time and current_weekday in schedule.get_weekdays_display():
            
        for rfid in faculty.rfids.all(): 
            if rfid.approved == 0:  
                print(rfid.rfid)
                rfid.approved = 1
                rfid.save()
            return schedule.id
   
    else:
        for rfid in faculty.rfids.all(): 
            rfid.approved = 0
            rfid.save()
           
    
    return -1


############################################################################
############################################################################
#API


@api_view(['POST'])
def check_rfid(request):
    RFID_input = request.data.get('RFID')

    if RFID_input:
        schedules = Schedule.objects.all()
        for schedule in schedules:
            schedule_id = update_rfids_approval(schedule)

        try : 

            record = RFID.objects.get(rfid=RFID_input)
            response = {
                "status": "success",
                "message": "RFID exists",
                "ID": record.id,
                "RFID": record.rfid,
                "Approve": record.approved  # This will be based on the latest schedule check or manual update
            }

            print(schedule_id)

            if schedule_id >= 0: 
                
                schedule = Schedule.objects.filter(id = schedule_id).first()
                logs = RfidLogs(
                    schedule = schedule, 
                    start_time = datetime.now().strftime("%H:%M:%S")
                )
                logs.save()
        
        except RFID.DoesNotExist:

            record = RFID.objects.create(rfid=RFID_input, approved=0)  # Default to 0 (denied)
            response = {
                "status": "success",
                "message": "RFID added successfully",
                "ID": record.id,
                "RFID": record.rfid,
                "Approve": record.approved
            }

    else : 
        response = {"status": "error", "message": "No RFID received from ESP32"}
    
    return Response(response)

#authentication
@api_view(['POST'])
def bind_rfid(request): 
    rfid = request.data.get('RFID')
    username = request.data.get('username')

    rfid_object = RFID.objects.filter(rfid = rfid).first()
    user = User.objects.filter(username = username).first()

    if rfid_object and user : 
        rfid_object.faculty = user
        rfid_object.save()

        return Response({
            "status_message" : "RFID was successfully binded to user"
        }) 
    else: 
        return Response({
            "status_message" : "Missing or invalid input"
        })
    


