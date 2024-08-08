# views.py
from django.http import HttpResponse
from wakeonlan import send_magic_packet
from django.shortcuts import render

# Predefined list of computers and their MAC addresses
COMPUTERS = {
    'Computer 1': '00:11:22:33:44:55',
    'Computer 2': '66:77:88:99:AA:BB',
    'Computer 3': 'CC:DD:EE:FF:00:11',
    'Computer 4': '22:33:44:55:66:77',
}

def select_and_wake_computers(request):
    if request.method == 'POST':
        selected_computers = request.POST.getlist('computers')
        
        if len(selected_computers) < 2:
            return HttpResponse("Please select at least 2 computers.", status=400)
        
        try:
            # Send magic packets to the selected computers
            for computer in selected_computers:
                mac_address = COMPUTERS.get(computer)
                if mac_address:
                    send_magic_packet(mac_address)
            return HttpResponse(f"Sent magic packets to: {', '.join(selected_computers)}")
        except Exception as e:
            return HttpResponse(f"Failed to send magic packets: {str(e)}", status=500)

    # Render a form to select computers
    return render(request, 'select_and_wake.html', {'computers': COMPUTERS.keys()})
