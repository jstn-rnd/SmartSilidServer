from datetime import timezone
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect, render
from .models import Schedule, Test, MacAddress
from django.shortcuts import render, redirect


from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .models import Schedule, Test, MacAddress
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def index(request):
    return render(request, 'server_app/index.html')




from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Test, MacAddress, Schedule
from .forms import ScheduleForm
import json


@csrf_exempt
def check_rfid(request):
    
    if request.method == 'POST':
        RFID = request.POST.get('RFID')

        if RFID:
            # Update the RFID approval status based on the schedule before checking
            schedules = Schedule.objects.all()
            for schedule in schedules:
                update_rfids_approval(schedule)  # Refresh approval statuses based on the schedule

            try:
                # Check if RFID exists
                record = Test.objects.get(RFID=RFID)
                response = {
                    "status": "success",
                    "message": "RFID exists",
                    "ID": record.id,
                    "RFID": record.RFID,
                    "Approve": record.approved  # This will be based on the latest schedule check or manual update
                }
                
                # Fetch MAC address
                mac_address = MacAddress.objects.filter(id=1).first()
                response['targetMacAddress'] = mac_address.mac_address if mac_address else "Not found"
            except Test.DoesNotExist:
                # RFID does not exist, insert into database
                record = Test.objects.create(RFID=RFID, approved=0)  # Default to 0 (denied)
                response = {
                    "status": "success",
                    "message": "RFID added successfully",
                    "ID": record.id,
                    "RFID": record.RFID,
                    "Approve": record.approved
                }

                # Fetch MAC address
                mac_address = MacAddress.objects.filter(id=1).first()
                response['targetMacAddress'] = mac_address.mac_address if mac_address else "Not found"
        else:
            response = {"status": "error", "message": "No RFID received from ESP32"}

        return JsonResponse(response)
    else:
        return JsonResponse({"status": "error", "message": "Invalid request method"})


def view_records(request):
    
    tests = Test.objects.all()
    mac_addresses = MacAddress.objects.all()
    
    context = {
        'tests': tests,
        'mac_addresses': mac_addresses,
    }
    
    return render(request, 'server_app/view_records.html', context)


from django.shortcuts import redirect
from django.views.decorators.http import require_POST

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
from .models import Schedule, Test
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
    rfids = Test.objects.values_list('RFID', flat=True)
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

    for rfid in schedule.rfids.all():
        # Log schedule details
        print(f"Processing RFID: {rfid.RFID}")
        print(f"Schedule details: start_time={schedule.start_time}, end_time={schedule.end_time}, weekdays={schedule.weekdays}")

        # If it's within the schedule time and manual approval has not overridden it
        if schedule.start_time <= current_time <= schedule.end_time and current_weekday in schedule.get_weekdays_display():
            # Only update if RFID has not been manually set
            if rfid.approved == 0:  # Only change approval if it's not manually set to 1
                rfid.approved = 1
                print(f"RFID {rfid.RFID} approved during schedule")
        else:
            # Outside the schedule window, always revoke approval
            rfid.approved = 0
            print(f"RFID {rfid.RFID} not approved outside schedule")
        
        # Save RFID approval status
        rfid.save()
        print(f"RFID {rfid.RFID} approval status saved: {rfid.approved}")
