from rest_framework.decorators import api_view
from rest_framework.response import Response
import subprocess

@api_view
def block_input(request):

    computer_list = [request.data.get("computer_name")]
    
    for computer in computer_list : 
        ps_script = f"""
        
        $username = "Administrator"
        $password = "Admin123"
        $computer = {computer}

        $securePassword = ConvertTo-SecureString $password -AsPlainText -Force

        $credential = New-Object System.Management.Automation.PSCredential ($username, $securePassword)

        $session = New-PSSession -ComputerName $computer -Credential $credential

        Invoke-Command -Session $session -ScriptBlock {{
            Write-Host 
        }}

        Remove-PSSession -Session $session
        """

        result = subprocess.run(["powershell.exe", "-Command", ps_script],capture_output=True, text=True)

        # Return the output and error
        if result.returncode == 0:
            print(f"Output: {result.stdout}")
        else:
            print(f"Error: {result.stderr}")

    return Response({"status_message" : "Input blocking completed"})
