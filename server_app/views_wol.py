import subprocess
import time
from django.http import HttpResponse
from wakeonlan import send_magic_packet
from django.shortcuts import render
from .models import RFID, Computer, Scan, Section, Student, User
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from server_app.Utils.computer_utls import change_computer_name


def normalize_mac(mac_address):
    """Normalize MAC address to be without hyphens and lowercase."""
    return mac_address.replace('-', ':').lower()

def get_ip_from_mac(mac_address):
    """Retrieve the IP address associated with a MAC address using ARP."""
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_table = result.stdout
        print(arp_table)
        # Normalize the MAC address to match the format in the ARP table
        normalized_mac = normalize_mac(mac_address)
        
        for line in arp_table.splitlines():
            parts = line.split()
            if len(parts) >= 3 and normalize_mac(parts[1]) == normalized_mac:
                ip_address = parts[0]
                print(f"MAC address {mac_address} found in ARP table.")
                return ip_address
    except Exception as e:
        print(f"Error while retrieving IP from MAC: {e}")
    
    print(f"MAC address {mac_address} not found in ARP table.")
    return None


def arp_for_state(computers): 
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        arp_table = result.stdout
        print(arp_table)

        active_computers = []
        inactive_computers = []
        
        for computer in computers: 
            normalized_mac = normalize_mac(computer.mac_address)
            found = False
        
            for line in arp_table.splitlines():
                parts = line.split()
                if len(parts) >= 3 and normalize_mac(parts[1]) == normalized_mac:
                    active_computers.append(computer.computer_name)
                    found = True
                    break    
                
            if found != True : 
                inactive_computers.append(computer.computer_name)

        response = {
            "active" : active_computers,
            "inactive" : inactive_computers
        }

        return response
    
    except Exception as e:
        print(f"Error while retrieving IP from MAC: {e}")
        return None
    

def reset_arp(): 
    try : 
        result = subprocess.run(["ipconfig"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "Default Gateway" in line:
                gateway =  line.split(":")[1].strip()
                gateway = gateway.strip()
                print(f"ping {gateway}")
                result = subprocess.run(['ping', '{gateway}', '-n', 1], capture_output=True, text=True)
                print(result)

        return None
    except Exception as e : 
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
                print(student_mac.mac_address)
                normalized_mac = normalize_mac(student_mac.mac_address)
                value = send_magic_packet(normalized_mac)
                print(value)

        return Response({"status_message" : f"Sent magic packets to: {', '.join(selected_computers)}"})
    
    except Exception as e:
        print("Error")
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
    
    time.sleep(30)

    for computer in computers : 

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
        
        command = ['arp', '-d', ip_address]
        print(f"Executing command: {' '.join(command)}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"arp remove result {result.returncode}")
        print(result.stdout)
        print(result.stderr)

        is_ip_still_found = get_ip_from_mac(original_mac_address)
        print(is_ip_still_found)

    
    if failed_computers:
        error_messages = "\n".join([f"Failed to shutdown {comp} (MAC: {Computer.objects.filter(computer_name=comp).first().mac_address}): {err}" for comp, err in failed_computers])
        response = f"Some shutdown commands failed:\n{error_messages}"
        return Response({"status message" : response})
    
    return Response({ "status_message" : "Shutdown commands sent successfully"})

    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_computers(request): 

    reset_arp()

    computers = Computer.objects.all()
    computers_with_state = arp_for_state(computers)
    active_computers = computers_with_state["active"]
    inactive_computers = computers_with_state["inactive"]

    response_json = []

    for computer in computers : 

        if computer.computer_name in active_computers: 
            computer.status = 1
            computer.save()

        elif computer.computer_name in inactive_computers: 
            computer.status = 0
            computer.save()

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
    computer_name = request.data.get('computer_name', None)

    admin_computer_exists = Computer.objects.filter(is_admin=1)
    
    for computer in admin_computer_exists: 
        print(computer.computer_name)
        computer.is_admin = 0
        computer.save()

    if not computer_name: 
        new_admin = None
    
    else : 
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
        "status_message" : "Admin computer has been updated successfully", 
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_all_computer(request): 
    section_name = request.data.get("section_name")

    if not section_name : 
        return Response({
            "status_message" : "Invalid or missing input"
        })
    
    section = Section.objects.filter(name = section_name).first()

    if not section : 
        return Response({
            "status_message" : "Section not found"
        })

    students = Student.objects.filter(section=section).order_by('last_name', 'first_name', 'middle_initial')
    
    scans_list = []
    for student in students:
        scan = Scan.objects.filter(student = student).first()

        if scan : 
            scans_list.append(scan)

    all_computers = Computer.objects.all().order_by('computer_name') 

    used_computers = []
    for scan in scans_list:
        if scan.computer not in used_computers:
            used_computers.append(scan.computer)

    

    available_computers = []
    for computer in all_computers:
        if computer not in used_computers:
            available_computers.append(computer)

    counter = 0
    for student in students : 
        scan = Scan.objects.filter(student = student).first()
        if not scan: 
            scan = Scan(
                student = student
            )
            scan.save()
        if not scan.computer: 
            try : 
                scan.computer = available_computers[counter]
                scan.save()
                counter += 1 
            except IndexError : 
                return Response({
                    "status_message" : "Students are greater than the number of computers, some students did not get assigned computers"
                })
    
    return Response({
        "status_message" : "Computers has been assigned successfully"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unassign_all_computer(request): 
    section_name = request.data.get("section_name")

    if not section_name: 
        return Response({
            "status_message": "Invalid or missing input"
        })
    
    section = Section.objects.filter(name=section_name).first()
    
    if not section: 
        return Response({
            "status_message": "Section not found"
        })

    students = Student.objects.filter(section=section)

    for student in students:
        scan = Scan.objects.filter(student=student).first()
        if scan and scan.computer:
            scan.computer = None
            scan.save()

    return Response({
        "status_message": "All computers have been successfully unassigned for the section."
    })


@api_view(['POST'])
def change_computer_status(request):
    status = request.data.get("status")
    computer_name = request.data.get("computerName")
    mac_address = request.data.get("macAddress")

    print(status)
    print(computer_name)
    print(mac_address)

    if not computer_name or not mac_address or status == None: 
        print("may mali")
        return Response({
            "status" : "Missing or invalid input"
        })
    
    if status != 1 and status != 0: 
        print(2)
        return Response({
            "status" : "Missing or invalid input"
        })

    computer = change_computer_name(computer_name, mac_address)
    computer.status = status
    computer.save()

    return Response({
        "status_message" : "Computer status have been updated successfully"
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_computers(request): 
    computers = request.data.get("computers")
    print(computers)

    if type(computers) != list: 
        return Response({
            "status" : 0,
            "status_message" : "Missing or invalid input"
        })
    
    for computer in computers : 
        computer_object = Computer.objects.filter(computer_name = computer).first()
        
        if computer_object:
            computer_object.delete()
    
    return Response({
        "status" : 1, 
        "status_message" : "Computer successfully deleted" 
    })