import subprocess
from django.http import HttpResponse
from wakeonlan import send_magic_packet
from django.shortcuts import render
from .models import Computer

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

def select_and_wake_computers(request):
    if request.method == 'POST':
        selected_computers = request.POST.getlist('computers')
        
        if len(selected_computers) < 1:
            return HttpResponse("Please select at least 1 computer.", status=400)
        
        try:
            for computer in selected_computers:
                student_mac = Computer.objects.filter(computer_name=computer).first()
                if student_mac:
                    normalized_mac = normalize_mac(student_mac.mac_address)
                    send_magic_packet(normalized_mac)
            return HttpResponse(f"Sent magic packets to: {', '.join(selected_computers)}")
        except Exception as e:
            return HttpResponse(f"Failed to send magic packets: {str(e)}", status=500)

    return render(request, 'server_app/select_and_wake.html', {'computers': Computer.objects.values_list('computer_name', flat=True)})

def shutdown_computers(request):
    if request.method == 'POST':
        computers = request.POST.getlist('computers')
        if not computers:
            return HttpResponse("No computers selected.", status=400)
        
        failed_computers = []
        
        for computer in computers:
            student_mac = Computer.objects.filter(computer_name=computer).first()
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
            return HttpResponse(f"Some shutdown commands failed:\n{error_messages}", status=500)
        
        return HttpResponse("Shutdown commands sent successfully.")
    
    return render(request, 'server_app/shutdown_computers.html', {'computers': Computer.objects.values_list('computer_name', flat=True)})
