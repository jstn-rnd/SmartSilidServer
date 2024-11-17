import subprocess
import time
from django.http import HttpResponse
from wakeonlan import send_magic_packet
from django.shortcuts import render
from .models import RFID, Computer, Scan, Student, User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

def normalize_mac(mac_address):
    """Normalize MAC address to be without hyphens and lowercase."""
    return mac_address.replace('-', ':').lower()

def get_ip_from_mac(mac_address):
    """Retrieve the IP address associated with a MAC address using ARP."""
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_table = result.stdout
        
        # Normalize the MAC address to match the format in the ARP table
        normalized_mac = normalize_mac(mac_address)
        
        # Log ARP table for debugging
        print("ARP Table:")
        print(arp_table)
        
        for line in arp_table.splitlines():
            parts = line.split()
            if len(parts) >= 3 and normalize_mac(parts[1]) == normalized_mac:
                ip_address = parts[0]
                print(f"Found IP address {ip_address} for MAC address {mac_address}")
                return ip_address
    except Exception as e:
        print(f"Error while retrieving IP from MAC: {e}")
    
    print(f"MAC address {mac_address} not found in ARP table.")
    return None

#authentication
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wake_computers(request):

    selected_computers = request.data.get('computers')
    
    if len(selected_computers) < 1:
        return Response({ "status_message" : "Please select at least 1 computer."})
    
    try:
        for computer in selected_computers:
            student_mac = Computer.objects.filter(computer_name=computer).first()
            if student_mac:
                print(student_mac.computer_name)
                normalized_mac = normalize_mac(student_mac.mac_address)
                send_magic_packet(normalized_mac)

        return Response({"status_message" : f"Sent magic packets to: {', '.join(selected_computers)}"})
    
    except Exception as e:
        return Response({"status_message" : f"Failed to send magic packets: {str(e)}"})

   
#authentication
@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def shutdown_computers(request):

    computers = request.data.get('computers')

    if not computers:
        return Response({ "status" : "No computers selected" })
    
    failed_computers = []
    
    for computer in computers:
        student_mac = Computer.objects.filter(computer_name=computer).first()
        print(computer)
        
        if not student_mac:
            failed_computers.append((computer, "MAC address not found"))
            continue
        
        original_mac_address = student_mac.mac_address
        ip_address = get_ip_from_mac(original_mac_address)

        if not ip_address:
            failed_computers.append((computer, f"IP address not found for MAC address {original_mac_address}"))
            continue
        
        try:
            # Log the command for debugging
            command = ['shutdown', '/s', '/f', '/t', '0', '/m', f'\\\\{ip_address}']
            print(f"Executing command: {' '.join(command)}")
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            
            # Capture and log output and errors
            if result.returncode != 0:
                failed_computers.append((computer, f"Failed to execute command. Error: {result.stderr.strip()}"))
            else:
                print(f"Shutdown command output: {result.stdout.strip()}")
            
        except Exception as e:
            failed_computers.append((computer, f"Exception occurred: {str(e)}"))
    
    if failed_computers:
        error_messages = "\n".join([f"Failed to shutdown {comp} (MAC: {Computer.objects.filter(computer_name=comp).first().mac_address}): {err}" for comp, err in failed_computers])
        response = f"Some shutdown commands failed:\n{error_messages}"
        return Response({"status message" : response})
    
    return Response({ "status_message" : "Shutdown commands sent successfully"})
    
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_computers(request): 
    computers = Computer.objects.all()

    response_json = []

    for computer in computers : 
        response_json.append({
            "computer_name" : computer.computer_name,
            "status" : computer.status, 
            "is_admin" : computer.is_admin
            })
    
    return Response({
        "status" : "Computers obtained succesfully", 
        "computers" : response_json
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_computer_admin(request): 
    computer_name = request.data.get('computer_name')

    if not computer_name:
        return Response({
            "status": "computer_name parameter is required."
        })

    admin_computer_exists = Computer.objects.filter(is_admin=1)
    
    for computer in admin_computer_exists: 
        print(computer.computer_name)
        computer.is_admin = 0
        computer.save()
    
    new_admin = Computer.objects.filter(computer_name = computer_name).first()
    new_admin.is_admin = 1
    new_admin.save()

    faculties = User.objects.all()

    for faculty in faculties: 
        scan = Scan.objects.filter(faculty = faculty).first()

        if not scan : 
            scan = Scan(
                faculty = faculty, 
                computer = new_admin
            )

        scan.computer = computer

    return Response({
        "status" : "Admin computer has been updated successfully", 
    })

@api_view(['POST'])
# @permission_classes([IsAuthenticated])
def bind_computer(request): 
    computer = request.data.get('computer')
    username = request.data.get('username', None)
    section = request.data.get('section')
    
    if not computer and not section:
        return Response({
          "status_message" : "Missing or invalid input"
        })
    
    computer_db = Computer.objects.filter(computer_name = computer).first()

    if not computer_db: 
        return Response({
            "status_message" : "Computer not found"
        })
    
    existing_scan = Scan.objects.filter(computer = computer_db, student__section__name = section).first()
    print("SECTION", section)
    # print("EXISTING SCAN", existing_scan.id)
    if not username and section and existing_scan: 
        existing_scan.computer = None
        existing_scan.save()

        return Response({
            "status_message" : "Computer is unassigned successfully"
        })
    

    user = Student.objects.filter(username = username).first()
    print(username)
    if not user: 
        return Response({
        "status_message" : "Student does not exist"
        })
        
    if existing_scan : 
        existing_scan.computer = None
        existing_scan.save()

    scan = Scan.objects.filter(student__username = username).first()

    if not scan: 
        scan = Scan(
            student = user, 
            computer = computer_db
        )

    if scan : 
        scan.computer = computer_db

    scan.save()

    return Response({
        "status_message" : "Computer was successfully binded to user"
    }) 



# def shutdown_computers(request):
#     if request.method == 'POST':
#         computers = request.POST.getlist('computers')
#         if not computers:
#             return HttpResponse("No computers selected.", status=400)
        
#         failed_computers = []
        
#         for computer in computers:
#             student_mac = Computer.objects.filter(computer_name=computer).first()
#             if not student_mac:
#                 failed_computers.append((computer, "MAC address not found"))
#                 continue
            
#             original_mac_address = student_mac.mac_address
#             ip_address = get_ip_from_mac(original_mac_address)
#             if not ip_address:
#                 failed_computers.append((computer, f"IP address not found for MAC address {original_mac_address}"))
#                 continue
            
#             try:
#                 # Log the command for debugging
#                 command = ['shutdown', '/s', '/f', '/t', '0', '/m', f'\\\\{ip_address}']
#                 print(f"Executing command: {' '.join(command)}")
#                 result = subprocess.run(command, capture_output=True, text=True, shell=True)
                
#                 # Capture and log output and errors
#                 if result.returncode != 0:
#                     failed_computers.append((computer, f"Failed to execute command. Error: {result.stderr.strip()}"))
#                 else:
#                     print(f"Shutdown command output: {result.stdout.strip()}")
                
#             except Exception as e:
#                 failed_computers.append((computer, f"Exception occurred: {str(e)}"))
        
#         if failed_computers:
#             error_messages = "\n".join([f"Failed to shutdown {comp} (MAC: {Computer.objects.filter(computer_name=comp).first().mac_address}): {err}" for comp, err in failed_computers])
#             return HttpResponse(f"Some shutdown commands failed:\n{error_messages}", status=500)
        
#         return HttpResponse("Shutdown commands sent successfully.")
    
#     return render(request, 'server_app/shutdown_computers.html', {'computers': Computer.objects.values_list('computer_name', flat=True)})



# def select_and_wake_computers(request):
#     if request.method == 'POST':
#         selected_computers = request.POST.getlist('computers')
        
#         if len(selected_computers) < 1:
#             return HttpResponse("Please select at least 1 computer.", status=400)
        
#         try:
#             for computer in selected_computers:
#                 student_mac = Computer.objects.filter(computer_name=computer).first()
#                 if student_mac:
#                     normalized_mac = normalize_mac(student_mac.mac_address)
#                     send_magic_packet(normalized_mac)
#             return HttpResponse(f"Sent magic packets to: {', '.join(selected_computers)}")
#         except Exception as e:
#             return HttpResponse(f"Failed to send magic packets: {str(e)}", status=500)

#     return render(request, 'server_app/select_and_wake.html', {'computers': Computer.objects.values_list('computer_name', flat=True)})

