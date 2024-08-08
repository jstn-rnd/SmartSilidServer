import win32com.client
import pythoncom
import logging
from django.shortcuts import render, redirect
from .models import Whitelist, Blacklist

# Set up logging
logging.basicConfig(filename='gpo_update.log', level=logging.DEBUG)

def update_gpo():
    """
    Updates the Group Policy Object (GPO) with the current blacklist URLs.
    
    Handles initialization and cleanup of COM for thread safety.

    Raises an exception if any error occurs during the update process.
    """
    try:
        pythoncom.CoInitialize()  # Initialize COM for thread safety

        # Connect to the GPO management COM object
        gpo_management = win32com.client.Dispatch("SomeOther.GPOManagement")  # Replace with correct COM object

        # Retrieve the specified GPO by its GUID
        gpo_guid = "53582B9C-5D78-40F2-8B14-223EECEAD27B"  # Replace with your GPO GUID
        gpo = gpo_management.GetGPO(gpo_guid)  # Ensure this method exists or use the correct method
        
        # Access the policy settings (modify as needed based on the actual COM object's API)
        policy = gpo.GetSettings()
        edge_policy = policy.AdministrativeTemplates.MicrosoftEdge

        # Fetch current blacklist data
        blacklist = Blacklist.objects.values_list('url', flat=True)

        # Update the policy to block URLs
        edge_policy.BlockAccessToListOfURLs = blacklist
        
        # Save the changes
        gpo.Save()

        print("GPO updated successfully.")

    except Exception as e:
        logging.error(f"An error occurred while updating GPO: {e}", exc_info=True)
        raise Exception(f"An error occurred while updating GPO: {e}")

    finally:
        pythoncom.CoUninitialize()  # Cleanup COM

def whitelist_view(request):
    """
    Handles adding and removing URLs from the whitelist.

    Updates the GPO with the modified whitelist after each change.
    """
    if request.method == 'POST':
        if 'add' in request.POST:
            url = request.POST.get('url')
            if url:
                Whitelist.objects.get_or_create(url=url)
                update_gpo()
        elif 'remove' in request.POST:
            url = request.POST.get('url')
            if url:
                Whitelist.objects.filter(url=url).delete()
                update_gpo()
        return redirect('whitelist')

    whitelist = Whitelist.objects.all()
    return render(request, 'server_app/whitelist.html', {'whitelist': whitelist})

def blacklist_view(request):
    """
    Handles adding and removing URLs from the blacklist.

    Updates the GPO with the modified blacklist after each change.
    """
    if request.method == 'POST':
        if 'add' in request.POST:
            url = request.POST.get('url')
            if url:
                Blacklist.objects.get_or_create(url=url)
                update_gpo()
        elif 'remove' in request.POST:
            url = request.POST.get('url')
            if url:
                Blacklist.objects.filter(url=url).delete()
                update_gpo()
        return redirect('blacklist')

    blacklist = Blacklist.objects.all()
    return render(request, 'server_app/blacklist.html', {'blacklist': blacklist})
