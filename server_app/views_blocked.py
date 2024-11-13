from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import BlockedURL
import subprocess
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Function to run the PowerShell script
def run_powershell_script(url_list):
    script = f'''
    Import-Module GroupPolicy

    $GPOName = "block"
    $newURLs = @({", ".join([f'"{url}"' for url in url_list])})

    $gpo = Get-GPO -Name $GPOName -ErrorAction SilentlyContinue
    if (-not $gpo) {{
        $gpo = New-GPO -Name $GPOName
    }}

    # Microsoft Edge URLBlocklist registry path
    $edgeRegistryPath = "HKCU\\Software\\Policies\\Microsoft\\Edge\\URLBlocklist"
    
    # Google Chrome URLBlocklist registry path
    $chromeRegistryPath = "HKCU\\Software\\Policies\\Google\\Chrome\\URLBlocklist"
    
    # Firefox URLBlocklist registry path (if using ADMX template)
    $firefoxRegistryPath = "HKCU\\Software\\Policies\\Mozilla\\Firefox\\WebsiteFilter\\Block"

    # Function to clear and add new URLs for a browser
    function Set-URLBlocklist ($gpoName, $registryPath, $urls) {{
        # Check if registry path exists before removing
        $keyExists = Get-GPRegistryValue -Name $gpoName -Key $registryPath -ErrorAction SilentlyContinue
        if ($keyExists) {{
            Remove-GPRegistryValue -Name $gpoName -Key $registryPath -ErrorAction SilentlyContinue
        }}

        # Add new URLs
        for ($i = 0; $i -lt $urls.Count; $i++) {{
            Set-GPRegistryValue -Name $gpoName -Key $registryPath -ValueName "$i" -Type String -Value $urls[$i] -ErrorAction SilentlyContinue
        }}
    }}

    # Set URL blocklist for Edge
    Set-URLBlocklist -gpoName $GPOName -registryPath $edgeRegistryPath -urls $newURLs
    
    # Set URL blocklist for Chrome
    Set-URLBlocklist -gpoName $GPOName -registryPath $chromeRegistryPath -urls $newURLs

    # Set URL blocklist for Firefox
    Set-URLBlocklist -gpoName $GPOName -registryPath $firefoxRegistryPath -urls $newURLs

    # Suppress any output
    $null = Write-Host "Policy reset to Not Configured and new URLs added." -ErrorAction SilentlyContinue
    
    '''
    process = subprocess.Popen(["powershell", "-Command", script], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.communicate()  # Wait for the script to finish

# View to list, add, and delete URLs
def blocked_url_manage(request):
    if request.method == 'POST':
        # If the form is submitted, add a new URL
        url = request.POST.get('url')
        if url:
            BlockedURL.objects.create(url=url)
    
    # If 'delete' is in the request, delete the selected URL
    if 'delete' in request.GET:
        url_id = request.GET.get('delete')
        try:
            url = BlockedURL.objects.get(id=url_id)
            url.delete()
        except BlockedURL.DoesNotExist:
            pass  # Handle the case where the URL does not exist

    # List all blocked URLs
    urls = BlockedURL.objects.all()

    if 'update_gpo' in request.GET:
        url_list = [url.url for url in urls]
        run_powershell_script(url_list)
        return redirect('manage_blocked_urls')  

    return render(request, 'server_app/manage.html', {'urls': urls})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_url_block(request): 
    url = request.data.get('url')
    print(url)
    try :

        url_object  = BlockedURL.objects.filter(url = url).first()
        if not url_object : 
            new_url = BlockedURL(url = url)
            new_url.save()

        urls = BlockedURL.objects.all()

        url_list = [url.url for url in urls]
        
        print(url_list)
        run_powershell_script(url_list)
            
        return Response({
            "status_message" : "Url has been blocked succesfully"
        })
    
    except Exception as e : 
        return Response({
            "status_message" : "Url addition has been unsuccesful",
            "error" : str(e)
        })

    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_url_block(request): 

    
    response_json = []

    urls = BlockedURL.objects.all()

    for url in urls : 
        response_json.append(url.url)
    
    return Response({
        "status_message" : "Url request succesful",
        "url" : response_json

    })


@api_view(['POST'])        
@permission_classes([IsAuthenticated])
def delete_url_block(request): 
    url = request.data.get('url')

    try :
        url_object = BlockedURL.objects.filter(url = url).first()
        url_object.delete()

        urls = BlockedURL.objects.all()

        run_powershell_script([url.url for url in urls])
        
        return Response({
            "status_message" : "Url has been removed from the list"
        })

    except Exception as e: 
        return Response({
            "status_message" : "Url delete has been unsuccesful",
            "error" : str(e)
        })
    
    


        

    

    


