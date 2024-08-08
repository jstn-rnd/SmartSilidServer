from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect, render

from django.shortcuts import render, redirect


from django.shortcuts import render, redirect



def index(request):
    return render(request, 'server_app/index.html')




from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Test, MacAddress
import json


@csrf_exempt
def check_rfid(request):
    if request.method == 'POST':
        RFID = request.POST.get('RFID')
        if RFID:
            try:
                # Check if RFID exists
                record = Test.objects.get(RFID=RFID)
                response = {
                    "status": "error",
                    "message": "RFID already exists in database",
                    "ID": record.id,
                    "RFID": record.RFID,
                    "Approve": record.approved
                }

                # Fetch MAC address
                mac_address = MacAddress.objects.filter(id=1).first()
                response['targetMacAddress'] = mac_address.mac_address if mac_address else "Not found"
            except Test.DoesNotExist:
                # RFID does not exist, insert into database
                record = Test.objects.create(RFID=RFID, approved=0)  # Adjust approved field as needed
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
            test.approved = approve_value
            test.save()
        except Test.DoesNotExist:
            pass
    return redirect('view_records')