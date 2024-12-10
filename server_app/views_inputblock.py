from rest_framework.decorators import api_view
from rest_framework.response import Response
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import Computer
import subprocess

# @api_view(['POST'])
# def block_input(request):
#     computer_list = Computer.objects.filter(is_admin=0)
    
#     # for computer in computer_list:
#     ps_script = f"""
# $username = "Administrator"
# $password = "Admin123"
# $computer = "DESKTOP-HBTUJID"  # Assuming `computer` has a `name` attribute

# $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
# $credential = New-Object System.Management.Automation.PSCredential ($username, $securePassword)
# $session = New-PSSession -ComputerName $computer -Credential $credential

# Invoke-Command -Session $session -ScriptBlock {{
#     Add-Type @"
# using System;
# using System.Runtime.InteropServices;
# public class InputBlocker {{
#     [DllImport("user32.dll", SetLastError = true)]
#     public static extern bool BlockInput(bool fBlockIt);
# }}
# "@

#     [InputBlocker]::BlockInput($true)
    
# }}

# Remove-PSSession -Session $session
# """
#     result = subprocess.run(["powershell.exe", "-Command", ps_script], capture_output=True, text=True)
#     if result.returncode == 0:
#         print(f"Output: {result.stdout}")
#     else:
#         print(f"Error: {result.stderr}")

#     return Response({"status_message": "Input blocking completed"})


# @api_view(['POST'])
# def unblock_input(request):
#     computer_list = Computer.objects.filter(is_admin=0)
    
#     # for computer in computer_list:
#     ps_script = f"""
# $username = "Administrator"
# $password = "Admin123"
# $computer = "DESKTOP-HBTUJID"

# $securePassword = ConvertTo-SecureString $password -AsPlainText -Force
# $credential = New-Object System.Management.Automation.PSCredential ($username, $securePassword)
# $session = New-PSSession -ComputerName $computer -Credential $credential

# Invoke-Command -Session $session -ScriptBlock {{
#     Add-Type @"
# using System;
# using System.Runtime.InteropServices;
# public class InputBlocker {{
#     [DllImport("user32.dll", SetLastError = true)]
#     public static extern bool BlockInput(bool fBlockIt);
# }}
# "@

#     [InputBlocker]::BlockInput($false)
# }}

# Remove-PSSession -Session $session
# """
#     result = subprocess.run(["powershell.exe", "-Command", ps_script], capture_output=True, text=True)
#     if result.returncode == 0:
#             print(f"Output: {result.stdout}")
#     else:
#             print(f"Error: {result.stderr}")

#     return Response({"status_message": "Input unblocking completed"})

def execute_ps_exec_command(command, client_computer_name):
    try:
        # Run the PsExec command
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(f"Sent command to {client_computer_name}")
        print(f"STDOUT: {stdout.decode()}")
        print(f"STDERR: {stderr.decode()}")
    except Exception as e:
        print(f"Failed to send command to {client_computer_name}: {str(e)}")


@api_view(['POST'])
def block_input(request):
    try:
        # Fetch all non-admin computers
        admin_computers = Computer.objects.filter(is_admin=1).values_list('computer_name', flat=True)
        selected_computers = request.data.get('computers', [])
        filtered_computers = [computer for computer in selected_computers if computer not in admin_computers]


        # Create a ThreadPoolExecutor to run commands in parallel
        with ThreadPoolExecutor() as executor:
            futures = []
            for client_computer in filtered_computers:
                # PsExec command to block input on the remote machine
                command = fr'C:\Windows\System32\PSTools\PsExec.exe \\{client_computer} -i 1 -u smartsilid.com\Administrator -p Admin123 powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\script\block2_input.ps1'
                # Submit the command execution to the executor and store the future
                futures.append(executor.submit(execute_ps_exec_command, command, client_computer))

            # Wait for all tasks to complete and collect results
            for future in as_completed(futures):
                future.result()  # This will raise exceptions if there were any errors

        return Response({'status': 'success', 'message': 'Input block commands sent to all non-admin computers.'})

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})


@api_view(['POST'])
def unblock_input(request):
    try:
        # Fetch all non-admin computers
        admin_computers = Computer.objects.filter(is_admin=1).values_list('computer_name', flat=True)
        selected_computers = request.data.get('computers', [])
        filtered_computers = [computer for computer in selected_computers if computer not in admin_computers]

        # Create a ThreadPoolExecutor to run commands in parallel
        with ThreadPoolExecutor() as executor:
            futures = []
            for client_computer in filtered_computers:
                # PsExec command to unblock input on the remote machine
                command = fr'C:\Windows\System32\PSTools\PsExec.exe \\{client_computer} -i 1 -u smartsilid.com\Administrator -p Admin123 powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File C:\script\unblock2_input.ps1'
                # Submit the command execution to the executor and store the future
                futures.append(executor.submit(execute_ps_exec_command, command, client_computer))

            # Wait for all tasks to complete and collect results
            for future in as_completed(futures):
                future.result()  # This will raise exceptions if there were any errors

        return Response({'status': 'success', 'message': 'Input unblock commands sent to all non-admin computers.'})

    except Exception as e:
        return Response({'status': 'error', 'message': str(e)})